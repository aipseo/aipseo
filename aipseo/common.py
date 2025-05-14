"""Common utilities shared across aipseo modules."""

import json
import os
import sys
from typing import Any, Dict

from rich.console import Console
from rich.table import Table

# Create console instances
console = Console()
ERROR_CONSOLE = Console(stderr=True, style="bold red")

def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read a JSON file and return its contents."""
    try:
        if not os.path.exists(file_path):
            ERROR_CONSOLE.print(f"Error: File '{file_path}' not found.")
            sys.exit(1)

        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        ERROR_CONSOLE.print(f"Error: File '{file_path}' is not valid JSON.")
        sys.exit(1)
    except Exception as e:
        ERROR_CONSOLE.print(f"Error reading file: {e}")
        sys.exit(1)

def format_output(data: Dict[str, Any], format_type: str = "pretty") -> None:
    """Format and print data based on the specified format."""
    if format_type.lower() == "json":
        console.print(json.dumps(data, indent=2))
    else:  # pretty
        if "error" in data:
            ERROR_CONSOLE.print(f"Error: {data['error']}")
            sys.exit(1)

        # Create a table for the data
        table = Table(title="aipseo Results")

        # Add columns and rows based on data structure
        if isinstance(data, dict):
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    table.add_row(key, json.dumps(value, indent=2))
                else:
                    table.add_row(key, str(value))

        console.print(table) 