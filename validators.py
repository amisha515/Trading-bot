"""Input validators for trading bot."""

import re
from typing import Optional, Union

from bot.logging_config import logger


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate trading pair symbol.
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
    
    Returns:
        Validated symbol in uppercase
    
    Raises:
        ValidationError: If symbol is invalid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string")
    
    symbol = symbol.upper().strip()
    
    if not re.match(r'^[A-Z]+USDT$', symbol):
        raise ValidationError(f"Invalid symbol format: {symbol}. Expected format: BTCUSDT")
    
    if len(symbol) < 7:
        raise ValidationError(f"Symbol too short: {symbol}")
    
    logger.debug(f"Symbol validated: {symbol}")
    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.
    
    Args:
        side: Order side ('BUY' or 'SELL')
    
    Returns:
        Validated side in uppercase
    
    Raises:
        ValidationError: If side is invalid
    """
    if not side or not isinstance(side, str):
        raise ValidationError("Side must be a non-empty string")
    
    side = side.upper().strip()
    
    if side not in ['BUY', 'SELL']:
        raise ValidationError(f"Invalid side: {side}. Must be 'BUY' or 'SELL'")
    
    logger.debug(f"Side validated: {side}")
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.
    
    Args:
        order_type: Order type ('MARKET' or 'LIMIT')
    
    Returns:
        Validated order type in uppercase
    
    Raises:
        ValidationError: If order type is invalid
    """
    if not order_type or not isinstance(order_type, str):
        raise ValidationError("Order type must be a non-empty string")
    
    order_type = order_type.upper().strip()
    
    if order_type not in ["MARKET", "LIMIT"]:
        raise ValidationError(
            f"Invalid order type: {order_type}. Must be 'MARKET' or 'LIMIT'"
        )
    
    logger.debug(f"Order type validated: {order_type}")
    return order_type


def validate_quantity(quantity: Union[str, float, int]) -> float:
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity
    
    Returns:
        Validated quantity as float
    
    Raises:
        ValidationError: If quantity is invalid
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid quantity: {quantity}. Must be a valid number")
    
    if qty <= 0:
        raise ValidationError(f"Quantity must be positive, got: {qty}")
    
    if qty > 10000:
        raise ValidationError(f"Quantity too large: {qty}. Maximum allowed: 10000")
    
    logger.debug(f"Quantity validated: {qty}")
    return qty


def validate_price(
    price: Optional[Union[str, float, int]],
    order_type: str,
) -> Optional[float]:
    """
    Validate order price.
    
    Args:
        price: Order price
        order_type: Type of order (MARKET or LIMIT)
    
    Returns:
        Validated price as float
    
    Raises:
        ValidationError: If price is invalid for the order type
    """
    order_type = validate_order_type(order_type)

    if order_type == "MARKET":
        logger.debug("Price validation skipped for MARKET order")
        return None
    
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders")
        
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid price: {price}. Must be a valid number")
        
        if p <= 0:
            raise ValidationError(f"Price must be positive, got: {p}")
        
        if p > 1000000:
            raise ValidationError(f"Price too large: {p}. Maximum allowed: 1000000")
        
        logger.debug(f"Price validated: {p}")
        return p
    
    return None


def validate_time_in_force(time_in_force: str) -> str:
    """Validate the Binance time-in-force value."""
    if not time_in_force or not isinstance(time_in_force, str):
        raise ValidationError("Time in force must be a non-empty string")

    tif = time_in_force.upper().strip()
    allowed = {"GTC", "IOC", "FOK"}
    if tif not in allowed:
        raise ValidationError(
            f"Invalid time in force: {tif}. Must be one of {', '.join(sorted(allowed))}"
        )

    logger.debug(f"Time in force validated: {tif}")
    return tif
