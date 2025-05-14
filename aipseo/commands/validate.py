# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Command to validate an aipseo configuration file."""

import os
from typing import Any, Dict, List

import typer
from rich.console import Console

from aipseo.common import ERROR_CONSOLE, console, format_output
from aipseo.utils import read_json_file

console = Console()
ERROR_CONSOLE = Console(stderr=True, style="bold red")


def validate_schema(data: Dict[str, Any]) -> List[str]:
    """Validate aipseo manifest schema."""
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
        else:
            # Validate API settings if present
            if "api" in data["settings"]:
                api_settings = data["settings"]["api"]
                if not isinstance(api_settings, dict):
                    errors.append("Invalid api settings: Must be an object")
                else:
                    # Check environment
                    if "environment" not in api_settings:
                        errors.append("Missing api.environment setting")
                    elif api_settings["environment"] not in ["development", "staging", "production"]:
                        errors.append("Invalid api.environment: Must be one of development, staging, production")
                    
                    # Check endpoints
                    if "endpoints" not in api_settings:
                        errors.append("Missing api.endpoints setting")
                    elif not isinstance(api_settings["endpoints"], dict):
                        errors.append("Invalid api.endpoints: Must be an object")
                    else:
                        required_envs = ["development", "staging", "production"]
                        for env in required_envs:
                            if env not in api_settings["endpoints"]:
                                errors.append(f"Missing api.endpoints.{env}")
                            elif not isinstance(api_settings["endpoints"][env], str):
                                errors.append(f"Invalid api.endpoints.{env}: Must be a string")
                    
                    # Check timeout
                    if "timeout" in api_settings and not isinstance(api_settings["timeout"], (int, float)):
                        errors.append("Invalid api.timeout: Must be a number")
                    
                    # Check retry settings
                    if "max_retries" in api_settings and not isinstance(api_settings["max_retries"], int):
                        errors.append("Invalid api.max_retries: Must be an integer")
                    if "retry_delay" in api_settings and not isinstance(api_settings["retry_delay"], (int, float)):
                        errors.append("Invalid api.retry_delay: Must be a number")

    # Check endpoints if present
    if "endpoints" in data:
        if not isinstance(data["endpoints"], list):
            errors.append("Invalid endpoints: Must be an array")

    return errors


def validate_command(file_path: str = "aipseo.json") -> None:
    """Validate an aipseo configuration file."""
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
        # Format the output using the common function
        format_output({
            "status": "success",
            "file": file_path,
            "tool_id": manifest.get("tool_id"),
            "version": manifest.get("version")
        })
