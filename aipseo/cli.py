# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""aipseo CLI entry point."""

from typing import Optional

import typer
from rich.console import Console

from aipseo import __version__
from aipseo.commands.init import init_command
from aipseo.commands.lookup import lookup_command
from aipseo.commands.market import market_app
from aipseo.commands.spam_score import spam_score_command
from aipseo.commands.validate import validate_command
from aipseo.commands.wallet import wallet_app

console = Console()
app = typer.Typer(help="aipseo CLI tool for SEO operations")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show the application version and exit."
    )
):
    """aipseo CLI - Tools for SEO operations."""
    if version:
        console.print(f"aipseo CLI version: [bold]{__version__}[/bold]")
        raise typer.Exit()


@app.command()
def init(
    output: str = typer.Option(
        "aipseo.json", "--output", "-o", help="Output file path"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
):
    """Initialize a new aipseo configuration file."""
    init_command(output, force)


@app.command()
def validate(
    file_path: str = typer.Option(
        "aipseo.json", "--file", "-f", help="Path to aipseo manifest file"
    )
):
    """Validate an aipseo configuration file."""
    validate_command(file_path)


@app.command()
def lookup(
    url: str = typer.Argument(..., help="URL to look up"),
    format: str = typer.Option(
        "pretty", "--format", "-f", help="Output format (json, pretty)"
    ),
):
    """Look up information for a URL."""
    lookup_command(url, format)


@app.command("spam-score")
def spam_score(
    url: str = typer.Argument(..., help="URL to check"),
    format: str = typer.Option(
        "pretty", "--format", "-f", help="Output format (json, pretty)"
    ),
):
    """Check spam score for a URL."""
    spam_score_command(url, format)


# Add wallet and marketplace command groups
app.add_typer(wallet_app, name="wallet")
app.add_typer(market_app, name="market")


if __name__ == "__main__":
    app()
