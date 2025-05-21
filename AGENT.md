# AGENT Guide for AI Assistants

This document provides guidance for AI agents working with the **AIPSEO** repository.
It covers the project structure, setup, conventions, and common tasks to help you navigate
and contribute effectively.

---

## Repository Overview

> **AIPSEO** is a command-line interface for AI-powered SEO backlinks. It enables users to:

- Look up URL metrics (`lookup`)
- Check spam scores (`spam-score`)
- Manage wallets (`wallet create/balance/deposit/withdraw`)
- Interact with a backlink marketplace (`market list/buy/sell`)

In addition to the CLI, AIPSEO provides a **Model Context Protocol (MCP) server** (`aipseo/mcp_server.py`) allowing AI agents to programmatically access certain functionalities. Initially, this includes an SEO content analysis tool.

## Project Structure

```
.
├── AGENT.md           # (this file): AI assistant guide
├── README.md          # User-facing docs (installation, usage)
├── pyproject.toml     # Project metadata, dependencies, CI/test/formatter config
├── aipseo.json        # Default CLI configuration (API endpoints)
├── aipseo/            # Source code package
│   ├── cli.py         # CLI entry point and command definitions
│   ├── api.py         # HTTP client for backend services
│   ├── common.py      # Shared utilities (I/O, formatting)
│   ├── utils.py       # Encryption, display, and CLI helpers
│   ├── mcp_server.py  # MCP server exposing tools for AI agents
│   └── commands/      # Command handlers and sub-commands
├── .github/           # CI/CD workflows (publish, tests)
├── LICENSE            # Apache-2.0 license
└── notice             # Trademark and brand guidelines
```

## Setup & Development

The project targets **Python 3.8+** and uses [Hatchling](https://hatch.pypa.io/) for packaging.
Development and test settings (pytest, black, ruff) are configured in `pyproject.toml`.

```bash
# Install development dependencies (editable install)
pip install -e ".[dev]"

# Initialize default configuration
aipseo init
```

## Running & Testing

- **CLI help**: `aipseo --help` or `python -m aipseo.cli --help`
- **Run commands** as documented in `README.md`
- **Testing**: `pytest` (note: tests/ may need to be added)
- **Code style**:
  - Formatter: `black --line-length 88`
  - Linter: `ruff`

## Coding Conventions

When modifying the codebase, follow these conventions:

1. Preserve existing SPDX license headers (`# spdx-license-identifier: apache-2.0`)
2. Retain copyright notices at the top of source files.
3. Adhere to `black` and `ruff` style rules as configured in `pyproject.toml`.
4. Keep diffs focused and minimal; avoid unrelated changes.
5. Rely on clear code and docstrings; minimize inline comments.

## Common CLI Commands

Refer to `README.md` for full usage. Key commands include:

| Command                     | Description                           |
|-----------------------------|---------------------------------------|
| `aipseo init`               | Initialize aipseo.json configuration  |
| `aipseo validate`           | Validate configuration file           |
| `aipseo lookup <url>`       | Look up URL metadata                  |
| `aipseo spam-score <url>`   | Check spam score for a URL            |
| `aipseo toolspec --format openai` | Emit machine-readable function spec for AI integration |
| `aipseo wallet ...`         | Wallet management (create, balance, etc.) |
| `aipseo market ...`         | Marketplace operations (list, buy, sell) |

## Interacting via MCP

AIPSEO includes an MCP server that exposes tools for AI agents. You can interact with these tools by connecting to the server using an MCP client.

The server is defined in `aipseo/mcp_server.py` and can be run (for development/testing) using an ASGI server like Uvicorn:
```bash
uvicorn aipseo.mcp_server:mcp_server --host 0.0.0.0 --port 8000
```

### Available MCP Tools

#### `analyze_seo_content`

*   **Description**: Analyzes a given piece of text content for SEO best practices against a target keyword.
*   **Parameters**:
    *   `content` (string): The text content to analyze.
    *   `keyword` (string): The target keyword for the analysis.
*   **Returns**: (string) A summary of the SEO analysis and actionable recommendations.
*   **Example (conceptual)**:
    ```python
    # Assuming you have an MCP client instance `mcp_client`
    # connected to the AIPSEO MCP server.

    article_text = "This is my new blog post about amazing widgets."
    focus_keyword = "amazing widgets"

    try:
        seo_feedback = mcp_client.tools.analyze_seo_content(content=article_text, keyword=focus_keyword)
        print("SEO Feedback:", seo_feedback)
    except Exception as e:
        print(f"Error calling analyze_seo_content: {e}")
    ```

## AI Assistant Guidelines

1. Use this guide to orient and audit your changes.
2. Consult `README.md` and module docstrings for functional context.
3. Run local tests and style checks before proposing patches.
4. Avoid making assumptions; refer back to code, docs, and tests.
5. For API behavior or endpoints, inspect `aipseo/api.py` and `aipseo.json`.

---

*Generated by an AI assistant to aid automated code reviews and contributions.*