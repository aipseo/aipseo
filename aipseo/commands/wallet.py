# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Wallet operations for the aipseo CLI."""

import getpass
import os

import typer

from aipseo.utils import (
    DEFAULT_WALLET_PATH,
    ERROR_CONSOLE,
    console,
    make_api_request,
    open_browser,
    read_wallet_file,
    write_wallet_file,
)

wallet_app = typer.Typer(help="Wallet operations for aipseo marketplace")


@wallet_app.command("create")
def create_wallet(
    name: str = typer.Option("default", "--name", "-n", help="Wallet name identifier"),
    output: str = typer.Option(
        DEFAULT_WALLET_PATH, "--output", "-o", help="Output wallet file path"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing wallet file"
    ),
):
    """Create a new wallet for aipseo marketplace operations."""
    if os.path.exists(output) and not force:
        ERROR_CONSOLE.print(
            f"Error: Wallet file '{output}' already exists. Use --force to overwrite."
        )
        raise typer.Exit(1)

    # Get password to encrypt wallet file
    password = getpass.getpass("Enter a password to secure your wallet: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if password != confirm_password:
        ERROR_CONSOLE.print("Error: Passwords do not match.")
        raise typer.Exit(1)

    if len(password) < 8:
        ERROR_CONSOLE.print("Error: Password must be at least 8 characters long.")
        raise typer.Exit(1)

    # Call API to create wallet
    result = make_api_request("wallet/create", method="POST", params={"name": name})

    if isinstance(result, dict) and "error" in result:
        ERROR_CONSOLE.print(f"Error creating wallet: {result['error']}")
        raise typer.Exit(1)

    if not isinstance(result, dict):
        ERROR_CONSOLE.print("Error: Unexpected response format from server")
        raise typer.Exit(1)

    wallet_id = result.get("wallet_id", "")
    deposit_address = result.get("deposit_address", "")

    # Save wallet ID to encrypted file
    write_wallet_file(output, wallet_id, password)

    # Display success message
    console.print("\n✅ [bold green]Wallet created successfully![/bold green]")
    console.print(f"Wallet ID: [cyan]{wallet_id}[/cyan]")
    console.print(f"Deposit Address: [cyan]{deposit_address}[/cyan]")
    console.print(
        f"\nUse [bold]aipseo wallet balance --wallet {output}[/bold] "
        f"to check your balance."
    )
    console.print(
        f"Use [bold]aipseo wallet deposit --wallet {output}[/bold] to add funds."
    )


@wallet_app.command("balance")
def check_balance(
    wallet: str = typer.Option(
        DEFAULT_WALLET_PATH, "--wallet", "-w", help="Path to wallet file"
    )
):
    """Check your wallet balance."""
    if not os.path.exists(wallet):
        ERROR_CONSOLE.print(f"Error: Wallet file '{wallet}' not found.")
        raise typer.Exit(1)

    # Get password to decrypt wallet file
    password = getpass.getpass("Enter your wallet password: ")

    # Read and decrypt wallet file
    wallet_data = read_wallet_file(wallet, password)
    wallet_id = wallet_data.get("wallet_id")

    # Call API to get balance
    result = make_api_request("wallet/balance", params={"wallet_id": wallet_id})

    if isinstance(result, dict) and "error" in result:
        ERROR_CONSOLE.print(f"Error checking balance: {result['error']}")
        raise typer.Exit(1)

    if not isinstance(result, dict):
        ERROR_CONSOLE.print("Error: Unexpected response format from server")
        raise typer.Exit(1)

    # Display balance
    console.print("\n[bold]Wallet Balance[/bold]")
    console.print(f"Tokens: [cyan]{result.get('tokens', 0):,}[/cyan]")
    console.print(f"USD Value: [green]${result.get('usd', 0.0):.2f}[/green]")


@wallet_app.command("deposit")
def deposit_funds(
    wallet: str = typer.Option(
        DEFAULT_WALLET_PATH, "--wallet", "-w", help="Path to wallet file"
    ),
    amount: float = typer.Option(
        ..., "--amount", "-a", help="Amount in USD to deposit"
    ),
):
    """Deposit funds to your wallet via Stripe checkout."""
    if not os.path.exists(wallet):
        ERROR_CONSOLE.print(f"Error: Wallet file '{wallet}' not found.")
        raise typer.Exit(1)

    if amount <= 0:
        ERROR_CONSOLE.print("Error: Deposit amount must be greater than zero.")
        raise typer.Exit(1)

    # Get password to decrypt wallet file
    password = getpass.getpass("Enter your wallet password: ")

    # Read and decrypt wallet file
    wallet_data = read_wallet_file(wallet, password)
    wallet_id = wallet_data.get("wallet_id")

    # Call API to get deposit URL
    result = make_api_request(
        "wallet/deposit",
        method="POST",
        params={"wallet_id": wallet_id, "amount_usd": amount},
    )

    if isinstance(result, dict) and "error" in result:
        ERROR_CONSOLE.print(f"Error initiating deposit: {result['error']}")
        raise typer.Exit(1)

    if not isinstance(result, dict):
        ERROR_CONSOLE.print("Error: Unexpected response format from server")
        raise typer.Exit(1)

    checkout_url = result.get("stripe_checkout_url", "")

    # Display info and open browser
    console.print(
        f"\n[bold green]Opening Stripe checkout to deposit ${amount:.2f}[/bold green]"
    )
    console.print("Complete the payment in your browser to add funds to your wallet.")

    if checkout_url:
        console.print(f"Checkout URL: [link={checkout_url}]{checkout_url}[/link]")
        # Open browser for payment
        open_browser(checkout_url)
    else:
        ERROR_CONSOLE.print("Error: No checkout URL was provided by the server")
        raise typer.Exit(1)


@wallet_app.command("withdraw")
def withdraw_funds(
    wallet: str = typer.Option(
        DEFAULT_WALLET_PATH, "--wallet", "-w", help="Path to wallet file"
    ),
    amount: float = typer.Option(
        ..., "--amount", "-a", help="Amount in USD to withdraw"
    ),
    dest: str = typer.Option(
        ..., "--dest", "-d", help="Destination (bank or crypto address)"
    ),
):
    """Withdraw funds from your wallet."""
    if not os.path.exists(wallet):
        ERROR_CONSOLE.print(f"Error: Wallet file '{wallet}' not found.")
        raise typer.Exit(1)

    if amount <= 0:
        ERROR_CONSOLE.print("Error: Withdrawal amount must be greater than zero.")
        raise typer.Exit(1)

    # Get password to decrypt wallet file
    password = getpass.getpass("Enter your wallet password: ")

    # Read and decrypt wallet file
    wallet_data = read_wallet_file(wallet, password)
    wallet_id = wallet_data.get("wallet_id")

    # Call API to initiate withdrawal
    result = make_api_request(
        "wallet/withdraw",
        method="POST",
        params={"wallet_id": wallet_id, "amount_usd": amount, "dest": dest},
    )

    if isinstance(result, dict) and "error" in result:
        ERROR_CONSOLE.print(f"Error initiating withdrawal: {result['error']}")
        raise typer.Exit(1)

    if not isinstance(result, dict):
        ERROR_CONSOLE.print("Error: Unexpected response format from server")
        raise typer.Exit(1)

    # Display success message
    console.print("\n[bold green]Withdrawal initiated![/bold green]")
    console.print(f"Status: [cyan]{result.get('status', 'pending')}[/cyan]")
    console.print(
        f"Transaction ID: [cyan]{result.get('transaction_id', 'unknown')}[/cyan]"
    )
    console.print("\nPlease allow 1-2 business days for processing.")
