"""Boundary checks for Phase 04 scope."""
from __future__ import annotations

import ast
from pathlib import Path


def _collect_app_python_files() -> list[Path]:
    app_dir = Path(__file__).resolve().parents[1] / "app"
    return sorted(app_dir.rglob("*.py"))


def _file_import_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_app_code_has_no_langgraph_or_backend_clients() -> None:
    forbidden_roots = {
        "langgraph",
        "rabbitmq",
        "aio_pika",
        "pika",
        "sqlalchemy",
        "psycopg",
        "asyncpg",
    }
    violations: list[str] = []
    for path in _collect_app_python_files():
        imported = _file_import_names(path)
        blocked = sorted(imported & forbidden_roots)
        if blocked:
            violations.append(f"{path.name}: {', '.join(blocked)}")
    assert violations == []
