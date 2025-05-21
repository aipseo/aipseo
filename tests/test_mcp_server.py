# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

import unittest
from mcp.server import ToolRegistry

# Expected tools that should be registered (imported for clarity/reference)
from aipseo.agent_tools import (
    get_url_lookup,
    get_spam_score,
    list_market_opportunities,
    get_wallet_balance
)

# The registry instance from mcp_server.py
# This relies on aipseo.mcp_server.py defining 'registry' at the module level
try:
    from aipseo.mcp_server import registry as mcp_server_registry
except ImportError as e:
    # This allows tests to be discovered and run, even if mcp_server itself has issues.
    # The test method will then fail gracefully.
    mcp_server_registry = None 
    print(f"Could not import mcp_server_registry: {e}")


class TestMCPServer(unittest.TestCase):

    def test_tools_are_registered(self):
        self.assertIsNotNone(mcp_server_registry, 
                             "MCP server registry (from aipseo.mcp_server) could not be imported. "
                             "This may indicate an issue with aipseo/mcp_server.py or its dependencies.")
        
        self.assertIsInstance(mcp_server_registry, ToolRegistry, 
                              "The imported 'registry' from aipseo.mcp_server is not a ToolRegistry instance.")

        expected_tool_names = sorted([ # Use sorted list for consistent comparison
            "get_url_lookup",
            "get_spam_score",
            "list_market_opportunities",
            "get_wallet_balance",
        ])
        
        # mcp_server_registry.get_tools() yields (name, callable) tuples
        # We only need the names for this test.
        registered_tool_names = sorted([tool_name for tool_name, _ in mcp_server_registry.get_tools()])

        # Check if all expected tools are registered
        for tool_name in expected_tool_names:
            self.assertIn(tool_name, registered_tool_names, 
                          f"Expected tool '{tool_name}' not found in MCP server registry.")
        
        # Check if the number of registered tools matches the number of expected tools
        # This ensures no unexpected tools are registered.
        self.assertEqual(len(registered_tool_names), len(expected_tool_names),
                         f"Mismatch in the number of registered tools. "
                         f"Expected: {len(expected_tool_names)}, Found: {len(registered_tool_names)}. "
                         f"Registered tools: {registered_tool_names}")


if __name__ == '__main__':
    unittest.main()
