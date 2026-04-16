"""Order management for trading bot."""

from typing import Any, Dict, Optional

from bot.client import BinanceFuturesClient
from bot.logging_config import logger
from bot.validators import (
    ValidationError,
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
    validate_time_in_force,
)


def build_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    """Validate and normalize an order request."""
    normalized_type = validate_order_type(order_type)
    request: Dict[str, Any] = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "type": normalized_type,
        "quantity": validate_quantity(quantity),
    }

    if normalized_type == "LIMIT":
        request["price"] = validate_price(price, normalized_type)
        request["timeInForce"] = validate_time_in_force(time_in_force)
    else:
        validate_price(price, normalized_type)

    logger.debug("Validated order request: %s", request)
    return request


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float
) -> Dict[str, Any]:
    """
    Place a market order.
    
    Args:
        client: Binance Futures client
        symbol: Trading pair (e.g., 'BTCUSDT')
        side: Order side ('BUY' or 'SELL')
        quantity: Order quantity
    
    Returns:
        Order response dictionary
    
    Raises:
        ValidationError: If validation fails
        Exception: If order placement fails
    """
    request = build_order_request(symbol, side, "MARKET", quantity)
    return place_order(client, request)


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC"
) -> Dict[str, Any]:
    """
    Place a limit order.
    
    Args:
        client: Binance Futures client
        symbol: Trading pair (e.g., 'BTCUSDT')
        side: Order side ('BUY' or 'SELL')
        quantity: Order quantity
        price: Order price
        time_in_force: Time in force (default: 'GTC')
    
    Returns:
        Order response dictionary
    
    Raises:
        ValidationError: If validation fails
        Exception: If order placement fails
    """
    request = build_order_request(
        symbol,
        side,
        "LIMIT",
        quantity,
        price=price,
        time_in_force=time_in_force,
    )
    return place_order(client, request)


def place_order(
    client: BinanceFuturesClient,
    request: Dict[str, Any],
) -> Dict[str, Any]:
    """Place a validated MARKET or LIMIT order."""
    try:
        payload = build_order_request(
            symbol=request["symbol"],
            side=request["side"],
            order_type=request.get("order_type", request.get("type")),
            quantity=request["quantity"],
            price=request.get("price"),
            time_in_force=request.get("time_in_force", "GTC"),
        )
        logger.info("Submitting order request: %s", payload)
        response = client.create_order(**payload)
        logger.info("Order placed successfully: %s", response.get("orderId"))
        return format_order_response(response)
    except ValidationError:
        raise
    except Exception as exc:
        logger.error("Failed to place order: %s", str(exc))
        raise


def format_order_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format order response to display key information.
    
    Args:
        response: Raw order response from Binance API
    
    Returns:
        Formatted order information
    """
    formatted = {
        "orderId": response.get("orderId"),
        "status": response.get("status"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "orderType": response.get("type"),
        "quantity": float(response.get("origQty", 0)),
        "executedQty": float(response.get("executedQty", 0)),
        "price": float(response.get("price", 0)) if response.get("price") else None,
        "avgPrice": float(response.get("avgPrice", 0)) if response.get("avgPrice") else None,
        "timeInForce": response.get("timeInForce"),
        "updateTime": response.get("updateTime")
    }
    
    return formatted


def get_order_status(
    client: BinanceFuturesClient,
    symbol: str,
    order_id: int
) -> Dict[str, Any]:
    """
    Get the status of an order.
    
    Args:
        client: Binance Futures client
        symbol: Trading pair
        order_id: Order ID
    
    Returns:
        Order status information
    """
    symbol = validate_symbol(symbol)
    
    try:
        logger.info(f"Getting order status for {symbol} order {order_id}")
        response = client.get_order(symbol=symbol, order_id=order_id)
        return format_order_response(response)
    except Exception as e:
        logger.error(f"Failed to get order status: {str(e)}")
        raise


def cancel_order(
    client: BinanceFuturesClient,
    symbol: str,
    order_id: int
) -> Dict[str, Any]:
    """
    Cancel an order.
    
    Args:
        client: Binance Futures client
        symbol: Trading pair
        order_id: Order ID
    
    Returns:
        Cancelled order information
    """
    symbol = validate_symbol(symbol)
    
    try:
        logger.info(f"Cancelling order {order_id} for {symbol}")
        response = client.cancel_order(symbol=symbol, order_id=order_id)
        logger.info(f"Order {order_id} cancelled successfully")
        return format_order_response(response)
    except Exception as e:
        logger.error(f"Failed to cancel order: {str(e)}")
        raise
