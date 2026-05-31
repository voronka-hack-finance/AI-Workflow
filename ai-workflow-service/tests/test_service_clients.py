"""AI service client tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.clients.intent_parser_client import IntentParserClient
from app.core.config import Settings
from app.core.errors import ContractValidationError
from shared_http.errors import ServiceTimeoutError, ServiceUnavailableError


@pytest.fixture
def settings() -> Settings:
    return Settings(
        intent_parser_service_url="http://intent-parser.test",
        ai_workflow_http_timeout_seconds=1.0,
        ai_workflow_http_max_retries=2,
    )


@pytest.mark.asyncio
async def test_intent_parser_client_parses_response(settings: Settings) -> None:
    client = IntentParserClient(settings)
    payload = {
        "schema_version": "1.0",
        "request_id": "req_001",
        "user_id": "user_123",
        "chat_id": "chat_001",
        "raw_message": "test",
        "intent_result": {"primary_intent": "budget_recommendation"},
    }

    with patch.object(client._http, "post_json", AsyncMock(return_value=payload)):
        from tests.conftest import sample_task

        result = await client.parse_intent(sample_task())

    assert result.request_id == "req_001"
    assert result.intent_result.primary_intent == "budget_recommendation"


@pytest.mark.asyncio
async def test_client_retries_on_503(settings: Settings) -> None:
    from shared_http.client import ServiceHttpClient

    http = ServiceHttpClient("http://example.test", timeout=1.0, max_retries=2)
    responses = [
        httpx.Response(503, request=httpx.Request("POST", "http://example.test/x")),
        httpx.Response(200, json={"ok": True}, request=httpx.Request("POST", "http://example.test/x")),
    ]

    async def fake_post(*args, **kwargs):
        return responses.pop(0)

    with patch("httpx.AsyncClient.post", new=AsyncMock(side_effect=fake_post)):
        result = await http.post_json("/x", {"a": 1})

    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_client_timeout_error(settings: Settings) -> None:
    from shared_http.client import ServiceHttpClient

    http = ServiceHttpClient("http://example.test", timeout=0.01, max_retries=0)

    with patch(
        "httpx.AsyncClient.post",
        new=AsyncMock(side_effect=httpx.TimeoutException("timeout")),
    ):
        with pytest.raises(ServiceTimeoutError, match="example.test/x"):
            await http.post_json("/x", {})


@pytest.mark.asyncio
async def test_client_timeout_error_without_message(settings: Settings) -> None:
    from shared_http.client import ServiceHttpClient

    http = ServiceHttpClient("http://example.test", timeout=30.0, max_retries=0)

    with patch(
        "httpx.AsyncClient.post",
        new=AsyncMock(side_effect=httpx.ReadTimeout("")),
    ):
        with pytest.raises(ServiceTimeoutError, match="timed out after 30.0s"):
            await http.post_json("/x", {})


@pytest.mark.asyncio
async def test_intent_parser_client_uses_longer_timeout(settings: Settings) -> None:
    settings = Settings(
        intent_parser_service_url="http://intent-parser.test",
        ai_workflow_http_timeout_seconds=30.0,
        intent_parser_http_timeout_seconds=150.0,
        ai_workflow_http_max_retries=2,
    )
    client = IntentParserClient(settings)
    assert client._http._timeout == 150.0


@pytest.mark.asyncio
async def test_response_agent_client_uses_longer_timeout(settings: Settings) -> None:
    settings = Settings(
        response_agent_service_url="http://response-agent.test",
        ai_workflow_http_timeout_seconds=30.0,
        response_agent_http_timeout_seconds=300.0,
        ai_workflow_http_max_retries=2,
    )
    from app.clients.response_agent_client import ResponseAgentClient

    client = ResponseAgentClient(settings)
    assert client._http._timeout == 300.0


@pytest.mark.asyncio
async def test_contract_validation_error(settings: Settings) -> None:
    client = IntentParserClient(settings)

    with patch.object(client._http, "post_json", AsyncMock(return_value={"invalid": True})):
        from tests.conftest import sample_task

        with pytest.raises(ContractValidationError):
            await client.parse_intent(sample_task())


@pytest.mark.asyncio
async def test_service_unavailable_after_retries(settings: Settings) -> None:
    from shared_http.client import ServiceHttpClient

    http = ServiceHttpClient("http://example.test", timeout=1.0, max_retries=1)

    with patch(
        "httpx.AsyncClient.post",
        new=AsyncMock(side_effect=httpx.ConnectError("connection failed")),
    ):
        with pytest.raises(ServiceUnavailableError):
            await http.post_json("/x", {})
