# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Marketplace operations for the aipseo CLI."""

import getpass
import os
from typing import Optional

import typer

from aipseo.utils import (
    DEFAULT_WALLET_PATH,
    ERROR_CONSOLE,
    console,
    display_marketplace_listings,
    make_api_request,
    read_wallet_file,
)

market_app = typer.Typer(help="Marketplace operations for aipseo")


@market_app.command("list")
def list_marketplace(
    dr_min: Optional[int] = typer.Option(
        None, "--dr-min", help="Minimum Domain Rating to filter by"
    ),
    price_max: Optional[float] = typer.Option(
        None, "--price-max", help="Maximum price in USD to filter by"
    ),
    topic: Optional[str] = typer.Option(
        None, "--topic", "-t", help="Topic category to filter by"
    ),
):
    """List available backlink opportunities in the marketplace."""
    # Build search params
    params = {}
    if dr_min is not None:
        params["dr_min"] = dr_min
    if price_max is not None:
        params["price_max"] = price_max
    if topic is not None:
        params["topic"] = topic

    # Call API to search listings
    result = make_api_request("marketplace/search", params=params)

    if isinstance(result, dict) and "error" in result:
        ERROR_CONSOLE.print(f"Error searching marketplace: {result['error']}")
        raise typer.Exit(1)

    # Display listings - make sure we have a list of listings
    listings = result if isinstance(result, list) else []
    display_marketplace_listings(listings)

    # Show tip for purchase
    console.print(
        "\n[i]To buy a listing, use 'aipseo market buy "
        "--listing-id <ID> --wallet <path>'[/i]"
    )


@market_app.command("buy")
def buy_listing(
    wallet: str = typer.Option(
        DEFAULT_WALLET_PATH, "--wallet", "-w", help="Path to wallet file"
    ),
    listing_id: str = typer.Option(
        ..., "--listing-id", "-l", help="ID of the listing to purchase"
    ),
):
    """Purchase a backlink from the marketplace."""
    if not os.path.exists(wallet):
        ERROR_CONSOLE.print(f"Error: Wallet file '{wallet}' not found.")
        raise typer.Exit(1)

    # Get password to decrypt wallet file
    password = getpass.getpass("Enter your wallet password: ")

    # Read and decrypt wallet file
    wallet_data = read_wallet_file(wallet, password)
    wallet_id = wallet_data.get("wallet_id")

    # Call API to purchase listing
    result = make_api_request(
        "marketplace/buy",
        method="POST",
        params={"wallet_id": wallet_id, "listing_id": listing_id},
    )

    if isinstance(result, dict) and "error" in result:
        ERROR_CONSOLE.print(f"Error purchasing listing: {result['error']}")
        raise typer.Exit(1)

    if not isinstance(result, dict):
        ERROR_CONSOLE.print("Error: Unexpected response format from server")
        raise typer.Exit(1)

    # Display success message
    console.print("\n[bold green]Purchase successful![/bold green]")
    console.print(f"Status: [cyan]{result.get('status', 'pending')}[/cyan]")
    console.print(f"Escrow ID: [cyan]{result.get('escrow_id', 'unknown')}[/cyan]")
    console.print(
        "\nThe seller will be notified and the link will be placed " "within 72 hours."
    )
    console.print("Funds are held in escrow until the link placement is verified.")


@market_app.command("sell")
def sell_backlink(
    wallet: str = typer.Option(
        DEFAULT_WALLET_PATH, "--wallet", "-w", help="Path to wallet file"
    ),
    source_url: str = typer.Option(
        ..., "--source-url", "-s", help="URL of the page where the link will be placed"
    ),
    target_url: str = typer.Option(
        ..., "--target-url", "-t", help="URL that will be linked to"
    ),
    price: float = typer.Option(
        ..., "--price", "-p", help="Price in USD for the backlink"
    ),
    anchor: str = typer.Option(..., "--anchor", "-a", help="Anchor text for the link"),
    rel: Optional[str] = typer.Option(
        None,
        "--rel",
        "-r",
        help="Optional rel attribute for the link (e.g., 'nofollow')",
    ),
):
    """List a backlink for sale in the marketplace."""
    if not os.path.exists(wallet):
        ERROR_CONSOLE.print(f"Error: Wallet file '{wallet}' not found.")
        raise typer.Exit(1)

    if price <= 0:
        ERROR_CONSOLE.print("Error: Price must be greater than zero.")
        raise typer.Exit(1)

    # Get password to decrypt wallet file
    password = getpass.getpass("Enter your wallet password: ")

    # Read and decrypt wallet file
    wallet_data = read_wallet_file(wallet, password)
    wallet_id = wallet_data.get("wallet_id")

    # Build params
    params = {
        "wallet_id": wallet_id,
        "source_url": source_url,
        "target_url": target_url,
        "price_usd": price,
        "anchor": anchor,
    }

    if rel:
        params["rel"] = rel

    # Call API to list backlink
    result = make_api_request("marketplace/list", method="POST", params=params)

    if isinstance(result, dict) and "error" in result:
        ERROR_CONSOLE.print(f"Error listing backlink: {result['error']}")
        raise typer.Exit(1)

    if not isinstance(result, dict):
        ERROR_CONSOLE.print("Error: Unexpected response format from server")
        raise typer.Exit(1)

    # Display success message
    console.print("\n[bold green]Backlink listed for sale![/bold green]")
    console.print(f"Listing ID: [cyan]{result.get('listing_id', 'unknown')}[/cyan]")
    console.print(f"Source URL: [cyan]{source_url}[/cyan]")
    console.print(f"Target URL: [cyan]{target_url}[/cyan]")
    console.print(f"Price: [green]${price:.2f}[/green]")
    console.print(f"Anchor Text: [magenta]{anchor}[/magenta]")

    if rel:
        console.print(f"Rel Attribute: [cyan]{rel}[/cyan]")

    console.print("\nYour listing is now active in the aipseo Marketplace.")
