"""Smoke test: package imports, CLI is wired, repo root resolves."""

from __future__ import annotations

from click.testing import CliRunner

from coc import __version__
from coc.cli import main


def test_version_string():
    assert isinstance(__version__, str)
    assert len(__version__.split(".")) == 3


def test_cli_help_exits_zero():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Catalog of Complexity CLI" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_repo_root_resolves(repo_root):
    assert (repo_root / "pyproject.toml").exists()
