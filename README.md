# aipseo

[![license](https://img.shields.io/github/license/aipseo/aipseo)](license)
[![CI/CD](https://github.com/aipseo/aipseo/actions/workflows/ci.yml/badge.svg)](https://github.com/aipseo/aipseo/actions/workflows/ci.yml)

A command-line interface for AI powered SEO backlinks.

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

Copyright 2024 Mark Counterman (ilovepoker@gmail.com)

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
this software must follow the brand guidelines at https://aipseo.com/brand.

## Support

For licensing inquiries, please contact:
Mark Counterman
Email: ilovepoker@gmail.com