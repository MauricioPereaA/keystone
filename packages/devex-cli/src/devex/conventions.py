"""Loader for the canonical conventions.

Reads the bundled conventions.json (package data) so the installed CLI is
self-contained. This is the SAME file the TypeScript framework consumes to
generate CI workflows — local validation and CI enforcement share one source
of truth. See ADR-0001.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any


@lru_cache(maxsize=1)
def load_conventions() -> dict[str, Any]:
    """Return the parsed conventions.json bundled with the package."""
    data = resources.files("devex._data").joinpath("conventions.json").read_text("utf-8")
    return json.loads(data)
