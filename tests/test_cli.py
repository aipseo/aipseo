import pytest
from typer.testing import CliRunner

from aipseo.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "aipseo CLI tool for SEO operations" in result.stdout


def test_version_option():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "aipseo CLI version:" in result.stdout