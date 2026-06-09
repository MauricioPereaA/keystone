"""devex CLI entrypoint.

Command surface for the Keystone devex CLI. Commands are thin: parse args, call
pure logic (validators / conventions), render via Rich. A group callback
validates conventions.json up-front so every command fails fast on a bad source.
See .kiro/specs/devex-cli/tasks.md for the roadmap.
"""

from __future__ import annotations

import subprocess
import sys

import typer
from rich.console import Console

from devex import __version__
from devex.conventions import load_conventions
from devex.exit_codes import ExitCode
from devex.schema import ConventionsError
from devex.validators import validate_branch, validate_commit, validate_pr_title

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
def dora() -> None:
    """Read the telemetry event stream and report the four DORA metrics. TODO."""
    console.print("[yellow]TODO[/] dora report — see .kiro/specs/devex-cli/tasks.md")


if __name__ == "__main__":
    app()
