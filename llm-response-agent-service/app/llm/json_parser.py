"""Parse raw LLM JSON output."""
from __future__ import annotations

import json
import re
from json import JSONDecoder
from typing import Any

from app.core.errors import LLMParseError

_JSON_FENCE_PATTERN = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
_JSON_DECODER = JSONDecoder()


def strip_markdown_fences(text: str) -> str:
    stripped = text.strip()
    match = _JSON_FENCE_PATTERN.search(stripped)
    if match:
        return match.group(1).strip()
    return stripped


def extract_first_json_object(text: str) -> dict[str, Any]:
    cleaned = strip_markdown_fences(text)
    search_from = 0
    while search_from < len(cleaned):
        start = cleaned.find("{", search_from)
        if start == -1:
            break
        try:
            payload, _end = _JSON_DECODER.raw_decode(cleaned, start)
        except json.JSONDecodeError:
            search_from = start + 1
            continue
        if isinstance(payload, dict):
            return payload
        search_from = start + 1

    raise LLMParseError("No valid JSON object found in LLM output")


def parse_llm_json(raw_text: str) -> dict[str, Any]:
    return extract_first_json_object(raw_text)
