# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Tests for the marketplace commands."""

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


@patch("aipseo.commands.market.make_api_request")
@patch("aipseo.commands.market.display_marketplace_listings")
def test_market_list(mock_display, mock_api, runner):
    """Test the market list command."""
    mock_listings = [
        {
            "listing_id": "lst_12345678",
            "source_url": "https://example1.com/blog/post-1",
            "dr_bucket": 45,
            "price_usd": 50.0,
            "anchor": "sample anchor text 1",
        },
        {
            "listing_id": "lst_87654321",
            "source_url": "https://example2.com/blog/post-2",
            "dr_bucket": 35,
            "price_usd": 40.0,
            "anchor": "sample anchor text 2",
        },
    ]

    # Set up mock return
    mock_api.return_value = mock_listings

    # Test the command with no parameters
    result = runner.invoke(app, ["market", "list"])

    # Debug output
    if result.exit_code != 0:
        print(f"Exit code: {result.exit_code}")
        print(f"Exception: {result.exception}")
        print(f"Output: {result.stdout}")

    # Check basic result
    assert result.exit_code == 0

    # Verify the function calls for no parameters
    mock_api.assert_called_with("marketplace/search", params={})
    mock_display.assert_called_with(mock_listings)

    # Reset mock to test with parameters
    mock_api.reset_mock()
    mock_display.reset_mock()

    # Test with parameters
    result = runner.invoke(
        app, ["market", "list", "--dr-min", "40", "--price-max", "60"]
    )

    # Verify the function calls with parameters
    mock_api.assert_called_with(
        "marketplace/search", params={"dr_min": 40, "price_max": 60}
    )
    mock_display.assert_called_with(mock_listings)


@patch("aipseo.commands.market.make_api_request")
@patch("aipseo.commands.market.read_wallet_file")
@patch("aipseo.utils.CRYPTO_AVAILABLE", True)
@patch("os.path.exists", return_value=True)
def test_market_buy(mock_exists, mock_read, mock_api, runner, temp_wallet_file):
    """Test the market buy command."""
    # Verify password mock is working
    import getpass

    assert getpass.getpass("anything") == "testpassword123"

    # Set up mock returns
    mock_read.return_value = {"wallet_id": "w_test123456789"}
    mock_api.return_value = {
        "status": "success",
        "escrow_id": "esc_123456789012",
        "listing_id": "lst_12345678",
    }

    # Test the command
    result = runner.invoke(
        app,
        ["market", "buy", "--wallet", temp_wallet_file, "--listing-id", "lst_12345678"],
    )

    # Debug output
    if result.exit_code != 0:
        print(f"Exit code: {result.exit_code}")
        print(f"Exception: {result.exception}")
        print(f"Output: {result.stdout}")

    # Check result
    assert result.exit_code == 0
    assert "Purchase successful" in result.stdout
    assert "success" in result.stdout
    assert "Escrow ID:" in result.stdout

    # Verify the API was called correctly
    mock_api.assert_called_once_with(
        "marketplace/buy",
        method="POST",
        params={"wallet_id": "w_test123456789", "listing_id": "lst_12345678"},
    )


@patch("aipseo.commands.market.make_api_request")
@patch("aipseo.commands.market.read_wallet_file")
@patch("aipseo.utils.CRYPTO_AVAILABLE", True)
@patch("os.path.exists", return_value=True)
def test_market_sell(mock_exists, mock_read, mock_api, runner, temp_wallet_file):
    """Test the market sell command."""
    # Verify password mock is working
    import getpass

    assert getpass.getpass("anything") == "testpassword123"

    # Set up mock returns
    mock_read.return_value = {"wallet_id": "w_test123456789"}
    mock_api.return_value = {
        "listing_id": "lst_87654321",
        "source_url": "https://example.com/blog/post",
        "target_url": "https://target.com/page",
        "price_usd": 75.0,
        "status": "active",
    }

    # Test the command
    result = runner.invoke(
        app,
        [
            "market",
            "sell",
            "--wallet",
            temp_wallet_file,
            "--source-url",
            "https://example.com/blog/post",
            "--target-url",
            "https://target.com/page",
            "--price",
            "75",
            "--anchor",
            "click here to visit",
            "--rel",
            "nofollow",
        ],
    )

    # Debug output
    if result.exit_code != 0:
        print(f"Exit code: {result.exit_code}")
        print(f"Exception: {result.exception}")
        print(f"Output: {result.stdout}")

    # Check result
    assert result.exit_code == 0
    assert "Backlink listed for sale" in result.stdout
    assert "Listing ID:" in result.stdout
    assert "https://example.com/blog/post" in result.stdout
    assert "https://target.com/page" in result.stdout
    assert "$75.00" in result.stdout
    assert "click here to visit" in result.stdout
    assert "nofollow" in result.stdout

    # Verify the API was called correctly
    mock_api.assert_called_once_with(
        "marketplace/list",
        method="POST",
        params={
            "wallet_id": "w_test123456789",
            "source_url": "https://example.com/blog/post",
            "target_url": "https://target.com/page",
            "price_usd": 75.0,
            "anchor": "click here to visit",
            "rel": "nofollow",
        },
    )
