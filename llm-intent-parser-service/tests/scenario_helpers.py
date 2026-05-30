"""Helpers for data-driven intent scenario tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.schemas.intent_request import IntentParseRequest

SCENARIOS_PATH = Path(__file__).parent / "fixtures" / "intent_scenarios.json"

DEFAULT_REQUEST_FIELDS: dict[str, Any] = {
    "user_id": "user_123",
    "chat_id": "chat_001",
    "current_date": "2026-05-29",
    "timezone": "Europe/Moscow",
}


def load_scenarios(*, ids: list[str] | None = None) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    if ids is None:
        return scenarios
    id_set = set(ids)
    filtered = [scenario for scenario in scenarios if scenario["id"] in id_set]
    missing = id_set - {scenario["id"] for scenario in filtered}
    if missing:
        raise ValueError(f"Unknown scenario ids: {sorted(missing)}")
    return filtered


def build_request_from_scenario(scenario: dict[str, Any]) -> IntentParseRequest:
    payload: dict[str, Any] = {
        **DEFAULT_REQUEST_FIELDS,
        "request_id": f"req_{scenario['id']}",
        "raw_message": scenario["message"],
    }
    chat_context = scenario.get("chat_context")
    if chat_context is not None:
        payload["chat_context"] = chat_context
    return IntentParseRequest.model_validate(payload)


def assert_partial_match(
    actual: Any,
    expected: Any,
    *,
    path: str = "",
) -> None:
    if expected is None:
        assert actual is None, f"Expected null at {path or '<root>'}, got {actual!r}"
        return

    if isinstance(expected, dict):
        assert isinstance(actual, dict), (
            f"Expected dict at {path or '<root>'}, got {type(actual).__name__}: {actual!r}"
        )
        for key, expected_value in expected.items():
            child_path = f"{path}.{key}" if path else key
            assert key in actual, f"Missing key at {child_path}"
            assert_partial_match(actual[key], expected_value, path=child_path)
        return

    if isinstance(expected, list):
        assert actual == expected, (
            f"List mismatch at {path or '<root>'}: expected {expected!r}, got {actual!r}"
        )
        return

    assert actual == expected, (
        f"Value mismatch at {path or '<root>'}: expected {expected!r}, got {actual!r}"
    )
