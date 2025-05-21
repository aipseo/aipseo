# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

import unittest
import asyncio
from mcp.server.fastmcp import FastMCP

# Expected tools that should be registered (imported for clarity/reference)
from aipseo.agent_tools import (
    get_url_lookup,
    get_spam_score,
    list_market_opportunities,
    get_wallet_balance,
    analyze_seo_content, # Added the re-integrated tool
)

# The mcp_server instance from mcp_server.py
try:
    from aipseo.mcp_server import mcp_server
except ImportError as e:
    # This allows tests to be discovered and run, even if mcp_server itself has issues.
    # The test method will then fail gracefully.
    mcp_server = None
    print(f"Could not import mcp_server: {e}")


class TestMCPServer(unittest.TestCase):

    def setUp(self):
        # Create an event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        # Clean up the event loop
        self.loop.close()

    def test_tools_are_registered(self):
        self.assertIsNotNone(mcp_server,
                             "MCP server instance (from aipseo.mcp_server) could not be imported. "
                             "This may indicate an issue with aipseo/mcp_server.py or its dependencies.")

        self.assertIsInstance(mcp_server, FastMCP,
                              "The imported 'mcp_server' from aipseo.mcp_server is not a FastMCP instance.")

        # Define the expected tool names (these should match the @mcp_server.tool() decorated functions)
        expected_tool_names = sorted([
            "analyze_seo_content_tool",
            "get_url_lookup_tool",
            "get_spam_score_tool",
            "list_market_opportunities_tool",
            "get_wallet_balance_tool",
        ])

        # Get the list of registered tools from the FastMCP instance
        # FastMCP exposes tools through list_tools() method
        registered_tools = self.loop.run_until_complete(mcp_server.list_tools())
        registered_tool_names = sorted(tool.name for tool in registered_tools)

        # Check if all expected tools are registered
        for tool_name in expected_tool_names:
             self.assertIn(tool_name, registered_tool_names,
                          f"Expected tool '{tool_name}' not found in MCP server.")

        # Check if the number of registered tools matches the number of expected tools
        self.assertEqual(len(registered_tool_names), len(expected_tool_names),
                         f"Mismatch in the number of registered tools. "
                         f"Expected: {len(expected_tool_names)}, Found: {len(registered_tool_names)}. "
                         f"Registered tools: {registered_tool_names}")


if __name__ == '__main__':
    unittest.main()
