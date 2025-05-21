# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

"""This module implements an MCP (Model Context Protocol) server for aipseo.

It exposes tools that AI agents can use to interact with aipseo's functionalities,
including SEO content analysis, URL lookup, spam score, market opportunities, and wallet balance.
"""

import uvicorn
from mcp.server.fastmcp import FastMCP

# Import tools from agent_tools (including the re-integrated analyze_seo_content)
from aipseo.agent_tools import (
    analyze_seo_content, # Re-integrated tool
    get_url_lookup,
    get_spam_score,
    list_market_opportunities,
    get_wallet_balance,
)

# Create a FastMCP server instance
mcp_server = FastMCP("AIPSEO_MCP_Server")

# Register tools using the FastMCP decorator
@mcp_server.tool()
def analyze_seo_content_tool(content: str, keyword: str) -> str:
    """Analyzes the given content for SEO against a target keyword."""
    return analyze_seo_content(content, keyword)

@mcp_server.tool()
def get_url_lookup_tool(url: str) -> dict:
    """Performs a URL lookup using the APIClient."""
    return get_url_lookup(url)

@mcp_server.tool()
def get_spam_score_tool(url: str) -> dict:
    """Retrieves the spam score for a given URL using the APIClient."""
    return get_spam_score(url)

@mcp_server.tool()
def list_market_opportunities_tool(dr_min: int | None = None, price_max: float | None = None, topic: str | None = None) -> list:
    """Lists market opportunities based on the provided filters using the APIClient."""
    return list_market_opportunities(dr_min, price_max, topic)

@mcp_server.tool()
def get_wallet_balance_tool(wallet_id: str) -> dict:
    """Retrieves the balance for a given wallet ID using the APIClient."""
    return get_wallet_balance(wallet_id)

# Main execution block to run the server
if __name__ == "__main__":
    # Use FastMCP's built-in run method
    mcp_server.run(host="0.0.0.0", port=8000)
