"""Tests for service scaffolding (the init / adopt logic)."""

import json
from pathlib import Path

from devex.scaffold import is_valid_service_name, scaffold_service


def test_valid_service_names() -> None:
    assert is_valid_service_name("transactionify")
    assert is_valid_service_name("pay-svc-1")
    assert not is_valid_service_name("Transactionify")  # uppercase
    assert not is_valid_service_name("1svc")  # leading digit
    assert not is_valid_service_name("a/b")  # path separator
    assert not is_valid_service_name("")


def test_scaffold_creates_golden_path_files(tmp_path: Path) -> None:
    result = scaffold_service(tmp_path, "transactionify", "python", overwrite=False)
    created = {p.name for p in result.created}
    assert {"keystone.json", "package.json", "README.md"} <= created
    assert (tmp_path / ".github" / "pull_request_template.md").exists()
    assert (tmp_path / "scripts" / "generate-workflows.mjs").exists()
    config = json.loads((tmp_path / "keystone.json").read_text(encoding="utf-8"))
    assert config == {"service": "transactionify", "language": "python"}


def test_package_json_pulls_the_framework(tmp_path: Path) -> None:
    scaffold_service(tmp_path, "svc", "typescript", overwrite=False)
    pkg = json.loads((tmp_path / "package.json").read_text(encoding="utf-8"))
    assert "@keystone/platform" in pkg["dependencies"]
    assert pkg["scripts"]["generate:workflows"]


def test_generate_wrapper_threads_api_spec_through(tmp_path: Path) -> None:
    # keystone.json's optional apiSpec must reach both generators so the
    # contract step targets the service's real OpenAPI spec.
    scaffold_service(tmp_path, "svc", "python", overwrite=False)
    wrapper = (tmp_path / "scripts" / "generate-workflows.mjs").read_text(encoding="utf-8")
    assert "apiSpec" in wrapper
    assert "generatePrPipeline({ repo: service, language, apiSpec })" in wrapper
    assert "generateIntegrationPipeline({ repo: service, language, apiSpec })" in wrapper


def test_adopt_never_overwrites_existing_files(tmp_path: Path) -> None:
    existing = tmp_path / "README.md"
    existing.write_text("MY EXISTING APP", encoding="utf-8")
    result = scaffold_service(tmp_path, "svc", "python", overwrite=False)
    assert existing in result.skipped
    assert existing.read_text(encoding="utf-8") == "MY EXISTING APP"  # untouched
    assert (tmp_path / "keystone.json") in result.created  # new artifact still added
