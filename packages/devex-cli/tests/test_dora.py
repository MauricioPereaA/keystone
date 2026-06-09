"""Tests for DORA metric computation (the four metrics from one event stream)."""

import json
from datetime import datetime, timedelta, timezone

from hypothesis import given
from hypothesis import strategies as st

from devex.conventions import load_conventions
from devex.dora import (
    EVENT_FAILED,
    EVENT_ROLLED_BACK,
    EVENT_STARTED,
    EVENT_SUCCEEDED,
    DoraEvent,
    compute_metrics,
    parse_events,
)

UTC = timezone.utc
T0 = datetime(2026, 6, 8, 12, 0, tzinfo=UTC)


def _ev(event: str, *, env: str = "production", repo: str = "svc", lead_h: float = 1.0, at: datetime = T0) -> DoraEvent:
    return DoraEvent(event=event, work_id="FIN-1", repo=repo, env=env, commit_time=at - timedelta(hours=lead_h), timestamp=at)


def test_event_constants_are_a_subset_of_conventions() -> None:
    """Guard: the dora event vocabulary stays in sync with conventions.json telemetry.events."""
    allowed = set(load_conventions()["telemetry"]["events"])
    assert {EVENT_STARTED, EVENT_SUCCEEDED, EVENT_FAILED, EVENT_ROLLED_BACK} <= allowed


def test_deployment_frequency_counts_prod_successes_only() -> None:
    events = [_ev(EVENT_SUCCEEDED), _ev(EVENT_SUCCEEDED), _ev(EVENT_SUCCEEDED, env="staging"), _ev(EVENT_FAILED)]
    assert compute_metrics(events).deployment_frequency == 2


def test_change_failure_rate() -> None:
    events = [_ev(EVENT_SUCCEEDED), _ev(EVENT_SUCCEEDED), _ev(EVENT_FAILED), _ev(EVENT_ROLLED_BACK)]
    metrics = compute_metrics(events)
    assert metrics.total_deploys == 4
    assert metrics.change_failure_rate == 0.5


def test_lead_time_is_the_median_commit_to_deploy() -> None:
    events = [_ev(EVENT_SUCCEEDED, lead_h=2), _ev(EVENT_SUCCEEDED, lead_h=4)]
    assert compute_metrics(events).lead_time_seconds == 3 * 3600  # median(2h, 4h)


def test_mttr_is_failed_to_next_success() -> None:
    events = [
        DoraEvent(EVENT_FAILED, "FIN-1", "svc", "production", T0, T0),
        DoraEvent(EVENT_SUCCEEDED, "FIN-1", "svc", "production", T0, T0 + timedelta(hours=1)),
    ]
    assert compute_metrics(events).mttr_seconds == 3600


def test_empty_stream_is_safe() -> None:
    metrics = compute_metrics([])
    assert metrics.deployment_frequency == 0
    assert metrics.change_failure_rate == 0.0
    assert metrics.lead_time_seconds is None
    assert metrics.mttr_seconds is None


def test_parse_events_skips_malformed_lines() -> None:
    good = json.dumps(
        {
            "event": "deployment.succeeded",
            "workId": "FIN-1",
            "actor": "ci",
            "repo": "svc",
            "env": "production",
            "commitSha": "abc",
            "commitTime": "2026-06-08T10:00:00Z",
            "timestamp": "2026-06-08T12:00:00Z",
        }
    )
    events, skipped = parse_events([good, "", "{ not json", json.dumps({"event": "x"})])
    assert len(events) == 1
    assert skipped == 2  # bad JSON + missing required keys (blank line is ignored, not skipped)


outcome_events = st.sampled_from([EVENT_SUCCEEDED, EVENT_FAILED, EVENT_ROLLED_BACK])


@given(events=st.lists(outcome_events, max_size=20))
def test_change_failure_rate_always_in_unit_interval(events: list[str]) -> None:
    """Property: change failure rate is always a probability in [0, 1]."""
    evs = [DoraEvent(e, "FIN-1", "svc", "production", T0, T0) for e in events]
    assert 0.0 <= compute_metrics(evs).change_failure_rate <= 1.0
