"""CLI smoke tests: command surface + exit codes.

Exit codes are the contract hooks and CI depend on (0 pass / 1 validation fail),
so we assert them directly rather than scraping output.
"""

import json

from typer.testing import CliRunner

from devex.cli import app

runner = CliRunner()


def test_version_runs() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "devex" in result.stdout


def test_check_pr_title_accepts_conventional_title_with_work_id() -> None:
    result = runner.invoke(app, ["check-pr-title", "feat(api): FIN-123 add payment validation"])
    assert result.exit_code == 0


def test_check_pr_title_rejects_title_without_work_id() -> None:
    result = runner.invoke(app, ["check-pr-title", "feat: add payment validation"])
    assert result.exit_code == 1


def test_check_pr_title_rejects_non_conventional_title() -> None:
    result = runner.invoke(app, ["check-pr-title", "FIN-123: add payment validation"])
    assert result.exit_code == 1


def test_workid_extracts_from_ref() -> None:
    result = runner.invoke(app, ["workid", "--ref", "feature/FIN-9-add-thing"])
    assert result.exit_code == 0
    assert "FIN-9" in result.stdout


def test_workid_fails_when_no_work_id_present() -> None:
    result = runner.invoke(app, ["workid", "--ref", "no work id here"])
    assert result.exit_code == 1


def test_dora_reports_metrics_from_a_stream(tmp_path) -> None:
    event = json.dumps(
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
    stream = tmp_path / "events.ndjson"
    stream.write_text(event + "\n", encoding="utf-8")
    result = runner.invoke(app, ["dora", "--stream", str(stream)])
    assert result.exit_code == 0
    assert "DORA metrics" in result.stdout


def test_init_scaffolds_into_a_subdir(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "transactionify", "--language", "python"])
    assert result.exit_code == 0
    assert (tmp_path / "transactionify" / "keystone.json").exists()
    assert (tmp_path / "transactionify" / ".github" / "pull_request_template.md").exists()


def test_init_rejects_bad_service_name(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "BadName"])
    assert result.exit_code == 2


def test_init_rejects_unknown_language(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init", "svc", "--language", "rust"])
    assert result.exit_code == 2


def test_adopt_keeps_existing_files(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "README.md").write_text("MY EXISTING APP", encoding="utf-8")
    result = runner.invoke(app, ["adopt"])
    assert result.exit_code == 0
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "MY EXISTING APP"
    assert (tmp_path / "keystone.json").exists()
