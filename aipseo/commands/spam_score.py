# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Command to check spam score for a URL."""

import typer
from rich.console import Console

from aipseo.common import format_output
from aipseo.utils import make_api_request

console = Console()
ERROR_CONSOLE = Console(stderr=True, style="bold red")


def spam_score_command(url: str, format_type: str = "pretty") -> None:
    """Check spam score for a URL."""
    # Validate URL
    if not url or not isinstance(url, str):
        ERROR_CONSOLE.print("Error: URL must be provided.")
        raise typer.Exit(1)

    # Clean the URL by removing protocol if present
    clean_url = url.lower()
    for protocol in ["http://", "https://"]:
        if clean_url.startswith(protocol):
            clean_url = clean_url[len(protocol) :]
            break

    # Make the API request
    result = make_api_request("spam-score", params={"url": clean_url})

    # Format and display the result
    format_output(result, format_type)
