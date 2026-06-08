"""CLI smoke tests: command surface + exit codes.

Exit codes are the contract hooks and CI depend on (0 pass / 1 validation fail),
so we assert them directly rather than scraping output.
"""

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
