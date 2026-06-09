"""devex CLI entrypoint.

Command surface for the Keystone devex CLI. Commands are thin: parse args, call
pure logic (validators / conventions), render via Rich. A group callback
validates conventions.json up-front so every command fails fast on a bad source.
See .kiro/specs/devex-cli/tasks.md for the roadmap.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from devex import __version__, hooks, pipeline, scaffold
from devex._log import log
from devex.conventions import load_conventions
from devex.dora import DEFAULT_ENV, compute_metrics, parse_events
from devex.exit_codes import ExitCode
from devex.schema import ConventionsError
from devex.settings import ci_branch, is_ci_pull_request, telemetry_stream_path
from devex.validators import Result, validate_branch, validate_commit, validate_pr_title
from devex.work_id import extract_work_id

# Ensure UTF-8 output so Rich status glyphs (✓ / ✗) render on legacy Windows
# consoles, where the default cp1252 codec raises UnicodeEncodeError. No-op when
# stdout is already UTF-8 or the stream is not reconfigurable (e.g. test capture).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (ValueError, OSError) as exc:
            log.warning("stdout.reconfigure_failed", error=exc)

app = typer.Typer(help="Keystone devex — the developer interface to the platform.", no_args_is_help=True)
console = Console()


@app.callback()
def _main() -> None:
    """Validate the conventions source up-front; a bad file fails fast (exit CONFIG)."""
    try:
        load_conventions()
    except ConventionsError as exc:
        console.print(f"[red]✗[/] invalid conventions.json: {exc}")
        raise typer.Exit(code=ExitCode.CONFIG) from None


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout.strip()


def _resolve_branch() -> str:
    """Branch to validate: CI context first (PR source / pushed ref), else local git.

    On a `pull_request` the checkout is a detached merge ref, so the local branch
    name is "HEAD"; GITHUB_HEAD_REF carries the real source branch.
    """
    return ci_branch() or _git("rev-parse", "--abbrev-ref", "HEAD") or "HEAD"


@app.command()
def version() -> None:
    """Print the CLI version."""
    console.print(f"devex {__version__}")


def _standards_results() -> list[Result]:
    """Validate the current branch + last commit against conventions.json (CI-aware)."""
    results = [validate_branch(_resolve_branch())]
    if is_ci_pull_request():
        # A pull_request checkout is a synthetic, shallow merge ref: the real
        # change commit isn't reachable (git sees the merge as parentless), so
        # validating it would fail on the merge subject. The branch carries the
        # Work ID; the local commit-msg hook validates commits at write time.
        results.append(Result(True, "commit check skipped (pull_request checkout)"))
    else:
        results.append(validate_commit(_git("log", "-1", "--pretty=%s")))
    return results


@app.command(name="standards-check")
def standards_check() -> None:
    """Validate the current branch and last commit against conventions.json (shift-left)."""
    results = _standards_results()
    for r in results:
        console.print(("[green]✓[/] " if r.ok else "[red]✗[/] ") + r.message)
    if not all(r.ok for r in results):
        raise typer.Exit(code=ExitCode.VALIDATION)


@app.command(name="check-pr-title")
def check_pr_title(title: str = typer.Argument(..., help="The pull-request title to validate.")) -> None:
    """Validate a PR title against conventions.json (conventional-commit type + Work ID).

    Used by CI (.github/workflows/pr-title.yml) so the PR-title rule comes from the
    single source of truth — the same conventions the developer validates locally.
    """
    r = validate_pr_title(title)
    console.print(("[green]✓[/] " if r.ok else "[red]✗[/] ") + r.message)
    if not r.ok:
        raise typer.Exit(code=ExitCode.VALIDATION)


def _generate_workflows(target: Path) -> bool:
    """Best-effort: run the @keystone/platform generator if node + the framework are available."""
    try:
        proc = subprocess.run(
            ["node", "scripts/generate-workflows.mjs"],
            cwd=target,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (FileNotFoundError, OSError, subprocess.SubprocessError) as exc:
        log.warning("workflows.generate_skipped", error=exc)
        return False
    return proc.returncode == 0


def _report_scaffold(result: scaffold.ScaffoldResult, target: Path) -> None:
    for path in result.created:
        console.print(f"[green]+[/] {path}")
    for path in result.skipped:
        console.print(f"[yellow]·[/] kept existing {path}")
    if _generate_workflows(target):
        console.print("[green]✓[/] generated CI workflows via @keystone/platform")
    else:
        console.print("[yellow]ℹ[/] run 'pnpm install && pnpm generate:workflows' to emit the CI workflows")


def _require_language(language: str) -> None:
    if language not in scaffold.LANGUAGES:
        console.print(f"[red]✗[/] unknown language '{language}' (expected: {', '.join(scaffold.LANGUAGES)})")
        raise typer.Exit(code=ExitCode.CONFIG)


@app.command()
def init(
    service: str = typer.Argument(..., help="Service name (lowercase kebab)."),
    language: str = typer.Option("python", "--language", help="App language: python|go|clojure|typescript."),
    here: bool = typer.Option(False, "--here", help="Scaffold into the current directory instead of ./<service>."),
) -> None:
    """Bootstrap a new service onto the golden path (skeleton + PR template + CI workflows)."""
    _require_language(language)
    if not scaffold.is_valid_service_name(service):
        console.print(f"[red]✗[/] invalid service name '{service}' (expected lowercase kebab, e.g. 'transactionify')")
        raise typer.Exit(code=ExitCode.CONFIG)
    target = Path.cwd() if here else Path(service)
    result = scaffold.scaffold_service(target, service, language, overwrite=False)
    _report_scaffold(result, target)
    console.print(f"\n[bold]Service '{service}' is on the golden path.[/]")


@app.command()
def adopt(
    language: str = typer.Option("python", "--language", help="App language: python|go|clojure|typescript."),
) -> None:
    """Add Keystone artifacts to the EXISTING repo in the current directory (never overwrites app code)."""
    _require_language(language)
    target = Path.cwd()
    service = target.name
    result = scaffold.scaffold_service(target, service, language, overwrite=False)
    _report_scaffold(result, target)
    console.print(f"\n[bold]'{service}' adopted the golden path.[/] Existing files were kept.")


@app.command()
def pr(
    draft: bool = typer.Option(False, "--draft", help="Open the PR as a draft."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print what would happen without calling gh."),
) -> None:
    """Open a PR via gh: the title comes from your last commit (Work ID enforced) + the standard template."""
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch in load_conventions()["branch"].get("protected", []):
        console.print(f"[red]✗[/] '{branch}' is a protected branch — create a feature branch first")
        raise typer.Exit(code=ExitCode.CONFIG)
    title = _git("log", "-1", "--pretty=%s")
    result = validate_pr_title(title)
    if not result.ok:
        console.print("[red]✗[/] " + result.message)
        console.print("The PR title is taken from your last commit — make it '<type>(<scope>): WORK-ID subject'.")
        raise typer.Exit(code=ExitCode.VALIDATION)
    if dry_run:
        console.print(f"[green]✓[/] would open PR [bold]{title}[/] from branch '{branch}'")
        return
    cmd = ["gh", "pr", "create", "--title", title, "--body", scaffold.pr_template()]
    if draft:
        cmd.append("--draft")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, OSError, subprocess.SubprocessError) as exc:
        console.print(f"[red]✗[/] could not run gh: {exc}")
        raise typer.Exit(code=ExitCode.CONFIG) from None
    if proc.returncode != 0:
        console.print(f"[red]✗[/] gh pr create failed: {proc.stderr.strip()}")
        raise typer.Exit(code=ExitCode.CONFIG)
    console.print(proc.stdout.strip())


hooks_app = typer.Typer(help="Manage git hooks (shift-left validation).", no_args_is_help=True)
app.add_typer(hooks_app, name="hooks")


@hooks_app.command("install")
def hooks_install(
    force: bool = typer.Option(False, "--force", help="Replace pre-existing non-Keystone hooks."),
) -> None:
    """Install pre-commit + pre-push hooks that run `devex standards-check`."""
    hooks_path = _git("rev-parse", "--git-path", "hooks")
    if not hooks_path:
        console.print("[red]✗[/] not a git repository")
        raise typer.Exit(code=ExitCode.CONFIG)
    installed, skipped = hooks.install_hooks(Path(hooks_path), force=force)
    for path in installed:
        console.print(f"[green]+[/] installed {path}")
    for path in skipped:
        console.print(f"[yellow]·[/] kept existing {path} (use --force to replace)")


pipeline_app = typer.Typer(help="Run pipeline stages locally.", no_args_is_help=True)
app.add_typer(pipeline_app, name="pipeline")


@pipeline_app.command("run")
def pipeline_run(
    local: bool = typer.Option(True, "--local/--no-local", help="Run the small-tests stage locally."),
    dry_run: bool = typer.Option(False, "--dry-run", help="List the stages without running the tests."),
) -> None:
    """Simulate the PR pipeline's small-tests stage locally (shift-left)."""
    if not local:
        console.print("[yellow]ℹ[/] only --local is supported in the PoC")
        raise typer.Exit(code=ExitCode.CONFIG)
    language = pipeline.detect_language(Path.cwd())
    command = pipeline.language_test_command(language)
    console.print(f"[bold]pipeline run --local[/] (language: {language})")

    # Stage 1 — conventions gate.
    results = _standards_results()
    for r in results:
        console.print(("  [green]✓[/] " if r.ok else "  [red]✗[/] ") + r.message)
    gate_ok = all(r.ok for r in results)

    # Stage 2 — dependency setup, mirroring the CI toolchain's setup step. Without
    # it a stale local venv could pass what a fresh CI sync would fail.
    setup_ok = True
    for setup_command in pipeline.local_setup_commands(language, Path.cwd()):
        console.print(f"  setup: {' '.join(setup_command)}")
        if dry_run:
            continue
        try:
            if subprocess.run(setup_command, timeout=600).returncode != 0:
                console.print("  [red]✗[/] dependency setup failed")
                setup_ok = False
                break
        except (FileNotFoundError, OSError, subprocess.SubprocessError) as exc:
            console.print(f"  [red]✗[/] could not run setup: {exc}")
            raise typer.Exit(code=ExitCode.CONFIG) from None

    # Stage 3 — small-tests.
    if command is None:
        console.print(f"  [yellow]·[/] no local test command mapped for '{language}'")
    else:
        console.print(f"  small-tests: {' '.join(command)}")
    if not dry_run and command is not None and setup_ok:
        try:
            tests_ok = subprocess.run(command, timeout=600).returncode == 0
        except (FileNotFoundError, OSError, subprocess.SubprocessError) as exc:
            console.print(f"  [red]✗[/] could not run tests: {exc}")
            raise typer.Exit(code=ExitCode.CONFIG) from None
    else:
        tests_ok = True

    if not gate_ok or not setup_ok or not tests_ok:
        raise typer.Exit(code=ExitCode.VALIDATION)


