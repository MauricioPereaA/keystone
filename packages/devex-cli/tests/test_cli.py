"""CLI smoke tests: command surface + exit codes.

Exit codes are the contract hooks and CI depend on (0 pass / 1 validation fail),
so we assert them directly rather than scraping output.
"""

import json
import os
import subprocess

from typer.testing import CliRunner

from devex.cli import app

_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


def _git_init(path, branch: str) -> None:
    subprocess.run(["git", "init", "-b", branch], cwd=path, check=True, capture_output=True)

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


def test_hooks_install_in_a_git_repo(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _git_init(tmp_path, "main")
    result = runner.invoke(app, ["hooks", "install"])
    assert result.exit_code == 0
    assert (tmp_path / ".git" / "hooks" / "pre-commit").exists()
    assert (tmp_path / ".git" / "hooks" / "pre-push").exists()


def test_pr_rejects_a_protected_branch(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _git_init(tmp_path, "main")
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: FIN-1 init"],
        cwd=tmp_path,
        env=_GIT_ENV,
        check=True,
        capture_output=True,
    )
    result = runner.invoke(app, ["pr", "--dry-run"])
    assert result.exit_code == 2


def test_pr_dry_run_on_a_feature_branch(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _git_init(tmp_path, "feature/FIN-1-thing")
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "feat: FIN-1 add thing"],
        cwd=tmp_path,
        env=_GIT_ENV,
        check=True,
        capture_output=True,
    )
    result = runner.invoke(app, ["pr", "--dry-run"])
    assert result.exit_code == 0
    assert "would open PR" in result.output


def test_pipeline_run_no_local_is_unsupported(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["pipeline", "run", "--no-local"])
    assert result.exit_code == 2
