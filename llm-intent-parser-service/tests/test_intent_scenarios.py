"""Data-driven intent scenario tests (mock provider)."""
from __future__ import annotations

from typing import Any

import pytest

from app.parser.service import IntentParserService
from tests.scenario_helpers import (
    assert_partial_match,
    build_request_from_scenario,
    load_scenarios,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", load_scenarios(), ids=lambda s: s["id"])
async def test_intent_scenario(service: IntentParserService, scenario: dict[str, Any]) -> None:
    request = build_request_from_scenario(scenario)
    response = await service.parse(request)
    assert_partial_match(
        response.intent_result.model_dump(mode="json"),
        scenario["expected"],
    )
