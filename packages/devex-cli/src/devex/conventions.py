"""Loader for the canonical conventions.

Reads the bundled conventions.json (package data) so the installed CLI is
self-contained (ADR-0001) — or the KEYSTONE_CONVENTIONS_PATH override for local
development against the canonical file. This is the SAME contract the TypeScript
framework consumes to generate CI workflows: local validation and CI enforcement
share one source of truth.

The source is validated against the Pydantic schema on load; a missing,
unparseable, or schema-invalid file is a hard ConventionsError, never a silent
fallback (security.md §6, error-handling.md §CLI 3).
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

from devex.schema import ConventionsError, validate_conventions
from devex.settings import conventions_path


def _read_source() -> str:
    override = conventions_path()
    if override is not None:
        try:
            return override.read_text("utf-8")
        except FileNotFoundError as exc:
            raise ConventionsError(f"conventions file not found: {override}") from exc
    return resources.files("devex._data").joinpath("conventions.json").read_text("utf-8")


@lru_cache(maxsize=1)
def load_conventions() -> dict[str, Any]:
    """Return the parsed, schema-validated conventions as a dict (cached).

    Tests that change KEYSTONE_CONVENTIONS_PATH must call
    ``load_conventions.cache_clear()`` to pick up the new source.
    """
    try:
        data = json.loads(_read_source())
    except json.JSONDecodeError as exc:
        raise ConventionsError(f"conventions file is not valid JSON: {exc!s}") from exc
    validate_conventions(data)  # raises ConventionsError on any schema violation
    return data
