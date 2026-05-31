"""Extract allowed numeric facts from analytics for output validation."""
from __future__ import annotations

import re
from typing import Any

from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.response_agent_result import AgentOutput

_NUMBER_PATTERN = re.compile(r"-?\d+(?:[.,]\d+)?")


def _add_number(values: set[str], raw: Any) -> None:
    if raw is None:
        return
    if isinstance(raw, bool):
        return
    if isinstance(raw, (int, float)):
        values.add(str(int(raw)) if float(raw).is_integer() else str(raw))
        values.add(str(abs(int(raw))) if float(raw).is_integer() else str(abs(float(raw))))
        return
    if isinstance(raw, str):
        for match in _NUMBER_PATTERN.findall(raw.replace(",", ".")):
            values.add(match.rstrip("0").rstrip(".") if "." in match else match)


def _walk(value: Any, values: set[str]) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _walk(item, values)
        return
    if isinstance(value, list):
        for item in value:
            _walk(item, values)
        return
    _add_number(values, value)


def extract_allowed_numbers(far: FinancialAnalysisResult) -> set[str]:
    allowed: set[str] = {"0", "1", "2", "3", "6", "12"}
    analysis = far.analysis_result
    _add_number(allowed, analysis.risk_score)
    _add_number(allowed, analysis.expected_savings)
    for fn_result in far.function_results.values():
        _walk(fn_result.result, allowed)
        _walk(fn_result.warnings, allowed)
    _walk(far.warnings, allowed)
    return allowed


def extract_allowed_numbers_from_agent_outputs(agent_outputs: list[AgentOutput]) -> set[str]:
    allowed: set[str] = set()
    for output in agent_outputs:
        _walk(output.model_dump(mode="json"), allowed)
    return allowed


def extract_answer_numbers(text: str) -> set[str]:
    numbers: set[str] = set()
    for match in _NUMBER_PATTERN.findall(text.replace(",", ".")):
        normalized = match.rstrip("0").rstrip(".") if "." in match else match
        numbers.add(normalized)
    return numbers
