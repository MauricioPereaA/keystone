"""Tests for local pipeline simulation helpers."""

import json
from pathlib import Path

from devex.pipeline import (
    LOCAL_TEST_COMMANDS,
    detect_language,
    language_test_command,
    local_setup_commands,
)


def test_detect_language_defaults_without_config(tmp_path: Path) -> None:
    assert detect_language(tmp_path) == "python"


def test_detect_language_reads_keystone_json(tmp_path: Path) -> None:
    (tmp_path / "keystone.json").write_text(json.dumps({"service": "s", "language": "go"}), encoding="utf-8")
    assert detect_language(tmp_path) == "go"


def test_detect_language_tolerates_bad_json(tmp_path: Path) -> None:
    (tmp_path / "keystone.json").write_text("{ not json", encoding="utf-8")
    assert detect_language(tmp_path) == "python"


def test_language_test_command_per_language() -> None:
    # --no-project mirrors the generated CI step: works for uv-native and pip venvs.
    assert language_test_command("python") == ["uv", "run", "--no-project", "pytest", "-q"]
    assert language_test_command("typescript")[0] == "pnpm"
    assert language_test_command("rust") is None


def test_every_framework_language_has_a_local_command() -> None:
    # Mirror guard: keep the local commands in step with the four supported languages.
    assert set(LOCAL_TEST_COMMANDS) == {"python", "typescript", "go", "clojure"}


def test_setup_mirrors_uv_native_project(tmp_path: Path) -> None:
    # CI parity: with a pyproject the toolchain syncs the project before testing,
    # so a stale local venv can't pass what a fresh CI sync would fail.
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    assert local_setup_commands("python", tmp_path) == [["uv", "sync", "--extra", "dev"]]


def test_setup_mirrors_pip_requirements_project(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("six\n", encoding="utf-8")
    assert local_setup_commands("python", tmp_path) == [
        ["uv", "venv"],
        ["uv", "pip", "install", "-r", "requirements.txt"],
    ]


def test_setup_includes_dev_requirements_when_present(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("six\n", encoding="utf-8")
    (tmp_path / "requirements-dev.txt").write_text("pytest\n", encoding="utf-8")
    commands = local_setup_commands("python", tmp_path)
    assert ["uv", "pip", "install", "-r", "requirements-dev.txt"] in commands


def test_setup_for_other_languages(tmp_path: Path) -> None:
    assert local_setup_commands("typescript", tmp_path) == [["pnpm", "install", "--frozen-lockfile"]]
    assert local_setup_commands("go", tmp_path) == [["go", "mod", "download"]]
    assert local_setup_commands("clojure", tmp_path) == []
    assert local_setup_commands("rust", tmp_path) == []
