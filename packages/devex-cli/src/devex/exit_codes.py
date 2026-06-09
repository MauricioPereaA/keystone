"""CLI exit codes — the contract hooks and CI depend on.

Defined once (no magic numbers; see .claude/rules/magic-values.md §3 and
error-handling.md §CLI 5): 0 pass, 1 validation failure, 2 usage/config error.
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    OK = 0
    VALIDATION = 1
    CONFIG = 2
