"""Intent parser orchestration service."""
from __future__ import annotations

from app.core.config import Settings, get_settings
from app.core.errors import LLMParseError
from app.llm.base import LLMProvider
from app.llm.mock_provider import MockProvider
from app.llm.provider_factory import create_llm_provider
from app.parser.message_hints import apply_message_hints
from app.parser.json_parser import parse_llm_json
from app.parser.validator import validate_intent_payload
from app.prompts.intent_prompt import build_prompt_messages
from app.schemas.intent_request import IntentParseRequest
from shared_contracts.intent_result import IntentParserResponse


class IntentParserService:
    def __init__(
        self,
        provider: LLMProvider | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._provider = provider or create_llm_provider(self._settings)

    async def parse(self, request: IntentParseRequest) -> IntentParserResponse:
        provider = self._provider
        if isinstance(provider, MockProvider):
            provider = provider.bind_request(request)

        messages = build_prompt_messages(request)
        raw_output = await provider.generate(messages)

        try:
            payload = parse_llm_json(raw_output)
            intent_result = validate_intent_payload(payload)
            intent_result = apply_message_hints(request, intent_result)
        except LLMParseError:
            raise
        except Exception as exc:  # noqa: BLE001 - surface provider failures consistently
            raise LLMParseError(f"Failed to parse intent: {exc}") from exc

        return IntentParserResponse(
            request_id=request.request_id,
            user_id=request.user_id,
            chat_id=request.chat_id,
            raw_message=request.raw_message,
            intent_result=intent_result,
        )
