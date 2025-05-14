# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Command to initialize a new aipseo configuration file."""

import os
from typing import Any, Dict

import typer
from rich.console import Console

from aipseo.utils import generate_tool_id, write_json_file

console = Console()
ERROR_CONSOLE = Console(stderr=True, style="bold red")


def init_command(output_path: str = "aipseo.json", force: bool = False) -> None:
    """Initialize a new aipseo configuration file."""
    if os.path.exists(output_path) and not force:
        ERROR_CONSOLE.print(
            f"Error: File '{output_path}' already exists. Use --force to overwrite."
        )
        raise typer.Exit(1)

    # Create a minimal manifest
    manifest: Dict[str, Any] = {
        "tool_id": generate_tool_id(),
        "version": "1.0.0",
        "settings": {
            "api_enabled": True,
            "notifications_enabled": False,
            "api": {
                "environment": "development",
                "endpoints": {
                    "development": "https://dev-api.aipseo.repl.co/v1",
                    "staging": "https://staging-api.aipseo.repl.co/v1",
                    "production": "https://api.aipseo.repl.co/v1"
                },
                "timeout": 30,
                "max_retries": 3,
                "retry_delay": 1
            }
        },
        "endpoints": [],
    }

    # Write the manifest
    if write_json_file(output_path, manifest, force):
        console.print(f"✓ Created aipseo manifest at [bold]{output_path}[/bold]")
        console.print(f"Tool ID: [bold]{manifest['tool_id']}[/bold]")
    else:
        ERROR_CONSOLE.print(f"Error: Failed to create manifest at '{output_path}'.")
        raise typer.Exit(1)
