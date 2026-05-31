"""Backward-compatible alias for input validation."""
from app.validators.input_validator import InputValidator as SafetyValidator

__all__ = ["SafetyValidator"]
