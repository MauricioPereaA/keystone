"""Tests for the native git hooks installer."""

from pathlib import Path

from devex.hooks import HOOK_NAMES, KEYSTONE_MARKER, install_hooks


def test_install_writes_both_hooks(tmp_path: Path) -> None:
    installed, skipped = install_hooks(tmp_path)
    assert {p.name for p in installed} == set(HOOK_NAMES)
    assert not skipped
    for name in HOOK_NAMES:
        content = (tmp_path / name).read_text(encoding="utf-8")
        assert KEYSTONE_MARKER in content
        assert "devex standards-check" in content


def test_install_skips_a_foreign_existing_hook(tmp_path: Path) -> None:
    (tmp_path / "pre-commit").write_text("# my own hook\n", encoding="utf-8")
    installed, skipped = install_hooks(tmp_path)
    assert (tmp_path / "pre-commit") in skipped
    assert (tmp_path / "pre-commit").read_text(encoding="utf-8") == "# my own hook\n"  # untouched
    assert (tmp_path / "pre-push") in installed


def test_force_replaces_a_foreign_hook(tmp_path: Path) -> None:
    (tmp_path / "pre-commit").write_text("# my own hook\n", encoding="utf-8")
    installed, _ = install_hooks(tmp_path, force=True)
    assert (tmp_path / "pre-commit") in installed
    assert KEYSTONE_MARKER in (tmp_path / "pre-commit").read_text(encoding="utf-8")


def test_reinstall_over_our_own_hook_is_not_skipped(tmp_path: Path) -> None:
    install_hooks(tmp_path)
    installed, skipped = install_hooks(tmp_path)  # our marker is present -> overwrite, not skip
    assert {p.name for p in installed} == set(HOOK_NAMES)
    assert not skipped
