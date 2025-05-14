"""API client for aipseo services."""

import json
import os
import time
from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from aipseo.common import ERROR_CONSOLE, read_json_file


class APIClient:
    """Client for interacting with the aipseo API."""

    def __init__(self, manifest_path: Optional[str] = None):
        """Initialize the API client with configuration from manifest."""
        # Use environment variable or default path
        manifest_path = manifest_path or os.environ.get("aipseo_manifest", "aipseo.json")
        self.manifest = read_json_file(manifest_path)
        self.settings = self.manifest.get("settings", {})
        self.api_settings = self.settings.get("api", {})
        
        # Get current environment and endpoint
        self.environment = self.api_settings.get("environment", "development")
        self.endpoints = self.api_settings.get("endpoints", {})
        self.base_url = self.endpoints.get(self.environment)
        
        if not self.base_url:
            raise ValueError(f"No API endpoint configured for environment: {self.environment}")
        
        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.api_settings.get("max_retries", 3),
            backoff_factor=self.api_settings.get("retry_delay", 1),
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default timeout
        self.timeout = self.api_settings.get("timeout", 30)

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make a request to the API with proper error handling."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=json_data, timeout=self.timeout)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            ERROR_CONSOLE.print(f"Error: Request to {endpoint} timed out after {self.timeout} seconds")
            raise
        except requests.exceptions.ConnectionError:
            ERROR_CONSOLE.print(f"Error: Could not connect to {self.base_url}")
            raise
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                ERROR_CONSOLE.print("Error: Authentication failed. Please check your API credentials.")
            elif e.response.status_code == 403:
                ERROR_CONSOLE.print("Error: Access denied. Please check your permissions.")
            elif e.response.status_code == 429:
                ERROR_CONSOLE.print("Error: Rate limit exceeded. Please try again later.")
            else:
                ERROR_CONSOLE.print(f"Error: API request failed with status {e.response.status_code}")
            raise
        except json.JSONDecodeError:
            ERROR_CONSOLE.print(f"Error: Invalid JSON response from {endpoint}")
            raise
        except Exception as e:
            ERROR_CONSOLE.print(f"Error: Unexpected error during API request: {str(e)}")
            raise

    def lookup(self, url: str) -> Dict[str, Any]:
        """Look up information for a URL."""
        return self._make_request("lookup", params={"url": url})

    def spam_score(self, url: str) -> Dict[str, Any]:
        """Get spam score for a URL."""
        return self._make_request("spam-score", params={"url": url})

    def create_wallet(self, name: str) -> Dict[str, Any]:
        """Create a new wallet."""
        return self._make_request("wallet/create", method="POST", json_data={"name": name})

    def get_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Get wallet balance."""
        return self._make_request("wallet/balance", params={"wallet_id": wallet_id})

    def deposit(self, wallet_id: str, amount: float) -> Dict[str, Any]:
        """Initiate a deposit."""
        return self._make_request(
            "wallet/deposit",
            method="POST",
            json_data={"wallet_id": wallet_id, "amount_usd": amount},
        )

    def withdraw(self, wallet_id: str, amount: float, dest: str) -> Dict[str, Any]:
        """Initiate a withdrawal."""
        return self._make_request(
            "wallet/withdraw",
            method="POST",
            json_data={"wallet_id": wallet_id, "amount_usd": amount, "dest": dest},
        )

    def search_marketplace(
        self,
        dr_min: Optional[int] = None,
        price_max: Optional[float] = None,
        topic: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search marketplace listings."""
        params = {}
        if dr_min is not None:
            params["dr_min"] = dr_min
        if price_max is not None:
            params["price_max"] = price_max
        if topic is not None:
            params["topic"] = topic
        return self._make_request("marketplace/search", params=params)

    def buy_listing(self, wallet_id: str, listing_id: str) -> Dict[str, Any]:
        """Purchase a marketplace listing."""
        return self._make_request(
            "marketplace/buy",
            method="POST",
            json_data={"wallet_id": wallet_id, "listing_id": listing_id},
        )

    def list_backlink(
        self,
        wallet_id: str,
        source_url: str,
        target_url: str,
        price: float,
        anchor: str,
        rel: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List a backlink for sale."""
        data = {
            "wallet_id": wallet_id,
            "source_url": source_url,
            "target_url": target_url,
            "price_usd": price,
            "anchor": anchor,
        }
        if rel:
            data["rel"] = rel
        return self._make_request("marketplace/list", method="POST", json_data=data) 