# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Utility functions for the aipseo CLI."""

import base64
import json
import os
import random
import string
import sys
import webbrowser
from typing import Any, Dict, List, Optional, Tuple, Union

import typer
from rich.console import Console
from rich.table import Table
from aipseo.api import APIClient
from aipseo.common import ERROR_CONSOLE, console, read_json_file

# Try to import cryptography modules, but handle the case where they're not installed
CRYPTO_AVAILABLE = False
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    # Only set this to True if all imports succeed
    CRYPTO_AVAILABLE = True
except ImportError:
    # Define placeholder classes to avoid LSP errors
    # These will never be used when CRYPTO_AVAILABLE is False
    class Fernet:
        def __init__(self, key):
            pass

        def encrypt(self, data):
            pass

        def decrypt(self, data):
            pass

    class hashes:
        class SHA256:
            pass

    class PBKDF2HMAC:
        def __init__(self, algorithm, length, salt, iterations):
            pass

        def derive(self, key_material):
            pass


console = Console()
ERROR_CONSOLE = Console(stderr=True, style="bold red")

# Default wallet file location
DEFAULT_WALLET_PATH = ".wallet.json"


def generate_tool_id(length: int = 12) -> str:
    """Generate a random tool ID."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


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


def write_json_file(file_path: str, data: Dict[str, Any], force: bool = False) -> bool:
    """Write data to a JSON file."""
    try:
        # If the file exists and we're not forcing, return False
        if os.path.exists(file_path) and not force:
            return False

        # Ensure the directory exists
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # Write the data
        with open(file_path, "w") as f:
            json.dump(data, indent=2, sort_keys=True, fp=f)
        return True
    except Exception as e:
        ERROR_CONSOLE.print(f"Error writing file: {e}")
        sys.exit(1)


def derive_key_from_password(
    password: str, salt: Optional[bytes] = None
) -> Tuple[bytes, bytes]:
    """Derive a key from a password using PBKDF2."""
    if not CRYPTO_AVAILABLE:
        ERROR_CONSOLE.print(
            "Error: cryptography package is not installed. "
            "Run 'pip install cryptography'."
        )
        raise typer.Exit(1)

    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_data(
    data: str, password: str, salt: Optional[bytes] = None
) -> Dict[str, str]:
    """Encrypt data using Fernet symmetric encryption."""
    if not CRYPTO_AVAILABLE:
        ERROR_CONSOLE.print(
            "Error: cryptography package is not installed. "
            "Run 'pip install cryptography'."
        )
        raise typer.Exit(1)

    key, salt_bytes = derive_key_from_password(password, salt)
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())

    return {
        "encrypted_data": base64.b64encode(encrypted_data).decode("utf-8"),
        "salt": base64.b64encode(salt_bytes).decode("utf-8"),
    }


def decrypt_data(encrypted_data: str, password: str, salt: str) -> str:
    """Decrypt data that was encrypted with Fernet."""
    if not CRYPTO_AVAILABLE:
        ERROR_CONSOLE.print(
            "Error: cryptography package is not installed. "
            "Run 'pip install cryptography'."
        )
        raise typer.Exit(1)

    try:
        salt_bytes = base64.b64decode(salt)
        key, _ = derive_key_from_password(password, salt_bytes)

        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(base64.b64decode(encrypted_data))

        return decrypted_data.decode("utf-8")
    except Exception as e:
        ERROR_CONSOLE.print(f"Error decrypting data: {e}")
        raise typer.Exit(1) from None


def read_wallet_file(wallet_path: str, password: str) -> Dict[str, Any]:
    """Read and decrypt a wallet file."""
    try:
        with open(wallet_path, "r") as f:
            encrypted_wallet = json.load(f)

        wallet_id = decrypt_data(
            encrypted_wallet["encrypted_data"], password, encrypted_wallet["salt"]
        )

        return {"wallet_id": wallet_id}
    except FileNotFoundError:
        ERROR_CONSOLE.print(f"Error: Wallet file not found at {wallet_path}")
        raise typer.Exit(1) from None
    except json.JSONDecodeError:
        ERROR_CONSOLE.print(f"Error: Invalid wallet file format at {wallet_path}")
        raise typer.Exit(1) from None
    except Exception as e:
        ERROR_CONSOLE.print(f"Error reading wallet: {e}")
        raise typer.Exit(1) from None


def write_wallet_file(wallet_path: str, wallet_id: str, password: str) -> None:
    """Encrypt and write wallet data to file."""
    try:
        encrypted_data = encrypt_data(wallet_id, password)

        with open(wallet_path, "w") as f:
            json.dump(encrypted_data, f)

        console.print(f"✅ Wallet saved to [bold]{wallet_path}[/bold]")
    except Exception as e:
        ERROR_CONSOLE.print(f"Error writing wallet file: {e}")
        raise typer.Exit(1) from None


def open_browser(url: str) -> None:
    """Open a URL in the default web browser."""
    console.print(f"Opening [link={url}]{url}[/link] in your browser...")
    webbrowser.open(url)


def display_marketplace_listings(listings: List[Dict[str, Any]]) -> None:
    """Display marketplace listings in a formatted table."""
    if not listings:
        console.print("No listings match your criteria.")
        return

    table = Table(title="Marketplace Listings")
    table.add_column("ID", style="cyan")
    table.add_column("Source URL", style="green")
    table.add_column("DR", style="yellow")
    table.add_column("Price (USD)", style="blue")
    table.add_column("Anchor Text", style="magenta")

    for listing in listings:
        table.add_row(
            listing.get("listing_id", ""),
            listing.get("source_url", ""),
            str(listing.get("dr_bucket", "")),
            f"${listing.get('price_usd', 0):.2f}",
            listing.get("anchor", ""),
        )

    console.print(table)


def make_api_request(
    endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Make a request to the aipseo API using the API client."""
    try:
        client = APIClient()
        
        # Map endpoints to client methods
        if endpoint == "lookup":
            return client.lookup(params.get("url", ""))
        elif endpoint == "spam-score":
            return client.spam_score(params.get("url", ""))
        elif endpoint == "wallet/create":
            return client.create_wallet(params.get("name", "default"))
        elif endpoint == "wallet/balance":
            return client.get_balance(params.get("wallet_id", ""))
        elif endpoint == "wallet/deposit":
            return client.deposit(
                params.get("wallet_id", ""),
                params.get("amount_usd", 0.0)
            )
        elif endpoint == "wallet/withdraw":
            return client.withdraw(
                params.get("wallet_id", ""),
                params.get("amount_usd", 0.0),
                params.get("dest", "")
            )
        elif endpoint == "marketplace/search":
            return client.search_marketplace(
                dr_min=params.get("dr_min"),
                price_max=params.get("price_max"),
                topic=params.get("topic")
            )
        elif endpoint == "marketplace/buy":
            return client.buy_listing(
                params.get("wallet_id", ""),
                params.get("listing_id", "")
            )
        elif endpoint == "marketplace/list":
            return client.list_backlink(
                wallet_id=params.get("wallet_id", ""),
                source_url=params.get("source_url", ""),
                target_url=params.get("target_url", ""),
                price=params.get("price_usd", 0.0),
                anchor=params.get("anchor", ""),
                rel=params.get("rel")
            )
        else:
            return {"error": f"Unknown endpoint: {endpoint}"}
            
    except Exception as e:
        ERROR_CONSOLE.print(f"Error: {str(e)}")
        raise typer.Exit(1)
