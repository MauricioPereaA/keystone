"""DORA metrics computed from the DoraEvent stream.

The four metrics derive from the SINGLE telemetry stream the framework emits
(ADR-0002), never per-language instrumentation. Pure functions here; the CLI
command renders them. The event field names are the contract's camelCase
(workId / commitSha / commitTime) — what `@keystone/platform` actually emits.
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

# Deployment event vocabulary — mirrors conventions.json telemetry.events and the
# TS DeploymentEvent union (a test guards that these stay in parity with the source).
EVENT_STARTED = "deployment.started"
EVENT_SUCCEEDED = "deployment.succeeded"
EVENT_FAILED = "deployment.failed"
EVENT_ROLLED_BACK = "deployment.rolled_back"

DEFAULT_ENV = "production"


@dataclass(frozen=True)
class DoraEvent:
    event: str
    work_id: str
    repo: str
    env: str
    commit_time: datetime
    timestamp: datetime


@dataclass(frozen=True)
class DoraMetrics:
    deployment_frequency: int  # count of succeeded deploys in the target env
    lead_time_seconds: float | None  # median(timestamp - commitTime)
    change_failure_rate: float  # (failed + rolled_back) / total deploy outcomes
    mttr_seconds: float | None  # mean(failed -> next succeeded)
    total_deploys: int
    window: tuple[datetime, datetime] | None


def _parse_ts(value: str) -> datetime:
    # Accept the trailing "Z" that ISO-8601 / the framework emits, and normalize a
    # naive value to UTC so naive and aware events never collide in arithmetic
    # (otherwise a single hand-written/legacy line crashes the whole DORA report).
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def parse_events(lines: Iterable[str]) -> tuple[list[DoraEvent], int]:
    """Parse NDJSON DoraEvent lines. Returns (events, skipped) — malformed lines are skipped, not fatal."""
    events: list[DoraEvent] = []
    skipped = 0
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            events.append(
                DoraEvent(
                    event=data["event"],
                    work_id=str(data.get("workId", "")),
                    repo=str(data.get("repo", "")),
                    env=str(data.get("env", "")),
                    commit_time=_parse_ts(data["commitTime"]),
                    timestamp=_parse_ts(data["timestamp"]),
                )
            )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            skipped += 1
    return events, skipped


def _mttr_seconds(deploys: list[DoraEvent]) -> float | None:
    """Mean recovery time: per repo, from a failure to the next success."""
    by_repo: dict[str, list[DoraEvent]] = defaultdict(list)
    for event in sorted(deploys, key=lambda e: e.timestamp):
        by_repo[event.repo].append(event)
    recoveries: list[float] = []
    for repo_events in by_repo.values():
        failed_at: datetime | None = None
        for event in repo_events:
            if event.event in (EVENT_FAILED, EVENT_ROLLED_BACK):
                if failed_at is None:
                    failed_at = event.timestamp
            elif event.event == EVENT_SUCCEEDED and failed_at is not None:
                recoveries.append((event.timestamp - failed_at).total_seconds())
                failed_at = None
    return statistics.mean(recoveries) if recoveries else None


def compute_metrics(events: list[DoraEvent], env: str = DEFAULT_ENV) -> DoraMetrics:
    """Compute the four DORA metrics for the given environment."""
    outcomes = (EVENT_SUCCEEDED, EVENT_FAILED, EVENT_ROLLED_BACK)
    deploys = [e for e in events if e.event in outcomes and e.env == env]
    succeeded = [e for e in deploys if e.event == EVENT_SUCCEEDED]
    failures = [e for e in deploys if e.event in (EVENT_FAILED, EVENT_ROLLED_BACK)]
    leads = [(e.timestamp - e.commit_time).total_seconds() for e in succeeded]
    return DoraMetrics(
        deployment_frequency=len(succeeded),
        lead_time_seconds=statistics.median(leads) if leads else None,
        change_failure_rate=len(failures) / len(deploys) if deploys else 0.0,
        mttr_seconds=_mttr_seconds(deploys),
        total_deploys=len(deploys),
        window=(min(e.timestamp for e in deploys), max(e.timestamp for e in deploys)) if deploys else None,
    )
