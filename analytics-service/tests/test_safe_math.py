"""Safe math helper tests."""
from app.helpers.safe_math import safe_divide


def test_safe_divide() -> None:
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
