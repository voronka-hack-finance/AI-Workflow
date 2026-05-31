"""Boundary rules tests."""
from pathlib import Path


def test_service_has_no_backend_clients() -> None:
    root = Path(__file__).resolve().parent.parent / "app"
    forbidden = ("rabbitmq", "backend_data", "sqlalchemy", "psycopg")
    for path in root.rglob("*.py"):
        content = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in content, f"Forbidden token {token} found in {path}"


def test_service_has_no_analytics_formulas_module() -> None:
    app_root = Path(__file__).resolve().parent.parent / "app"
    assert not (app_root / "functions").exists()
