"""CLI interface for trading bot using Typer."""

from typing import Optional

import typer

from bot.client import initialize_client, test_connection
from bot.logging_config import logger
from bot.orders import build_order_request, cancel_order, get_order_status, place_order
from bot.validators import ValidationError, validate_order_type


app = typer.Typer(
    help="Trading Bot - Binance Futures Testnet (USDT-M)",
    no_args_is_help=True,
)


def print_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    time_in_force: Optional[str] = None,
) -> None:
    """Print a clear order request summary before submission."""
    typer.echo("\nOrder Request Summary")
    typer.echo("-" * 60)
    typer.echo(f"Symbol:         {symbol}")
    typer.echo(f"Side:           {side}")
    typer.echo(f"Order Type:     {order_type}")
    typer.echo(f"Quantity:       {quantity}")
    if price is not None:
        typer.echo(f"Price:          {price}")
    if time_in_force:
        typer.echo(f"Time in Force:  {time_in_force}")
    typer.echo("-" * 60)


def print_order_result(order: dict) -> None:
    """Print formatted order response details."""
    typer.echo("\nOrder Response")
    typer.echo("=" * 60)
    typer.echo(f"Order ID:       {order['orderId']}")
    typer.echo(f"Status:         {order['status']}")
    typer.echo(f"Symbol:         {order['symbol']}")
    typer.echo(f"Side:           {order['side']}")
    typer.echo(f"Type:           {order['orderType']}")
    typer.echo(f"Quantity:       {order['quantity']}")
    typer.echo(f"Executed Qty:   {order['executedQty']}")
    if order["price"]:
        typer.echo(f"Price:          {order['price']}")
    if order["avgPrice"]:
        typer.echo(f"Avg Price:      {order['avgPrice']}")
    typer.echo("=" * 60 + "\n")


@app.command()
def place(
    symbol: str = typer.Argument(..., help="Trading pair (e.g., BTCUSDT)"),
    side: str = typer.Argument(..., help="Order side (BUY or SELL)"),
    order_type: str = typer.Argument(..., help="Order type (MARKET or LIMIT)"),
    quantity: float = typer.Argument(..., help="Order quantity"),
    price: Optional[float] = typer.Option(
        None,
        "--price",
        help="Order price for LIMIT orders",
    ),
    time_in_force: str = typer.Option(
        "GTC",
        "--tif",
        help="Time in Force for LIMIT orders (GTC, IOC, FOK)",
    ),
) -> None:
    """Place a MARKET or LIMIT order."""
    try:
        normalized_type = validate_order_type(order_type)
        print_order_summary(
            symbol=symbol.upper().strip(),
            side=side.upper().strip(),
            order_type=normalized_type,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force if normalized_type == "LIMIT" else None,
        )

        request = build_order_request(
            symbol=symbol,
            side=side,
            order_type=normalized_type,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )

        client = initialize_client()
        test_connection(client)

        typer.echo(f"\nSubmitting {normalized_type} order...")
        order = place_order(client, request)
        print_order_result(order)
        typer.secho(
            f"[OK] {normalized_type} order placed successfully",
            fg=typer.colors.GREEN,
        )
    except ValidationError as exc:
        typer.secho(f"[ERROR] Validation Error: {exc}", fg=typer.colors.RED)
        logger.error("Validation Error: %s", exc)
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"[ERROR] Error: {exc}", fg=typer.colors.RED)
        logger.error("Error: %s", exc)
        raise typer.Exit(code=1)


@app.command()
def status(
    symbol: str = typer.Argument(..., help="Trading pair (e.g., BTCUSDT)"),
    order_id: int = typer.Argument(..., help="Order ID"),
) -> None:
    """Get the status of an order."""
    try:
        client = initialize_client()
        test_connection(client)

        typer.echo("\nFetching order status...")
        order = get_order_status(client, symbol, order_id)
        print_order_result(order)

        typer.secho("[OK] Order status retrieved successfully", fg=typer.colors.GREEN)
    except ValidationError as exc:
        typer.secho(f"[ERROR] Validation Error: {exc}", fg=typer.colors.RED)
        logger.error("Validation Error: %s", exc)
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"[ERROR] Error: {exc}", fg=typer.colors.RED)
        logger.error("Error: %s", exc)
        raise typer.Exit(code=1)


@app.command()
def cancel(
    symbol: str = typer.Argument(..., help="Trading pair (e.g., BTCUSDT)"),
    order_id: int = typer.Argument(..., help="Order ID"),
) -> None:
    """Cancel an open order."""
    try:
        client = initialize_client()
        test_connection(client)

        typer.echo("\nCancelling order...")
        order = cancel_order(client, symbol, order_id)
        print_order_result(order)

        typer.secho("[OK] Order cancelled successfully", fg=typer.colors.GREEN)
    except ValidationError as exc:
        typer.secho(f"[ERROR] Validation Error: {exc}", fg=typer.colors.RED)
        logger.error("Validation Error: %s", exc)
        raise typer.Exit(code=1)
    except Exception as exc:
        typer.secho(f"[ERROR] Error: {exc}", fg=typer.colors.RED)
        logger.error("Error: %s", exc)
        raise typer.Exit(code=1)


@app.command()
def test() -> None:
    """Test connection to Binance Futures Testnet."""
    try:
        client = initialize_client()
        test_connection(client)
        typer.secho("[OK] Connection successful", fg=typer.colors.GREEN)
    except Exception as exc:
        typer.secho(f"[ERROR] Connection failed: {exc}", fg=typer.colors.RED)
        logger.error("Connection failed: %s", exc)
        raise typer.Exit(code=1)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
