"""Service and endpoint error-path tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import BaseMessage

from app.core.errors import LLMParseError
from app.main import app
from app.parser.service import IntentParserService
from app.schemas.intent_request import IntentParseRequest
from tests.conftest import minimal_parse_payload


class InvalidJsonProvider:
    async def generate(self, messages: list[BaseMessage]) -> str:
        del messages
        return "not valid json at all"


@pytest.mark.asyncio
async def test_service_rejects_invalid_llm_json() -> None:
    service = IntentParserService(provider=InvalidJsonProvider())
    request = IntentParseRequest.model_validate(minimal_parse_payload())
    with pytest.raises(LLMParseError):
        await service.parse(request)


def test_endpoint_rejects_invalid_llm_json() -> None:
    from app.api.v1 import parse_intent as parse_intent_module

    original_service = parse_intent_module._parser_service
    parse_intent_module._parser_service = IntentParserService(provider=InvalidJsonProvider())
    try:
        client = TestClient(app)
        response = client.post("/api/v1/intent/parse", json=minimal_parse_payload())
        assert response.status_code == 422
        assert "JSON" in response.json()["detail"]
    finally:
        parse_intent_module._parser_service = original_service
