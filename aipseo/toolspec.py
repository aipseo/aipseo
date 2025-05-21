# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman
# ruff: noqa: I001

"""Generate machine-readable tool specifications for aipseo commands."""

import inspect
import json
import sys # Added for printing notices to stderr
from typing import Any, Dict, List, Optional, Union, get_args, get_origin

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


def _generate_schema_for_callable(func: Any, name_override: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates an OpenAI-compatible schema for a given Python callable.
    """
    func_name = name_override or func.__name__
    description = inspect.getdoc(func) or ""
    sig = inspect.signature(func)
    properties: Dict[str, Any] = {}
    required: List[str] = []

    for param in sig.parameters.values():
        param_name = param.name
        annotation = param.annotation

        is_optional = False
        actual_annotation = annotation
        origin = get_origin(annotation)
        if origin is Union: # Handles Optional[X] which is Union[X, NoneType]
            union_args = get_args(annotation)
            if type(None) in union_args:
                is_optional = True
                non_none_args = [arg for arg in union_args if arg is not type(None)]
                if non_none_args:
                    actual_annotation = non_none_args[0]
                # If non_none_args is empty, it means annotation was Union[NoneType]
                # In such a case, actual_annotation remains NoneType, and _map_type will handle it.

        json_type = _map_type(actual_annotation)
        prop: Dict[str, Any] = {"type": json_type}
        
        # Parameter description (omitted for simplicity as per instructions)
        # prop["description"] = "Parsed description for " + param_name

        properties[param_name] = prop

        if param.default is inspect.Parameter.empty and not is_optional:
            required.append(param_name)
        elif param.default is not inspect.Parameter.empty:
            try:
                # Ensure default value is suitable for JSON
                json.dumps(param.default)
                prop["default"] = param.default
            except TypeError:
                # Default value is not JSON serializable, skip adding it.
                # Or represent it as a string, e.g., prop["x-python-default"] = str(param.default)
                pass # As per instructions

    schema: Dict[str, Any] = {
        "name": func_name,
        "description": description,
        "parameters": {"type": "object", "properties": properties},
    }
    if required:
        schema["parameters"]["required"] = required
    return schema


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

    # Add specs for agent_tools
    try:
        from aipseo import agent_tools # Import the module

        # List of functions from agent_tools to expose
        agent_tool_functions = [
            agent_tools.get_url_lookup,
            agent_tools.get_spam_score,
            agent_tools.list_market_opportunities,
            agent_tools.get_wallet_balance,
        ]

        for func_to_spec in agent_tool_functions:
            # Ensure the function is callable before trying to generate a spec
            if callable(func_to_spec):
                tool_schema = _generate_schema_for_callable(func_to_spec) # Call the new helper
                specs.append(tool_schema)
    except ImportError:
        # agent_tools.py might not be present, or specific tools are not yet defined.
        # This allows toolspec to run without erroring if they are missing.
        print("Notice: aipseo.agent_tools not found or functions missing, skipping their spec generation.", file=sys.stderr)
    except AttributeError as e:
        # Handle cases where agent_tools exists but a specific function is missing
        print(f"Notice: Attribute error while processing agent_tools: {e}", file=sys.stderr)

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
