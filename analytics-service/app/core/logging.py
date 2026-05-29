"""Logging setup placeholder."""
import logging

# TODO: integrate shared_logging package


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
