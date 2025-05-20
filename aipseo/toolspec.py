# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman
# ruff: noqa: I001

"""Generate machine-readable tool specifications for aipseo commands."""

import inspect
import json
from typing import Any, Dict, List, Optional, Union
from typing import get_args, get_origin

import typer


def _map_type(annotation: Any) -> str:
    """
    Map a Python type annotation to a JSON schema type.
    """
    if annotation is str:
        return "string"
    if annotation is bool:
        return "boolean"
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    return "string"


def generate_openai_spec() -> List[Dict[str, Any]]:
    """
    Generate an OpenAI function-calling schema for all aipseo CLI commands.
    """
    from aipseo.cli import app

    specs: List[Dict[str, Any]] = []

    def process_command(callback: Any, name_override: Optional[str] = None) -> None:
        cmd_name = name_override or callback.__name__
        description = inspect.getdoc(callback) or ""
        sig = inspect.signature(callback)
        properties: Dict[str, Any] = {}
        required: List[str] = []
        for param in sig.parameters.values():
            param_name = param.name
            param_info = param.default
            annotation = param.annotation

            origin = get_origin(annotation)
            if origin is Union:
                args = [arg for arg in get_args(annotation) if arg is not type(None)]
                types = [_map_type(arg) for arg in args]
                if len(types) == 1:
                    json_type = types[0]
                else:
                    json_type = types
            else:
                json_type = _map_type(annotation)

            prop: Dict[str, Any] = {"type": json_type}
            help_text = getattr(param_info, "help", None)
            if help_text:
                prop["description"] = help_text
            default_val = getattr(param_info, "default", None)
            if default_val is not ...:
                prop["default"] = default_val
            if default_val is ...:
                required.append(param_name)

            properties[param_name] = prop

        entry: Dict[str, Any] = {
            "name": cmd_name,
            "description": description,
            "parameters": {"type": "object", "properties": properties},
        }
        if required:
            entry["parameters"]["required"] = required
        specs.append(entry)

    # Top-level commands
    for cmd_info in app.registered_commands:
        process_command(cmd_info.callback)

    # Subcommands in each group
    for group_info in app.registered_groups:
        group_name = group_info.name
        for cmd_info in group_info.typer_instance.registered_commands:
            override = f"{group_name}_{cmd_info.callback.__name__}"
            process_command(cmd_info.callback, name_override=override)

    return specs


def emit_tool_spec(format: str) -> None:
    """
    Emit a tool specification in the requested format.
    """
    fmt = format.lower()
    if fmt != "openai":
        typer.echo(f"Error: Unsupported format '{format}'", err=True)
        raise typer.Exit(1)

    spec = generate_openai_spec()
    typer.echo(json.dumps(spec, indent=2))
