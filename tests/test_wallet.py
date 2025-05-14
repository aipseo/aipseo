# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Tests for the wallet commands."""

import getpass
import os
import tempfile
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from aipseo.cli import app


@pytest.fixture
def runner():
    """Return a CLI runner for testing."""
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_password_input(monkeypatch):
    """Mock getpass to return a standard password, apply to all tests."""
    # Using monkeypatch instead of patch for reliability
    monkeypatch.setattr("getpass.getpass", lambda prompt="": "testpassword123")


@pytest.fixture
def temp_wallet_file():
    """Create a temporary wallet file path for testing."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp:
        temp_path = temp.name

    try:
        # Just return the path, we'll mock the file operations
        yield temp_path
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@patch("aipseo.commands.wallet.make_api_request")
@patch("aipseo.commands.wallet.write_wallet_file")
@patch("aipseo.utils.CRYPTO_AVAILABLE", True)
@patch("os.path.exists", return_value=False)
def test_wallet_create(mock_exists, mock_write, mock_api, runner, temp_wallet_file):
    """Test the wallet create command."""
    # Verify password mock is working
    assert getpass.getpass("anything") == "testpassword123"

    # Mock API response
    mock_api.return_value = {
        "wallet_id": "w_test123456789",
        "deposit_address": "aipseo_address123456789",
    }

    # Test the command
    result = runner.invoke(
        app, ["wallet", "create", "--name", "test", "--output", temp_wallet_file]
    )

    # Debug output
    if result.exit_code != 0:
        print(f"Exit code: {result.exit_code}")
        print(f"Exception: {result.exception}")
        print(f"Output: {result.stdout}")

    # Check result
    assert result.exit_code == 0
    assert "Wallet created successfully" in result.stdout
    assert "Wallet ID:" in result.stdout
    assert "Deposit Address:" in result.stdout

    # Verify the API was called correctly
    mock_api.assert_called_once_with(
        "wallet/create", method="POST", params={"name": "test"}
    )

    # Verify the wallet write function was called
    mock_write.assert_called_once()


@patch("aipseo.commands.wallet.make_api_request")
@patch("aipseo.commands.wallet.read_wallet_file")
@patch("aipseo.utils.CRYPTO_AVAILABLE", True)
@patch("os.path.exists", return_value=True)
def test_wallet_balance(mock_exists, mock_read, mock_api, runner, temp_wallet_file):
    """Test the wallet balance command."""
    # Verify password mock is working
    assert getpass.getpass("anything") == "testpassword123"

    # Set up mock returns
    mock_read.return_value = {"wallet_id": "w_test123456789"}
    mock_api.return_value = {
        "wallet_id": "w_test123456789",
        "tokens": 1500,
        "usd": 150.0,
    }

    # Test the command
    result = runner.invoke(app, ["wallet", "balance", "--wallet", temp_wallet_file])

    # Debug output
    if result.exit_code != 0:
        print(f"Exit code: {result.exit_code}")
        print(f"Exception: {result.exception}")
        print(f"Output: {result.stdout}")

    # Check result
    assert result.exit_code == 0
    assert "Wallet Balance" in result.stdout
    assert "Tokens:" in result.stdout
    assert "USD Value:" in result.stdout
    # Just make sure there's output
    assert len(result.stdout) > 0
    # Ensure dollar sign is in output
    assert "$" in result.stdout

    # Verify the API was called correctly
    mock_api.assert_called_once_with(
        "wallet/balance", params={"wallet_id": "w_test123456789"}
    )


@patch("aipseo.commands.wallet.make_api_request")
@patch("aipseo.commands.wallet.read_wallet_file")
@patch("aipseo.commands.wallet.open_browser")
@patch("aipseo.utils.CRYPTO_AVAILABLE", True)
@patch("os.path.exists", return_value=True)
def test_wallet_deposit(
    mock_exists, mock_browser, mock_read, mock_api, runner, temp_wallet_file
):
    """Test the wallet deposit command."""
    # Verify password mock is working
    assert getpass.getpass("anything") == "testpassword123"

    # Set up mock returns
    mock_read.return_value = {"wallet_id": "w_test123456789"}
    checkout_url = "https://checkout.stripe.com/pay/mock_session_id"
    mock_api.return_value = {
        "wallet_id": "w_test123456789",
        "amount_usd": 100.0,
        "stripe_checkout_url": checkout_url,
    }

    # Test the command
    result = runner.invoke(
        app, ["wallet", "deposit", "--wallet", temp_wallet_file, "--amount", "100"]
    )

    # Debug output
    if result.exit_code != 0:
        print(f"Exit code: {result.exit_code}")
        print(f"Exception: {result.exception}")
        print(f"Output: {result.stdout}")

    # Check result
    assert result.exit_code == 0
    assert "Opening Stripe checkout" in result.stdout
    assert checkout_url in result.stdout

    # Verify the API was called correctly
    mock_api.assert_called_once_with(
        "wallet/deposit",
        method="POST",
        params={"wallet_id": "w_test123456789", "amount_usd": 100.0},
    )

    # Verify the browser was opened with the correct URL
    mock_browser.assert_called_once_with(checkout_url)


@patch("aipseo.commands.wallet.make_api_request")
@patch("aipseo.commands.wallet.read_wallet_file")
@patch("aipseo.utils.CRYPTO_AVAILABLE", True)
@patch("os.path.exists", return_value=True)
def test_wallet_withdraw(mock_exists, mock_read, mock_api, runner, temp_wallet_file):
    """Test the wallet withdraw command."""
    # Verify password mock is working
    assert getpass.getpass("anything") == "testpassword123"

    # Set up mock returns
    mock_read.return_value = {"wallet_id": "w_test123456789"}
    mock_api.return_value = {
        "wallet_id": "w_test123456789",
        "amount_usd": 50.0,
        "destination": "bank_account123",
        "status": "processing",
        "transaction_id": "tx_12345678",
    }

    # Test the command
    result = runner.invoke(
        app,
        [
            "wallet",
            "withdraw",
            "--wallet",
            temp_wallet_file,
            "--amount",
            "50",
            "--dest",
            "bank_account123",
        ],
    )

    # Debug output
    if result.exit_code != 0:
        print(f"Exit code: {result.exit_code}")
        print(f"Exception: {result.exception}")
        print(f"Output: {result.stdout}")

    # Check result
    assert result.exit_code == 0
    assert "Withdrawal initiated" in result.stdout
    assert "Status:" in result.stdout
    assert "Transaction ID:" in result.stdout

    # Verify the API was called correctly
    mock_api.assert_called_once_with(
        "wallet/withdraw",
        method="POST",
        params={
            "wallet_id": "w_test123456789",
            "amount_usd": 50.0,
            "dest": "bank_account123",
        },
    )
