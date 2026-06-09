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
