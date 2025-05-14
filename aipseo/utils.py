# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Utility functions for the AIPSEO CLI."""

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

# API Base URL - replace with actual URL when available
API_BASE_URL = "https://api.aipseo.com/v1"

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


def format_output(data: Dict[str, Any], format_type: str = "pretty") -> None:
    """Format and print data based on the specified format."""
    if format_type.lower() == "json":
        console.print(json.dumps(data, indent=2))
    else:  # pretty
        if "error" in data:
            ERROR_CONSOLE.print(f"Error: {data['error']}")
            sys.exit(1)

        # Create a table for the data
        table = Table(title="AIPSEO Results")

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
    """Make a request to the AIPSEO API."""
    if params is None:
        params = {}

    # Mock implementations for wallet and marketplace endpoints
    if endpoint == "wallet/create":
        return {
            "wallet_id": f"w_{generate_tool_id(16)}",
            "deposit_address": f"aipseo_{generate_tool_id(24)}",
        }
    elif endpoint == "wallet/balance":
        wallet_id = params.get("wallet_id", "")
        return {
            "wallet_id": wallet_id,
            "tokens": random.randint(100, 5000),
            "usd": random.uniform(10.0, 500.0),
        }
    elif endpoint == "wallet/deposit":
        wallet_id = params.get("wallet_id", "")
        amount = params.get("amount_usd", 100.0)
        return {
            "wallet_id": wallet_id,
            "amount_usd": amount,
            "stripe_checkout_url": "https://checkout.stripe.com/pay/mock_session_id",
        }
    elif endpoint == "wallet/withdraw":
        wallet_id = params.get("wallet_id", "")
        amount = params.get("amount_usd", 50.0)
        dest = params.get("dest", "example_bank_account")
        return {
            "wallet_id": wallet_id,
            "amount_usd": amount,
            "destination": dest,
            "status": "processing",
            "transaction_id": f"tx_{generate_tool_id(16)}",
        }
    elif endpoint == "marketplace/search":
        # Generate mock listings based on search criteria
        dr_min = params.get("dr_min", 20)
        price_max = params.get("price_max", 100.0)

        listings = []
        for _ in range(random.randint(3, 8)):
            dr = dr_min + random.randint(0, 30)
            price = min(price_max or 1000.0, dr * random.uniform(0.5, 1.5))
            listings.append(
                {
                    "listing_id": f"lst_{generate_tool_id(8)}",
                    "source_url": (
                        f"https://example{random.randint(1, 999)}.com/"
                        f"blog/post-{random.randint(1, 100)}"
                    ),
                    "dr_bucket": dr,
                    "price_usd": price,
                    "anchor": f"sample anchor text {random.randint(1, 100)}",
                }
            )
        return listings
    elif endpoint == "marketplace/buy":
        listing_id = params.get("listing_id", f"lst_{generate_tool_id(8)}")
        return {
            "status": "success",
            "escrow_id": f"esc_{generate_tool_id(12)}",
            "listing_id": listing_id,
        }
    elif endpoint == "marketplace/list":
        source_url = params.get("source_url", "https://example.com/blog")
        target_url = params.get("target_url", "https://target.com")
        price = params.get("price_usd", 50.0)
        return {
            "listing_id": f"lst_{generate_tool_id(8)}",
            "source_url": source_url,
            "target_url": target_url,
            "price_usd": price,
            "status": "active",
        }
    # Handle original endpoints
    elif endpoint == "lookup":
        url = params.get("url", "example.com")
        # Create a dummy response that looks like it came from an API
        return {
            "url": url,
            "domain_authority": 45,
            "page_authority": 38,
            "backlinks": 234,
            "referring_domains": 56,
            "indexed_pages": 1243,
            "last_crawled": "2023-05-10T14:32:45Z",
        }
    elif endpoint == "spam-score":
        url = params.get("url", "example.com")
        score = random.randint(1, 10)
        return {
            "url": url,
            "spam_score": score,
            "risk_level": "Low" if score < 4 else "Medium" if score < 7 else "High",
            "spam_flags": random.randint(0, 5),
            "last_checked": "2023-05-12T09:15:22Z",
        }
    else:
        return {"error": f"Unknown endpoint: {endpoint}"}

    # Real implementation would be something like this:
    """
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=params)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    """
