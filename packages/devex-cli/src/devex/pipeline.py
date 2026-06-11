"""Local pipeline simulation for `devex pipeline run --local` (shift-left, bonus).

Reproduces the PR pipeline's `small-tests` stage on the workstation so failures
surface before push, not in CI. The convention gate is run via the shared
validators; the language test command mirrors @keystone/platform's
`workflows/toolchains.ts` — the accepted cross-language duplication per
docs/engineering-rules/dry-principles.md (the new-language runbook updates both sides).
"""

from __future__ import annotations

import json
from pathlib import Path

from devex._log import log

#: Per-language small-tests command (mirrors the framework toolchains).
#: python uses --no-project so the command works for uv-native AND pip-venv
#: services alike, exactly like the generated CI step (FIN-309).
LOCAL_TEST_COMMANDS: dict[str, list[str]] = {
    "python": ["uv", "run", "--no-project", "pytest", "-q"],
    "typescript": ["pnpm", "test"],
    "go": ["go", "test", "./..."],
    "clojure": ["lein", "test"],
}

DEFAULT_LANGUAGE = "python"


def detect_language(root: Path, default: str = DEFAULT_LANGUAGE) -> str:
    """Read the service language from keystone.json, falling back to `default`."""
    config = root / "keystone.json"
    if not config.exists():
        return default
    try:
        return str(json.loads(config.read_text(encoding="utf-8")).get("language", default))
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("keystone_json.unreadable", path=config, error=exc)
        return default


def language_test_command(language: str) -> list[str] | None:
    """The local small-tests command for a language, or None if unsupported."""
    return LOCAL_TEST_COMMANDS.get(language)


def local_setup_commands(language: str, root: Path) -> list[list[str]]:
    """Dependency-install commands mirroring the CI toolchain's setup stage.

    The simulation must provision the SAME environment the generated job does —
    otherwise a stale local venv can pass what a fresh CI sync would fail (the
    exact "passes locally, fails CI" drift this command exists to prevent).
    Language runtimes (Node, Go, JVM) are the workstation's responsibility;
    only project dependencies are mirrored here.
    """
    if language == "python":
        if (root / "pyproject.toml").exists():
            return [["uv", "sync", "--extra", "dev"]]
        commands = [["uv", "venv"]]
        commands += [
            ["uv", "pip", "install", "-r", req]
            for req in ("requirements.txt", "requirements-dev.txt")
            if (root / req).exists()
        ]
        return commands
    if language == "typescript":
        return [["pnpm", "install", "--frozen-lockfile"]]
    if language == "go":
        return [["go", "mod", "download"]]
    return []
