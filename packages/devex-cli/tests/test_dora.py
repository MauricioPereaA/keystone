"""Tests for DORA metric computation (the four metrics from one event stream)."""

import json
from datetime import datetime, timedelta, timezone

from hypothesis import given
from hypothesis import strategies as st

from devex.conventions import load_conventions
from devex.dora import (
    DEFAULT_ENV,
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


def test_event_constants_match_conventions_exactly() -> None:
    """Guard: the dora event vocabulary stays IN PARITY with conventions.json telemetry.events.

    Set-equality (not subset) so an event ADDED to the source surfaces as a CI failure,
    not a silently-unrecognized event.
    """
    allowed = set(load_conventions()["telemetry"]["events"])
    assert {EVENT_STARTED, EVENT_SUCCEEDED, EVENT_FAILED, EVENT_ROLLED_BACK} == allowed


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


def test_naive_and_aware_timestamps_do_not_crash() -> None:
    """A line mixing a naive commitTime with an aware timestamp is normalized to UTC, not fatal."""
    line = json.dumps(
        {
            "event": "deployment.succeeded",
            "workId": "FIN-1",
            "actor": "ci",
            "repo": "svc",
            "env": "production",
            "commitSha": "x",
            "commitTime": "2026-06-08T10:00:00",  # naive (no offset)
            "timestamp": "2026-06-08T12:00:00Z",  # aware
        }
    )
    events, skipped = parse_events([line])
    assert skipped == 0
    assert compute_metrics(events).lead_time_seconds == 2 * 3600  # must not raise


def test_parse_events_accepts_an_event_built_from_required_fields() -> None:
    """Drift guard: the keys parse_events reads stay consistent with conventions.requiredFields."""
    event = {field: "x" for field in load_conventions()["telemetry"]["requiredFields"]}
    event["event"] = "deployment.succeeded"
    event["commitTime"] = "2026-06-08T10:00:00Z"
    event["timestamp"] = "2026-06-08T12:00:00Z"
    events, skipped = parse_events([json.dumps(event)])
    assert skipped == 0
    assert len(events) == 1


def test_default_env_is_a_known_environment() -> None:
    assert DEFAULT_ENV in load_conventions()["pipelines"]["environments"]


def test_mttr_is_isolated_per_repo() -> None:
    """A failure in one repo never pairs with a success in another (comparability guarantee)."""
    events = [
        DoraEvent(EVENT_FAILED, "FIN-1", "repo-a", "production", T0, T0),
        DoraEvent(EVENT_SUCCEEDED, "FIN-1", "repo-b", "production", T0, T0 + timedelta(hours=1)),
    ]
    assert compute_metrics(events).mttr_seconds is None


def test_mttr_counts_rolled_back_as_an_incident_start() -> None:
    events = [
        DoraEvent(EVENT_ROLLED_BACK, "FIN-1", "svc", "production", T0, T0),
        DoraEvent(EVENT_SUCCEEDED, "FIN-1", "svc", "production", T0, T0 + timedelta(hours=2)),
    ]
    assert compute_metrics(events).mttr_seconds == 2 * 3600


def test_started_events_are_excluded_from_deploy_outcomes() -> None:
    metrics = compute_metrics([_ev(EVENT_STARTED), _ev(EVENT_SUCCEEDED)])
    assert metrics.total_deploys == 1
    assert metrics.change_failure_rate == 0.0
