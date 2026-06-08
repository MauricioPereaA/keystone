"""Convention validators.

Pure functions that check a branch name, commit message, or PR title against
the patterns in conventions.json. No I/O, no side effects — trivially testable
and reused by both the CLI commands and the git hooks.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from devex.conventions import load_conventions


@dataclass(frozen=True)
class Result:
    ok: bool
    message: str


def _check(value: str, pattern: str, label: str, example: str) -> Result:
    if re.match(pattern, value):
        return Result(True, f"{label} OK")
    return Result(False, f"{label} invalid: '{value}'. Expected e.g. '{example}'")


def validate_branch(name: str) -> Result:
    c = load_conventions()["branch"]
    if name in c.get("protected", []):
        return Result(True, f"branch '{name}' is protected (skipped)")
    return _check(name, c["pattern"], "branch", c["examples"][0])


def validate_commit(message: str) -> Result:
    c = load_conventions()["commit"]
    return _check(message.splitlines()[0] if message else "", c["pattern"], "commit", c["examples"][0])


def validate_pr_title(title: str) -> Result:
    c = load_conventions()["pullRequest"]
    return _check(title, c["titlePattern"], "PR title", c["examples"][0])
