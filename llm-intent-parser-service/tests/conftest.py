"""Shared test fixtures."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.parser.service import IntentParserService


def _load_dotenv_keys(*keys: str) -> None:
    """Load selected keys from service .env for pytest (e.g. RUN_REAL_LLM_INTENT_TESTS)."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    wanted = set(keys)
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key not in wanted:
            continue
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv_keys("RUN_REAL_LLM_INTENT_TESTS")
os.environ.setdefault("INTENT_PARSER_LLM_PROVIDER", "mock")


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def service() -> IntentParserService:
    return IntentParserService()


def minimal_parse_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "request_id": "req_001",
        "user_id": "user_123",
        "chat_id": "chat_001",
        "raw_message": "Дай рекомендацию по бюджету на месяц.",
        "current_date": "2026-05-29",
        "timezone": "Europe/Moscow",
        "chat_context": {
            "last_6_messages": [],
            "chat_summary": None,
            "active_workflow": None,
        },
    }
    payload.update(overrides)
    return payload
