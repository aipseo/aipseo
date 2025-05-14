# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Command to validate an AIPSEO configuration file."""

import os
from typing import Any, Dict, List

import typer
from rich.console import Console

from aipseo.utils import read_json_file

console = Console()
ERROR_CONSOLE = Console(stderr=True, style="bold red")


def validate_schema(data: Dict[str, Any]) -> List[str]:
    """Validate AIPSEO manifest schema."""
    errors = []

    # Check required fields
    required_fields = ["tool_id", "version"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    # Check tool_id format
    if "tool_id" in data and (
        not isinstance(data["tool_id"], str) or len(data["tool_id"]) < 8
    ):
        errors.append("Invalid tool_id: Must be a string of at least 8 characters")

    # Check version format
    if "version" in data and not isinstance(data["version"], str):
        errors.append("Invalid version: Must be a string")

    # Check settings if present
    if "settings" in data:
        if not isinstance(data["settings"], dict):
            errors.append("Invalid settings: Must be an object")

    # Check endpoints if present
    if "endpoints" in data:
        if not isinstance(data["endpoints"], list):
            errors.append("Invalid endpoints: Must be an array")

    return errors


def validate_command(file_path: str = "aipseo.json") -> None:
    """Validate an AIPSEO configuration file."""
    if not os.path.exists(file_path):
        ERROR_CONSOLE.print(f"Error: File '{file_path}' not found.")
        raise typer.Exit(1)

    # Read the manifest
    manifest = read_json_file(file_path)

    # Validate the manifest
    errors = validate_schema(manifest)

    if errors:
        ERROR_CONSOLE.print(f"❌ Validation failed for '{file_path}':")
        for error in errors:
            ERROR_CONSOLE.print(f"  - {error}")
        raise typer.Exit(1)
    else:
        console.print(f"✓ Validation passed for [bold]{file_path}[/bold]")
        console.print(f"Tool ID: [bold]{manifest.get('tool_id')}[/bold]")
        console.print(f"Version: [bold]{manifest.get('version')}[/bold]")
