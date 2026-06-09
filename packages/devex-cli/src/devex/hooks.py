"""Native git hooks installer for `devex hooks install` (shift-left, bonus B).

Writes plain git hooks (no pre-commit-framework dependency) that run
`devex standards-check`, so non-conforming work is caught before it leaves the
workstation. Pure file logic — the CLI resolves the hooks directory via git.
"""

from __future__ import annotations

from pathlib import Path

KEYSTONE_MARKER = "Keystone shift-left hook"
HOOK_NAMES = ("pre-commit", "pre-push")


def _hook_script(name: str) -> str:
    return (
        "#!/usr/bin/env sh\n"
        f"# {KEYSTONE_MARKER} ({name}) — installed by `devex hooks install`.\n"
        "# Validates the branch + latest commit against conventions.json before code\n"
        "# leaves your machine. Edit the convention, not this hook.\n"
        "exec devex standards-check\n"
    )


def install_hooks(hooks_dir: Path, *, force: bool = False) -> tuple[list[Path], list[Path]]:
    """Install the pre-commit/pre-push hooks.

    A pre-existing hook that we did not write is skipped (unless `force`), so we
    never silently clobber a contributor's own hook or the pre-commit framework's.
    """
    installed: list[Path] = []
    skipped: list[Path] = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    for name in HOOK_NAMES:
        path = hooks_dir / name
        if path.exists() and not force and KEYSTONE_MARKER not in path.read_text(encoding="utf-8", errors="ignore"):
            skipped.append(path)
            continue
        path.write_text(_hook_script(name), encoding="utf-8")
        path.chmod(0o755)  # no-op on Windows; required on Linux/macOS
        installed.append(path)
    return installed, skipped
