# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

import unittest
from unittest.mock import patch, MagicMock

# Functions to test
from aipseo.agent_tools import (
    get_url_lookup,
    get_spam_score,
    list_market_opportunities,
    get_wallet_balance,
)
# To help with type hinting the mock APIClient instance
from aipseo.api import APIClient


class TestAgentTools(unittest.TestCase):

    @patch('aipseo.agent_tools.APIClient')
    def test_get_url_lookup(self, MockAPIClient: MagicMock) -> None:
        # Setup mock instance and its method's return value
        mock_api_instance = MockAPIClient.return_value
        expected_data = {"url": "example.com", "data": "some_lookup_data"}
        mock_api_instance.lookup.return_value = expected_data

        # Call the function
        result = get_url_lookup(url="example.com")

        # Assertions
        MockAPIClient.assert_called_once_with()  # Ensure APIClient was instantiated
        mock_api_instance.lookup.assert_called_once_with(url="example.com")
        self.assertEqual(result, expected_data)

    @patch('aipseo.agent_tools.APIClient')
    def test_get_spam_score(self, MockAPIClient: MagicMock) -> None:
        # Setup mock instance
        mock_api_instance = MockAPIClient.return_value
        expected_data = {"url": "example.com", "score": 10}
        mock_api_instance.spam_score.return_value = expected_data

        # Call the function
        result = get_spam_score(url="example.com")

        # Assertions
        MockAPIClient.assert_called_once_with()
        mock_api_instance.spam_score.assert_called_once_with(url="example.com")
        self.assertEqual(result, expected_data)

    @patch('aipseo.agent_tools.APIClient')
    def test_list_market_opportunities(self, MockAPIClient: MagicMock) -> None:
        # Setup mock instance
        mock_api_instance = MockAPIClient.return_value
        expected_data = [{"id": "1", "dr": 70, "price": 90, "topic": "tech"}]
        mock_api_instance.search_marketplace.return_value = expected_data

        # Call the function
        result = list_market_opportunities(dr_min=70, price_max=100.0, topic="tech")

        # Assertions
        MockAPIClient.assert_called_once_with()
        mock_api_instance.search_marketplace.assert_called_once_with(
            dr_min=70, price_max=100.0, topic="tech"
        )
        self.assertEqual(result, expected_data)

    @patch('aipseo.agent_tools.APIClient')
    def test_list_market_opportunities_no_args(self, MockAPIClient: MagicMock) -> None:
        # Setup mock instance
        mock_api_instance = MockAPIClient.return_value
        expected_data = [{"id": "2", "dr": 50}]
        mock_api_instance.search_marketplace.return_value = expected_data

        # Call the function
        result = list_market_opportunities()

        # Assertions
        MockAPIClient.assert_called_once_with()
        mock_api_instance.search_marketplace.assert_called_once_with(
            dr_min=None, price_max=None, topic=None
        )
        self.assertEqual(result, expected_data)
        
    @patch('aipseo.agent_tools.APIClient')
    def test_list_market_opportunities_some_args(self, MockAPIClient: MagicMock) -> None:
        # Setup mock instance
        mock_api_instance = MockAPIClient.return_value
        expected_data = [{"id": "3", "dr": 60, "topic": "finance"}]
        mock_api_instance.search_marketplace.return_value = expected_data

        # Call the function
        result = list_market_opportunities(dr_min=60, topic="finance")

        # Assertions
        MockAPIClient.assert_called_once_with()
        mock_api_instance.search_marketplace.assert_called_once_with(
            dr_min=60, price_max=None, topic="finance"
        )
        self.assertEqual(result, expected_data)

    @patch('aipseo.agent_tools.APIClient')
    def test_get_wallet_balance(self, MockAPIClient: MagicMock) -> None:
        # Setup mock instance
        mock_api_instance = MockAPIClient.return_value
        expected_data = {"wallet_id": "wallet123", "balance": 500}
        mock_api_instance.get_balance.return_value = expected_data

        # Call the function
        result = get_wallet_balance(wallet_id="wallet123")

        # Assertions
        MockAPIClient.assert_called_once_with()
        mock_api_instance.get_balance.assert_called_once_with(wallet_id="wallet123")
        self.assertEqual(result, expected_data)


if __name__ == '__main__':
    unittest.main()
