"""Parse LLM outputs with JSON-first and plain-text fallback for local models."""
from __future__ import annotations

from app.core.errors import LLMParseError
from app.llm.json_parser import parse_llm_json
from shared_contracts.intent_result import StyleInput
from shared_contracts.response_agent_result import AgentOutput, EditorOutput

_THINK_OPEN = "<" + "think>"
_THINK_CLOSE = "<" + "/think>"


def _strip_thinking_blocks(text: str) -> str:
    cleaned = text
    while _THINK_OPEN in cleaned:
        start = cleaned.find(_THINK_OPEN)
        end = cleaned.find(_THINK_CLOSE, start)
        if end == -1:
            cleaned = cleaned[:start]
            break
        cleaned = cleaned[:start] + cleaned[end + len(_THINK_CLOSE) :]
    return cleaned.strip()


def parse_agent_output(raw_text: str, agent_name: str) -> AgentOutput:
    cleaned = _strip_thinking_blocks(raw_text)
    if not cleaned:
        raise LLMParseError(f"Empty agent output for {agent_name}")

    try:
        payload = parse_llm_json(cleaned)
        payload.setdefault("agent_name", agent_name)
        return AgentOutput.model_validate(payload)
    except LLMParseError:
        return AgentOutput(
            agent_name=agent_name,
            status="success",
            summary=cleaned[:1000],
            facts=[cleaned[:500]] if cleaned else [],
            confidence="medium",
        )


def parse_editor_output(raw_text: str, style: StyleInput) -> EditorOutput:
    cleaned = _strip_thinking_blocks(raw_text)
    if not cleaned:
        raise LLMParseError("Empty final editor output")

    try:
        payload = parse_llm_json(cleaned)
        return EditorOutput.model_validate(payload)
    except LLMParseError:
        return EditorOutput(format=style.output_format, final_answer=cleaned)
