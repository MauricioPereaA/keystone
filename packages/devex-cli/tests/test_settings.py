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
