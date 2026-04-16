"""Central logging configuration for the trading bot."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "trading.log"


def setup_logging() -> logging.Logger:
    """Configure console and file logging once for the whole app."""
    logger = logging.getLogger("trading_bot")
    if logger.handlers:
        return logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


logger = setup_logging()
