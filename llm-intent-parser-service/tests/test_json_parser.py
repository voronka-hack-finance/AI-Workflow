"""JSON parser tests."""
import pytest

from app.core.errors import LLMParseError
from app.parser.json_parser import (
    extract_first_json_object,
    parse_llm_json,
    strip_markdown_fences,
)


def test_strip_markdown_fences() -> None:
    raw = '```json\n{"primary_intent":"expense_breakdown"}\n```'
    assert strip_markdown_fences(raw) == '{"primary_intent":"expense_breakdown"}'


def test_parse_valid_json() -> None:
    payload = parse_llm_json('{"requested_functions":["expense_breakdown"]}')
    assert payload["requested_functions"] == ["expense_breakdown"]


def test_parse_wrapped_intent_result() -> None:
    payload = parse_llm_json('{"intent_result":{"requested_functions":["goal_analysis"]}}')
    assert payload["requested_functions"] == ["goal_analysis"]


def test_parse_json_with_prefix_text() -> None:
    raw = 'Here is the JSON:\n{"primary_intent":"expense_breakdown","requested_functions":["expense_breakdown"]}'
    payload = parse_llm_json(raw)
    assert payload["primary_intent"] == "expense_breakdown"


def test_parse_json_with_prefix_and_suffix_text() -> None:
    raw = (
        "Some text before\n"
        '{"primary_intent":"budget_recommendation","requested_functions":["budget_recommendation"]}\n'
        "Some text after"
    )
    payload = parse_llm_json(raw)
    assert payload["requested_functions"] == ["budget_recommendation"]


def test_extract_first_json_object_from_fenced_block() -> None:
    raw = '```json\n{"primary_intent":"goal_analysis"}\n```'
    payload = extract_first_json_object(raw)
    assert payload["primary_intent"] == "goal_analysis"


def test_parse_invalid_json_raises() -> None:
    with pytest.raises(LLMParseError):
        parse_llm_json("{not-json")
