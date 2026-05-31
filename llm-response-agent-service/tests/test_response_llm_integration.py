"""Optional real LLM integration tests."""
from __future__ import annotations

import os

import pytest

from app.core.config import get_settings
from app.response_pipeline.response_agent_service import ResponseAgentService
from app.schemas.response_request import ResponseGenerateRequest
from tests.conftest import generate_payload

pytestmark = [
    pytest.mark.integration,
    pytest.mark.llm,
    pytest.mark.skipif(
        os.getenv("RUN_REAL_LLM_RESPONSE_TESTS") != "1",
        reason="Set RUN_REAL_LLM_RESPONSE_TESTS=1 to run real LLM response tests",
    ),
]


@pytest.fixture
def llm_service() -> ResponseAgentService:
    os.environ["RESPONSE_AGENT_LLM_PROVIDER"] = "openai_compatible"
    get_settings.cache_clear()
    return ResponseAgentService(settings=get_settings())


@pytest.mark.asyncio
async def test_generate_with_real_llm(llm_service: ResponseAgentService) -> None:
    request = ResponseGenerateRequest.model_validate(generate_payload())
    result = await llm_service.generate(request)
    assert result.editor_output.final_answer.strip()
    assert result.input_validation.can_run_agents is True
