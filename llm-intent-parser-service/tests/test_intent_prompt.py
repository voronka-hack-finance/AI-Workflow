"""Intent prompt tests."""
from langchain_core.messages import HumanMessage

from app.prompts.examples import FEW_SHOT_EXAMPLES, HUMAN_INPUT_INSTRUCTION
from app.prompts.intent_prompt import build_input_payload, build_prompt_messages
from app.schemas.intent_request import IntentParseRequest


def _request(**overrides: object) -> IntentParseRequest:
    payload = {
        "request_id": "req_001",
        "user_id": "user_123",
        "chat_id": "chat_001",
        "raw_message": "Дай рекомендацию по бюджету",
        "current_date": "2026-05-30",
        "timezone": "Europe/Moscow",
    }
    payload.update(overrides)
    return IntentParseRequest.model_validate(payload)


def test_build_input_payload_contains_all_keys() -> None:
    payload = build_input_payload(_request())
    assert set(payload.keys()) == {
        "current_date",
        "timezone",
        "chat_summary",
        "last_6_messages",
        "active_workflow",
        "raw_message",
    }
    assert payload["current_date"] == "2026-05-30"
    assert payload["timezone"] == "Europe/Moscow"
    assert payload["raw_message"] == "Дай рекомендацию по бюджету"
    assert payload["chat_summary"] is None
    assert payload["last_6_messages"] == []
    assert payload["active_workflow"] is None


def test_build_prompt_messages_uses_structured_json_input() -> None:
    messages = build_prompt_messages(_request())
    last_human = next(message for message in reversed(messages) if isinstance(message, HumanMessage))
    content = str(last_human.content)
    assert HUMAN_INPUT_INSTRUCTION.strip() in content
    assert '"raw_message": "Дай рекомендацию по бюджету"' in content
    assert '"current_date": "2026-05-30"' in content


def test_few_shot_examples_use_structured_json_input() -> None:
    first_human = FEW_SHOT_EXAMPLES[0]
    assert isinstance(first_human, HumanMessage)
    content = str(first_human.content)
    assert HUMAN_INPUT_INSTRUCTION.strip() in content
    assert '"raw_message": "Куда уходят деньги?"' in content


def test_select_few_shot_examples_respects_limit() -> None:
    from app.prompts.examples import select_few_shot_examples

    assert select_few_shot_examples(0) == []
    assert len(select_few_shot_examples(2)) == 4
    assert select_few_shot_examples(None) == FEW_SHOT_EXAMPLES


def test_build_prompt_messages_without_few_shot(monkeypatch) -> None:
    from app.core.config import Settings, get_settings

    monkeypatch.setenv("INTENT_PARSER_FEW_SHOT_LIMIT", "0")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.intent_parser_few_shot_limit == 0

    messages = build_prompt_messages(_request(), settings=settings)
    human_messages = [message for message in messages if isinstance(message, HumanMessage)]
    assert len(human_messages) == 1
    get_settings.cache_clear()
