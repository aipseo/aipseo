# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

import unittest
import inspect # For getting docstrings consistently
from aipseo.toolspec import generate_openai_spec

# Import agent tools to compare docstrings and parameter details
from aipseo.agent_tools import (
    get_url_lookup,
    get_spam_score,
    list_market_opportunities,
    get_wallet_balance,
)

class TestToolSpecGeneration(unittest.TestCase):

    def setUp(self):
        # Generate the specs once for all tests in this class
        self.all_specs = generate_openai_spec()
        self.generated_tool_names = [spec["name"] for spec in self.all_specs]

    def find_schema_by_name(self, name: str):
        for spec in self.all_specs:
            if spec["name"] == name:
                return spec
        return None

    def test_generate_openai_spec_includes_agent_tools(self):
        expected_agent_tool_names = [
            "get_url_lookup",
            "get_spam_score",
            "list_market_opportunities",
            "get_wallet_balance",
        ]
        for name in expected_agent_tool_names:
            self.assertIn(name, self.generated_tool_names,
                          f"Agent tool '{name}' not found in toolspec output.")

    def test_toolspec_includes_cli_commands(self):
        # Check for a few representative CLI commands
        # These names are based on the Typer command structure and toolspec.py naming logic
        expected_cli_tool_names = ["lookup", "spam-score", "wallet_create", "market_list"]
        # Also check for a subcommand to ensure group command processing works
        self.assertTrue(len(self.generated_tool_names) > len(expected_cli_tool_names), 
                        "Less tools generated than expected minimum (CLI + agent tools).")

        for name in expected_cli_tool_names:
            self.assertIn(name, self.generated_tool_names,
                          f"Expected CLI command '{name}' not found in toolspec output.")

    def test_get_url_lookup_schema_details(self):
        spec = self.find_schema_by_name("get_url_lookup")
        self.assertIsNotNone(spec, "Schema for 'get_url_lookup' not found.")
        
        # Compare docstring (stripping is important as inspect.getdoc might add newlines)
        self.assertEqual(spec["description"], inspect.getdoc(get_url_lookup).strip(), 
                         "Description mismatch for get_url_lookup")
        
        self.assertIn("url", spec["parameters"]["properties"])
        self.assertEqual(spec["parameters"]["properties"]["url"]["type"], "string")
        self.assertIn("url", spec["parameters"]["required"], "'url' should be a required parameter.")

    def test_get_spam_score_schema_details(self):
        spec = self.find_schema_by_name("get_spam_score")
        self.assertIsNotNone(spec, "Schema for 'get_spam_score' not found.")
        
        self.assertEqual(spec["description"], inspect.getdoc(get_spam_score).strip(),
                         "Description mismatch for get_spam_score")
        
        self.assertIn("url", spec["parameters"]["properties"])
        self.assertEqual(spec["parameters"]["properties"]["url"]["type"], "string")
        self.assertIn("url", spec["parameters"]["required"], "'url' should be a required parameter.")

    def test_list_market_opportunities_schema_details(self):
        spec = self.find_schema_by_name("list_market_opportunities")
        self.assertIsNotNone(spec, "Schema for 'list_market_opportunities' not found.")

        self.assertEqual(spec["description"], inspect.getdoc(list_market_opportunities).strip(), 
                         "Description mismatch for list_market_opportunities")

        params = spec["parameters"]["properties"]
        self.assertIn("dr_min", params)
        self.assertEqual(params["dr_min"]["type"], "integer")
        self.assertIn("price_max", params)
        self.assertEqual(params["price_max"]["type"], "number") # float maps to number
        self.assertIn("topic", params)
        self.assertEqual(params["topic"]["type"], "string")
        
        # Optional parameters should not be in 'required'
        required_params = spec["parameters"].get("required", [])
        self.assertNotIn("dr_min", required_params)
        self.assertNotIn("price_max", required_params)
        self.assertNotIn("topic", required_params)

    def test_get_wallet_balance_schema_details(self):
        spec = self.find_schema_by_name("get_wallet_balance")
        self.assertIsNotNone(spec, "Schema for 'get_wallet_balance' not found.")
        
        self.assertEqual(spec["description"], inspect.getdoc(get_wallet_balance).strip(),
                         "Description mismatch for get_wallet_balance")
        
        self.assertIn("wallet_id", spec["parameters"]["properties"])
        self.assertEqual(spec["parameters"]["properties"]["wallet_id"]["type"], "string")
        self.assertIn("wallet_id", spec["parameters"]["required"], "'wallet_id' should be a required parameter.")

if __name__ == '__main__':
    unittest.main()
