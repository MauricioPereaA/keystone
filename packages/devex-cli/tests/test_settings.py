"""Tests for the single config entrypoint."""

from pathlib import Path

import devex.settings as settings


def test_conventions_path_is_none_when_unset(monkeypatch) -> None:
    monkeypatch.delenv(settings.CONVENTIONS_PATH_ENV, raising=False)
    assert settings.conventions_path() is None


def test_conventions_path_returns_path_when_set(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "conventions.json"
    monkeypatch.setenv(settings.CONVENTIONS_PATH_ENV, str(target))
    assert settings.conventions_path() == target


def test_telemetry_stream_is_none_when_unset(monkeypatch) -> None:
    monkeypatch.delenv(settings.TELEMETRY_STREAM_ENV, raising=False)
    assert settings.telemetry_stream_path() is None


def test_ci_branch_is_none_outside_ci(monkeypatch) -> None:
    monkeypatch.delenv(settings.CI_HEAD_REF_ENV, raising=False)
    monkeypatch.delenv(settings.CI_REF_NAME_ENV, raising=False)
    assert settings.ci_branch() is None


def test_ci_branch_prefers_head_ref_then_ref_name(monkeypatch) -> None:
    # On a pull_request both may be set; the PR source branch (HEAD_REF) wins.
    monkeypatch.setenv(settings.CI_HEAD_REF_ENV, "feature/FIN-1-x")
    monkeypatch.setenv(settings.CI_REF_NAME_ENV, "1/merge")
    assert settings.ci_branch() == "feature/FIN-1-x"
    # On push only REF_NAME is set.
    monkeypatch.delenv(settings.CI_HEAD_REF_ENV, raising=False)
    monkeypatch.setenv(settings.CI_REF_NAME_ENV, "main")
    assert settings.ci_branch() == "main"
