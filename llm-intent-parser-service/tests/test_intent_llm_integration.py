"""Optional real LLM integration tests for intent scenarios."""
from __future__ import annotations

import os
from typing import Any

import pytest

from app.core.config import get_settings
from app.parser.service import IntentParserService
from tests.scenario_helpers import (
    assert_partial_match,
    build_request_from_scenario,
    load_scenarios,
)

LLM_SMOKE_IDS = ["budget_recommendation", "goal_analysis_full", "goal_analysis_missing"]

pytestmark = [
    pytest.mark.integration,
    pytest.mark.llm,
    pytest.mark.skipif(
        os.getenv("RUN_REAL_LLM_INTENT_TESTS") != "1",
        reason="Set RUN_REAL_LLM_INTENT_TESTS=1 to run real LLM intent tests",
    ),
]


@pytest.fixture
def llm_service() -> IntentParserService:
    os.environ["INTENT_PARSER_LLM_PROVIDER"] = "openai_compatible"
    get_settings.cache_clear()
    return IntentParserService(settings=get_settings())


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", load_scenarios(ids=LLM_SMOKE_IDS), ids=lambda s: s["id"])
async def test_intent_scenario_with_real_llm(
    llm_service: IntentParserService,
    scenario: dict[str, Any],
) -> None:
    request = build_request_from_scenario(scenario)
    response = await llm_service.parse(request)
    assert_partial_match(
        response.intent_result.model_dump(mode="json"),
        scenario["expected"],
    )
