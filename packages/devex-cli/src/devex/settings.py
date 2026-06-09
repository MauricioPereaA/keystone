"""Single configuration entrypoint for the devex CLI.

Per .claude/rules/environment-variables.md, the environment is read in ONE place;
the rest of the code imports typed values from here, never `os.environ` directly.
Keeping the lookups in functions (not module-level constants) makes them testable
— a test can set the env var and call the function without re-importing.
"""

from __future__ import annotations

import os
from pathlib import Path

#: Env var that overrides the conventions source (defaults to the bundled copy).
CONVENTIONS_PATH_ENV = "KEYSTONE_CONVENTIONS_PATH"
#: Env var pointing at the NDJSON telemetry stream that `devex dora` reads.
TELEMETRY_STREAM_ENV = "KEYSTONE_TELEMETRY_STREAM"
#: GitHub Actions context vars. On a pull_request the runner checks out a detached
#: merge ref, so the source branch lives in GITHUB_HEAD_REF; on push it is
#: GITHUB_REF_NAME. Reading them keeps standards-check / workid correct in CI.
CI_HEAD_REF_ENV = "GITHUB_HEAD_REF"
CI_REF_NAME_ENV = "GITHUB_REF_NAME"


def ci_branch() -> str | None:
    """Branch name from the CI context (PR source, then pushed ref), or None locally."""
    return os.environ.get(CI_HEAD_REF_ENV) or os.environ.get(CI_REF_NAME_ENV) or None


def is_ci_pull_request() -> bool:
    """True when running on a GitHub `pull_request` event.

    GITHUB_HEAD_REF is set only for pull_request events; the runner then checks
    out a synthetic, shallow merge ref where the real change commit isn't
    reliably reachable (its parents are grafted away). Callers skip commit-message
    validation there — the branch carries the Work ID.
    """
    return bool(os.environ.get(CI_HEAD_REF_ENV))


def conventions_path() -> Path | None:
    """Return the conventions.json override path, or None to use the bundled copy.

    The installed CLI is self-contained (ADR-0001) and ships a bundled conventions
    copy; this override exists for local development against the canonical file.
    """
    raw = os.environ.get(CONVENTIONS_PATH_ENV)
    return Path(raw) if raw else None


def telemetry_stream_path() -> Path | None:
    """Return the path to the NDJSON DoraEvent stream, or None if unset."""
    raw = os.environ.get(TELEMETRY_STREAM_ENV)
    return Path(raw) if raw else None
