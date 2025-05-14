# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""Tests for the utils module."""

from unittest.mock import mock_open, patch

from aipseo.utils import (
    generate_tool_id,
    make_api_request,
    write_json_file,
)


def test_generate_tool_id():
    """Test that generate_tool_id returns a string of the correct length."""
    tool_id = generate_tool_id()
    assert isinstance(tool_id, str)
    assert len(tool_id) == 12

    # Test custom length
    custom_length = 20
    tool_id = generate_tool_id(custom_length)
    assert len(tool_id) == custom_length


def test_write_and_read_json_file():
    """Test writing and reading a JSON file."""
    # Test data
    test_data = {"test": "data", "number": 42}

    # We need to patch sys.exit to prevent early exit during tests
    with patch("sys.exit") as mock_exit:
        with patch("builtins.open", new_callable=mock_open()) as mock_file:
            with patch("os.path.exists") as mock_exists:
                with patch("os.makedirs") as mock_makedirs:
                    with patch("json.dump") as mock_dump:
                        # First call: file doesn't exist
                        mock_exists.return_value = False
                        result = write_json_file("/fake/path", test_data)
                        assert result is True
                        mock_dump.assert_called_once()

                        # Reset mocks
                        mock_exists.reset_mock()
                        mock_dump.reset_mock()

                        # Second call: file exists and not forcing
                        mock_exists.return_value = True
                        result = write_json_file(
                            "/fake/path", {"new": "data"}, force=False
                        )
                        assert result is False
                        mock_dump.assert_not_called()

                        # Reset mocks
                        mock_exists.reset_mock()
                        mock_dump.reset_mock()

                        # Third call: file exists but forcing
                        mock_exists.return_value = True
                        result = write_json_file(
                            "/fake/path", {"new": "data"}, force=True
                        )
                        assert result is True
                        mock_dump.assert_called_once()


def test_make_api_request_lookup():
    """Test that make_api_request returns expected data for lookup endpoint."""
    result = make_api_request("lookup", params={"url": "example.com"})
    assert isinstance(result, dict)
    assert "url" in result
    assert result["url"] == "example.com"
    assert "domain_authority" in result


def test_make_api_request_spam_score():
    """Test that make_api_request returns expected data for spam-score endpoint."""
    result = make_api_request("spam-score", params={"url": "example.com"})
    assert isinstance(result, dict)
    assert "url" in result
    assert result["url"] == "example.com"
    assert "spam_score" in result
    assert isinstance(result["spam_score"], int)


def test_make_api_request_unknown_endpoint():
    """Test that make_api_request handles unknown endpoints."""
    result = make_api_request("unknown", params={"url": "example.com"})
    assert isinstance(result, dict)
    assert "error" in result
