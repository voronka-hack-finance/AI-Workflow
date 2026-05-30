"""Shared logger factory."""
import logging


def get_logger(name: str) -> logging.Logger:
    # TODO: structured logging, correlation ids
    return logging.getLogger(name)
