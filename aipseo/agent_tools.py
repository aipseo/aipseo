# spdx-license-identifier: apache-2.0
# copyright 2024 mark counterman

from typing import Optional

from aipseo.api import APIClient


def get_url_lookup(url: str) -> dict:
    """
    Performs a URL lookup using the APIClient.

    Args:
        url: The URL to lookup.

    Returns:
        A dictionary containing the lookup result.
    """
    client = APIClient()
    return client.lookup(url)


def get_spam_score(url: str) -> dict:
    """
    Retrieves the spam score for a given URL using the APIClient.

    Args:
        url: The URL to get the spam score for.

    Returns:
        A dictionary containing the spam score result.
    """
    client = APIClient()
    return client.spam_score(url)


def list_market_opportunities(
    dr_min: Optional[int] = None,
    price_max: Optional[float] = None,
    topic: Optional[str] = None,
) -> list:
    """
    Lists market opportunities based on the provided filters using the APIClient.

    Args:
        dr_min: Optional minimum domain rating.
        price_max: Optional maximum price.
        topic: Optional topic to filter by.

    Returns:
        A list of market opportunities.
    """
    client = APIClient()
    return client.search_marketplace(
        dr_min=dr_min, price_max=price_max, topic=topic
    )


def get_wallet_balance(wallet_id: str) -> dict:
    """
    Retrieves the balance for a given wallet ID using the APIClient.

    Args:
        wallet_id: The ID of the wallet to get the balance for.

    Returns:
        A dictionary containing the wallet balance result.
    """
    client = APIClient()
    return client.get_balance(wallet_id)
