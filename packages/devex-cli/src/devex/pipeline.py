"""Local pipeline simulation for `devex pipeline run --local` (shift-left, bonus).

Reproduces the PR pipeline's `small-tests` stage on the workstation so failures
surface before push, not in CI. The convention gate is run via the shared
validators; the language test command mirrors @keystone/platform's
`workflows/toolchains.ts` — the accepted cross-language duplication per
.claude/rules/dry-principles.md (the `/new-language` skill updates both sides).
"""

from __future__ import annotations

import json
from pathlib import Path

#: Per-language small-tests command (mirrors the framework toolchains).
LOCAL_TEST_COMMANDS: dict[str, list[str]] = {
    "python": ["uv", "run", "pytest", "-q"],
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
    except (json.JSONDecodeError, OSError):
        return default


def language_test_command(language: str) -> list[str] | None:
    """The local small-tests command for a language, or None if unsupported."""
    return LOCAL_TEST_COMMANDS.get(language)