@app.command()
def workid(
    ref: Optional[str] = typer.Option(
        None, "--ref", help="Text to extract the Work ID from; defaults to the branch, then the last commit."
    ),
) -> None:
    """Print the Work ID for the current change (generated CI uses it to stamp telemetry)."""
    candidates = [ref] if ref else [_resolve_branch(), _git("log", "-1", "--pretty=%s")]
    for text in candidates:
        work_id = extract_work_id(text or "")
        if work_id:
            console.print(work_id, markup=False, highlight=False)  # plain, capturable output
            return
    Console(stderr=True).print("[red]✗[/] no Work ID found in branch name or last commit")
    raise typer.Exit(code=ExitCode.VALIDATION)


def _fmt_duration(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    total = int(seconds)
    if total < 60:
        return f"{total}s"
    if total < 3600:
        return f"{total // 60}m"
    if total < 86400:
        return f"{total // 3600}h {(total % 3600) // 60}m"
    return f"{total // 86400}d {(total % 86400) // 3600}h"


@app.command()
def dora(
    stream: Optional[Path] = typer.Option(
        None, "--stream", help="NDJSON DoraEvent stream; defaults to $KEYSTONE_TELEMETRY_STREAM, else stdin."
    ),
    env: str = typer.Option(DEFAULT_ENV, "--env", help="Environment to report on."),
) -> None:
    """Compute the four DORA metrics from the telemetry event stream."""
    source = stream or telemetry_stream_path()
    lines = source.read_text("utf-8").splitlines() if source is not None else sys.stdin.read().splitlines()
    events, skipped = parse_events(lines)
    metrics = compute_metrics(events, env=env)

    table = Table(title=f"DORA metrics — {env}")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Deployment frequency", f"{metrics.deployment_frequency} deploy(s)")
    table.add_row("Lead time for changes (median)", _fmt_duration(metrics.lead_time_seconds))
    table.add_row("Change failure rate", f"{metrics.change_failure_rate * 100:.1f}%")
    table.add_row("Mean time to restore (MTTR)", _fmt_duration(metrics.mttr_seconds))
    console.print(table)
    if skipped:
        console.print(f"[yellow]skipped {skipped} malformed line(s)[/]")


if __name__ == "__main__":
    app()
