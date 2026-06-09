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

from devex import __version__
from devex.conventions import load_conventions
from devex.dora import DEFAULT_ENV, compute_metrics, parse_events
from devex.exit_codes import ExitCode
from devex.schema import ConventionsError
from devex.settings import telemetry_stream_path
from devex.validators import validate_branch, validate_commit, validate_pr_title
from devex.work_id import extract_work_id

# Ensure UTF-8 output so Rich status glyphs (✓ / ✗) render on legacy Windows
# consoles, where the default cp1252 codec raises UnicodeEncodeError. No-op when
# stdout is already UTF-8 or the stream is not reconfigurable (e.g. test capture).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (ValueError, OSError):
            pass

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


@app.command()
def version() -> None:
    """Print the CLI version."""
    console.print(f"devex {__version__}")


@app.command(name="standards-check")
def standards_check() -> None:
    """Validate the current branch and last commit against conventions.json (shift-left)."""
    checks = [
        validate_branch(_git("rev-parse", "--abbrev-ref", "HEAD") or "HEAD"),
        validate_commit(_git("log", "-1", "--pretty=%s") or ""),
    ]
    for r in checks:
        console.print(("[green]✓[/] " if r.ok else "[red]✗[/] ") + r.message)
    if not all(r.ok for r in checks):
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


@app.command()
def init(name: str = typer.Argument(..., help="Service name")) -> None:
    """Bootstrap a new service onto the golden path. TODO: scaffold from template."""
    console.print(f"[yellow]TODO[/] init '{name}' — see .kiro/specs/devex-cli/tasks.md")


@app.command()
def workid(
    ref: Optional[str] = typer.Option(
        None, "--ref", help="Text to extract the Work ID from; defaults to the branch, then the last commit."
    ),
) -> None:
    """Print the Work ID for the current change (generated CI uses it to stamp telemetry)."""
    candidates = [ref] if ref else [_git("rev-parse", "--abbrev-ref", "HEAD"), _git("log", "-1", "--pretty=%s")]
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
