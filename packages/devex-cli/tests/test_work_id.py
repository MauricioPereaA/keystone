"""Tests for Work ID extraction (sourced from conventions.json)."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from devex.work_id import extract_work_id


@pytest.mark.parametrize(
    "text,expected",
    [
        ("feature/FIN-123-add-payment", "FIN-123"),
        ("feat(api): FIN-123 add payment validation", "FIN-123"),
        ("fix: TX-19 retry on gateway timeout", "TX-19"),
        ("no work id here", None),
        ("lowercase-fin-1", None),
        ("HEAD", None),
    ],
)
def test_extract_work_id(text: str, expected: str | None) -> None:
    assert extract_work_id(text) == expected


work_ids = st.from_regex(r"[A-Z]{2,5}-[0-9]{1,6}", fullmatch=True)
slugs = st.from_regex(r"[a-z]+(-[a-z]+)*", fullmatch=True)


@given(work_id=work_ids, slug=slugs)
def test_extracts_work_id_from_any_wellformed_branch(work_id: str, slug: str) -> None:
    """Property: the Work ID is recovered from a well-formed branch name."""
    assert extract_work_id(f"feature/{work_id}-{slug}") == work_id
