import pytest
from typer.testing import CliRunner
import json

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


def test_toolspec_openai():
    result = runner.invoke(app, ["toolspec", "--format", "openai"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    names = [fn["name"] for fn in data]
    assert "lookup" in names