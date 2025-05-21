# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

import uvicorn
from mcp.server import Server, ToolRegistry

from aipseo.agent_tools import (
    get_url_lookup,
    get_spam_score,
    list_market_opportunities,
    get_wallet_balance,
)

# Create a ToolRegistry instance
registry = ToolRegistry()

# Register the functions from agent_tools
registry.register(get_url_lookup)
registry.register(get_spam_score)
registry.register(list_market_opportunities)
registry.register(get_wallet_balance)

# Create a Server instance
mcp_server = Server(registry=registry)

# Main execution block to run the server
if __name__ == "__main__":
    uvicorn.run("aipseo.mcp_server:mcp_server", host="0.0.0.0", port=8000, reload=True)
