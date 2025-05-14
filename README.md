# aipseo-cli · ai-powered seo toolkit

[![license](https://img.shields.io/github/license/aipseo/aipseo-cli)](license)

A command-line interface for interacting with AIPSEO services.

## Installation

```bash
pip install aipseo-cli
```

## Usage

```bash
# Initialize a new AIPSEO manifest file
aipseo init

# Validate an existing manifest file
aipseo validate

# Look up information for a URL
aipseo lookup example.com

# Check spam score
aipseo spam-score example.com

# Create a new wallet for marketplace operations
aipseo wallet create --name mywallet --output .wallet.json

# Check your wallet balance
aipseo wallet balance --wallet .wallet.json

# Deposit funds to your wallet using Stripe checkout
aipseo wallet deposit --wallet .wallet.json --amount 100

# Withdraw funds from your wallet
aipseo wallet withdraw --wallet .wallet.json --amount 50 --dest your_bank_account

# List available backlink opportunities in the marketplace
aipseo market list --dr-min 30 --price-max 100

# Purchase a backlink from the marketplace
aipseo market buy --wallet .wallet.json --listing-id lst_12345678

# List a backlink for sale in the marketplace
aipseo market sell --wallet .wallet.json --source-url https://yourblog.com/post --target-url https://target.com --price 75 --anchor "useful resource"
```

## Features

- **init**: Create a new AIPSEO manifest file
- **validate**: Validate an existing manifest file
- **lookup**: Look up information for a domain or URL
- **spam-score**: Get spam score for a domain or URL
- **wallet**: Manage your AIPSEO marketplace wallet
  - **create**: Create a new wallet for marketplace operations
  - **balance**: Check your wallet balance
  - **deposit**: Add funds to your wallet via Stripe checkout
  - **withdraw**: Withdraw funds from your wallet
- **market**: Marketplace operations for buying and selling backlinks
  - **list**: List available backlink opportunities
  - **buy**: Purchase a backlink from the marketplace
  - **sell**: List a backlink for sale in the marketplace

## Development

Clone the repository and install development dependencies:

```bash
git clone https://github.com/aipseo/aipseo-cli.git
cd aipseo-cli
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

apache-2.0