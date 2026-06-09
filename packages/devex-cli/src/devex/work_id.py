"""Work ID extraction.

The Work ID pattern is defined once in conventions.json; here we reuse it to
*find* a Work ID inside a branch name or commit subject (the anchored pattern,
un-anchored for searching). Generated CI workflows call `devex workid` to stamp
the Work ID into telemetry — so this keeps that link sourced from conventions,
never a hard-coded regex.
"""

from __future__ import annotations

import re

from devex.conventions import load_conventions


def _search_pattern() -> str:
    """The Work ID pattern with its anchors stripped, for searching within text."""
    pattern = load_conventions()["workId"]["pattern"]
    return pattern.removeprefix("^").removesuffix("$")


def extract_work_id(text: str) -> str | None:
    """Return the first Work ID found in `text`, or None.

    Works on a branch name (`feature/FIN-123-slug`), a commit subject
    (`feat: FIN-123 ...`), or a PR title.
    """
    match = re.search(_search_pattern(), text)
    return match.group(0) if match else None
