"""Unit + property-based tests for the convention validators.

Satisfies deliverable C (CLI test) and demonstrates the PR pipeline's
Property-Based Testing stage: we assert a property over generated inputs,
not just hand-picked examples.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from devex.validators import validate_branch, validate_commit, validate_pr_title


# ── Example-based (unit) ──────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "branch,expected",
    [
        ("feature/FIN-123-add-payment-validation", True),
        ("fix/TX-19-retry-timeout", True),
        ("main", True),  # protected branch is skipped, not failed
        ("feature/no-work-id", False),
        ("FIN-123-missing-type", False),
        ("Feature/FIN-123-Bad-Case", False),
    ],
)
def test_validate_branch(branch: str, expected: bool) -> None:
    assert validate_branch(branch).ok is expected


def test_validate_commit_requires_work_id() -> None:
    assert validate_commit("feat(api): FIN-123 add payment validation").ok is True
    assert validate_commit("feat: add payment validation").ok is False


def test_validate_pr_title() -> None:
    # A PR title is the squash-merge commit subject, so it follows the commit shape:
    # <type>(<scope>)?: <WORK-ID> <subject>.
    assert validate_pr_title("feat(api): FIN-123 add payment validation").ok is True
    assert validate_pr_title("fix: TX-19 retry on gateway timeout").ok is True
    assert validate_pr_title("FIN-123: add payment validation").ok is False  # no conventional-commit type
    assert validate_pr_title("feat: add payment validation").ok is False  # no Work ID
    assert validate_pr_title("Add payment validation").ok is False


# ── Property-based (PBT) ──────────────────────────────────────────────────────
work_ids = st.from_regex(r"[A-Z]{2,5}-[0-9]{1,6}", fullmatch=True)
slugs = st.from_regex(r"[a-z0-9]+(-[a-z0-9]+)*", fullmatch=True)


@given(work_id=work_ids, slug=slugs)
def test_any_wellformed_branch_passes(work_id: str, slug: str) -> None:
    """Property: a branch built from a valid type + Work ID + slug always validates."""
    assert validate_branch(f"feature/{work_id}-{slug}").ok is True


@given(subject=st.from_regex(r"(feat|fix|chore): [a-z ]{3,40}", fullmatch=True))
def test_commit_without_work_id_always_fails(subject: str) -> None:
    """Property: a conventional-commit subject with no Work ID never passes."""
    assert validate_commit(subject).ok is False


commit_types = st.sampled_from(["feat", "fix", "chore", "docs", "refactor", "test", "ci", "perf", "build"])


@given(type_=commit_types, work_id=work_ids, subject=st.from_regex(r"[a-z]+( [a-z]+){0,4}", fullmatch=True))
def test_any_conventional_pr_title_with_work_id_passes(type_: str, work_id: str, subject: str) -> None:
    """Property: <type>: <WORK-ID> <subject> always validates as a PR title."""
    assert validate_pr_title(f"{type_}: {work_id} {subject}").ok is True


@given(type_=commit_types, subject=st.from_regex(r"[a-z]+( [a-z]+){0,4}", fullmatch=True))
def test_pr_title_without_work_id_always_fails(type_: str, subject: str) -> None:
    """Property: a conventional-commit PR title lacking a Work ID never passes."""
    assert validate_pr_title(f"{type_}: {subject}").ok is False
