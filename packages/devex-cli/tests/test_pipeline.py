"""Tests for local pipeline simulation helpers."""

import json
from pathlib import Path

from devex.pipeline import LOCAL_TEST_COMMANDS, detect_language, language_test_command


def test_detect_language_defaults_without_config(tmp_path: Path) -> None:
    assert detect_language(tmp_path) == "python"


def test_detect_language_reads_keystone_json(tmp_path: Path) -> None:
    (tmp_path / "keystone.json").write_text(json.dumps({"service": "s", "language": "go"}), encoding="utf-8")
    assert detect_language(tmp_path) == "go"


def test_detect_language_tolerates_bad_json(tmp_path: Path) -> None:
    (tmp_path / "keystone.json").write_text("{ not json", encoding="utf-8")
    assert detect_language(tmp_path) == "python"


def test_language_test_command_per_language() -> None:
    assert language_test_command("python") == ["uv", "run", "pytest", "-q"]
    assert language_test_command("typescript")[0] == "pnpm"
    assert language_test_command("rust") is None


def test_every_framework_language_has_a_local_command() -> None:
    # Mirror guard: keep the local commands in step with the four supported languages.
    assert set(LOCAL_TEST_COMMANDS) == {"python", "typescript", "go", "clojure"}
