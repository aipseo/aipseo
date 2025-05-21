# aipseo

[![license](https://img.shields.io/github/license/aipseo/aipseo)](license)
[![CI/CD](https://github.com/aipseo/aipseo/actions/workflows/ci.yml/badge.svg)](https://github.com/aipseo/aipseo/actions/workflows/ci.yml)

AI powered SEO! aipseo.com

## Installation

```bash
pip install aipseo
```

## Quick Start

1. Initialize configuration:
```bash
aipseo init
```

2. Create a wallet:
```bash
aipseo wallet create --name mywallet --output .wallet.json
```

3. Explore marketplace:
```bash
aipseo market list
```

## Basic Usage

### Core Commands

```bash
# Initialize configuration
aipseo init

# Validate configuration
aipseo validate

# Look up URL information
aipseo lookup example.com

# Check spam score
aipseo spam-score example.com

# Emit machine-readable function spec for AI integration
aipseo toolspec --format openai
```

### Wallet Commands

```bash
# Create wallet
aipseo wallet create --name mywallet --output .wallet.json

# Check balance
aipseo wallet balance --wallet .wallet.json

# Deposit funds
aipseo wallet deposit --wallet .wallet.json --amount 100

# Withdraw funds
aipseo wallet withdraw --wallet .wallet.json --amount 50 --dest your_bank_account
```

### Marketplace Commands

```bash
# List opportunities
aipseo market list --dr-min 30 --price-max 100

# Buy backlink
aipseo market buy --wallet .wallet.json --listing-id lst_12345678

# Sell backlink
aipseo market sell \
  --wallet .wallet.json \
  --source-url https://yourblog.com/post \
  --target-url https://target.com \
  --price 75 \
  --anchor "useful resource"
```

## AI Agent Integration (MCP Server)

AIPSEO now includes an experimental Model Context Protocol (MCP) server, allowing AI agents and other applications to interact with its capabilities programmatically.

### Available Tools

The following tools are available via the MCP server (see `aipseo/mcp_server.py`):

*   **`analyze_seo_content_tool(content: str, keyword: str) -> str`**:
    *   **Description**: Analyzes a given piece of text content for SEO best practices against a target keyword.
    *   **Parameters**:
        *   `content` (string): The text content to analyze.
        *   `keyword` (string): The target keyword for the analysis.
    *   **Returns**: A string containing an analysis summary and actionable SEO recommendations.

*   **`get_url_lookup_tool(url: str) -> dict`**:
    *   **Description**: Retrieves lookup information (metadata, metrics) for a given URL.
    *   **Parameters**:
        *   `url` (string): The URL to look up.
    *   **Returns**: (dict) A dictionary containing the lookup data for the URL.

*   **`get_spam_score_tool(url: str) -> dict`**:
    *   **Description**: Fetches the spam score for a specified URL.
    *   **Parameters**:
        *   `url` (string): The URL to get the spam score for.
    *   **Returns**: (dict) A dictionary containing the spam score result.

*   **`list_market_opportunities_tool(dr_min: Optional[int] = None, price_max: Optional[float] = None, topic: Optional[str] = None) -> list`**:
    *   **Description**: Lists available backlink opportunities from the marketplace, with optional filters for Domain Rating (DR), maximum price, and topic.
    *   **Parameters**:
        *   `dr_min` (Optional[int]): Minimum Domain Rating.
        *   `price_max` (Optional[float]): Maximum price.
        *   `topic` (Optional[str]): Desired topic for backlinks.
    *   **Returns**: (list) A list of market opportunities matching the criteria.

*   **`get_wallet_balance_tool(wallet_id: str) -> dict`**:
    *   **Description**: Gets the current balance for a specified wallet ID.
    *   **Parameters**:
        *   `wallet_id` (string): The ID of the wallet to get the balance for.
    *   **Returns**: (dict) A dictionary containing the wallet balance result.

### Running the MCP Server

The MCP server is implemented using the latest [FastMCP](https://modelcontextprotocol.io/) API. To run it (for development/testing):

1.  Ensure you have `mcp` and an ASGI server like `uvicorn` installed in your environment.
    ```bash
    pip install "mcp[cli]" uvicorn
    ```
2.  Run the server using uvicorn (or use the built-in run method):
    ```bash
    uvicorn aipseo.mcp_server:mcp_server --host 0.0.0.0 --port 8000
    # or, from within Python:
    # python -m aipseo.mcp_server
    ```
    (You might need to adjust the path or module name depending on your project setup.)

The server uses `FastMCP` for tool registration and serving. AI agents can connect to this server using an MCP client. For more details, see the [Model Context Protocol documentation](https://modelcontextprotocol.io/).

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/aipseo/aipseo.git
cd aipseo

# Install dependencies
pip install -e ".[dev]"

# Initialize project
aipseo init
```

### Testing

```bash
# Run tests
pytest

# Check code style
ruff check .
```

## License

Copyright 2024 Mark Counterman

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Trademark

aipseo™ is a trademark of Mark Counterman. Use of the name "aipseo" or
the "aipseo verified" badge in modified or redistributed versions of
this software must follow the brand guidelines at aipseo.com

## Support

For licensing inquiries, please contact aipseo.com
