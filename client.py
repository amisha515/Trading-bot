"""Binance Futures client wrapper."""

import os
from typing import Any, Dict

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

from bot.logging_config import logger


DEFAULT_BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesClient:
    """Small wrapper around python-binance Futures methods."""

    def __init__(self, api_key: str, api_secret: str, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = FuturesTestnetClient(api_key, api_secret, testnet=True)
        # Ignore host app proxy env vars so requests go directly to Binance testnet.
        self._client.session.trust_env = False
        self._client.session.proxies.clear()
        self._client.FUTURES_URL = f"{self.base_url}/fapi"
        logger.info("Binance Futures client configured for %s", self.base_url)

    def get_server_time(self) -> Dict[str, Any]:
        """Ping Binance Futures Testnet."""
        return self._request("futures_time")

    def create_order(self, **payload: Any) -> Dict[str, Any]:
        """Create a futures order."""
        return self._request("futures_create_order", **payload)

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Fetch a futures order."""
        return self._request("futures_get_order", symbol=symbol, orderId=order_id)

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel a futures order."""
        return self._request("futures_cancel_order", symbol=symbol, orderId=order_id)

    def _request(self, method_name: str, **payload: Any) -> Dict[str, Any]:
        """Log requests and normalize Binance exceptions."""
        logger.info("API request: %s payload=%s", method_name, payload)
        try:
            method = getattr(self._client, method_name)
            response = method(**payload)
            logger.info("API response: %s", response)
            return response
        except BinanceAPIException as exc:
            logger.error(
                "Binance API error on %s: status=%s code=%s message=%s",
                method_name,
                exc.status_code,
                exc.code,
                exc.message,
            )
            raise RuntimeError(f"Binance API error: {exc.message}") from exc
        except BinanceRequestException as exc:
            logger.error("Network/request error on %s: %s", method_name, exc.message)
            raise RuntimeError(f"Network error: {exc.message}") from exc
        except Exception as exc:
            logger.exception("Unexpected error on %s", method_name)
            raise RuntimeError(f"Unexpected client error: {exc}") from exc


class FuturesTestnetClient(Client):
    """Disable the constructor spot ping so the app stays Futures-only."""

    def ping(self) -> Dict[str, Any]:
        return {}


def initialize_client() -> BinanceFuturesClient:
    """
    Initialize Binance Futures Testnet client.
    
    Returns:
        UMFutures client instance
    
    Raises:
        ValueError: If API keys are not configured
    """
    load_dotenv()

    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    base_url = os.getenv("BASE_URL", DEFAULT_BASE_URL)

    if not api_key or not api_secret:
        logger.error("API keys not found in .env file")
        raise ValueError(
            "API_KEY and API_SECRET must be set in .env file"
        )

    try:
        client = BinanceFuturesClient(api_key, api_secret, base_url)
        logger.info("Binance Futures Testnet client initialized successfully")
        return client
    except Exception as exc:
        logger.exception("Failed to initialize client")
        raise RuntimeError(f"Failed to initialize client: {exc}") from exc


def test_connection(client: BinanceFuturesClient) -> bool:
    """
    Test the connection to Binance Futures Testnet.
    
    Args:
        client: UMFutures client instance
    
    Returns:
        True if connection is successful
    """
    try:
        client.get_server_time()
        logger.info("Connection to Binance Futures Testnet successful")
        return True
    except Exception as exc:
        logger.error(f"Connection test failed: {str(exc)}")
        raise
