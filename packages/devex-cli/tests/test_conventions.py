"""Tests for conventions loading + Pydantic validation (fail-fast on a bad source)."""

import json
from pathlib import Path

import pytest

from devex.conventions import load_conventions
from devex.schema import ConventionsError, validate_conventions

# A minimal conventions dict that satisfies the schema (used for override tests).
VALID: dict = {
    "workId": {"pattern": r"^[A-Z]{2,5}-\d+$"},
    "branch": {"pattern": r"^(feature|fix)/[A-Z]{2,5}-\d+-[a-z0-9-]+$"},
    "commit": {"pattern": r"^(feat|fix): [A-Z]{2,5}-\d+ .+"},
    "pullRequest": {"titlePattern": r"^(feat|fix): [A-Z]{2,5}-\d+ .+"},
    "pipelines": {
        "prPipeline": {"triggers": ["pull_request"], "stages": ["small-tests"], "smallTests": ["unit"]},
        "integrationPipeline": {"triggers": ["push.main"], "stages": ["deploy"]},
        "environments": ["sandbox", "staging", "production"],
    },
    "telemetry": {
        "schemaVersion": "1.0.0",
        "events": ["deployment.succeeded"],
        "doraMetrics": ["deployment_frequency"],
        "requiredFields": ["event"],
    },
}


@pytest.fixture(autouse=True)
def _clear_conventions_cache():
    load_conventions.cache_clear()
    yield
    load_conventions.cache_clear()


def test_bundled_conventions_loads_and_validates() -> None:
    conv = load_conventions()
    assert conv["branch"]["pattern"]
    assert conv["telemetry"]["schemaVersion"]


def test_override_path_is_read(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "conventions.json"
    target.write_text(json.dumps(VALID), encoding="utf-8")
    monkeypatch.setenv("KEYSTONE_CONVENTIONS_PATH", str(target))
    load_conventions.cache_clear()
    assert load_conventions()["workId"]["pattern"] == VALID["workId"]["pattern"]


def test_missing_override_file_fails_fast(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KEYSTONE_CONVENTIONS_PATH", str(tmp_path / "does-not-exist.json"))
    load_conventions.cache_clear()
    with pytest.raises(ConventionsError):
        load_conventions()


def test_invalid_json_fails_fast(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "conventions.json"
    target.write_text("{ not json", encoding="utf-8")
    monkeypatch.setenv("KEYSTONE_CONVENTIONS_PATH", str(target))
    load_conventions.cache_clear()
    with pytest.raises(ConventionsError):
        load_conventions()


def test_schema_violation_raises() -> None:
    with pytest.raises(ConventionsError):
        validate_conventions({"workId": {"pattern": "x"}})  # missing branch/commit/...


def test_invalid_regex_pattern_raises() -> None:
    bad = json.loads(json.dumps(VALID))
    bad["branch"]["pattern"] = "([unclosed"
    with pytest.raises(ConventionsError):
        validate_conventions(bad)
