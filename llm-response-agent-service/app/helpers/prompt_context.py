"""Helpers for building compact analytics context for prompts."""
from __future__ import annotations

import json
from typing import Any

from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput


def build_agent_context_json(
    *,
    agent_name: str,
    intent: IntentResult,
    far: FinancialAnalysisResult,
    constraints: ConstraintsInput,
    style: StyleInput,
    original_user_message: str,
) -> str:
    function_results: dict[str, Any] = {}
    for name, result in far.function_results.items():
        function_results[name] = {
            "status": result.status,
            "result": result.result,
            "warnings": result.warnings,
        }

    payload = {
        "agent_name": agent_name,
        "original_user_message": original_user_message,
        "intent": {
            "primary_intent": intent.primary_intent,
            "requested_functions": intent.requested_functions,
            "goal": intent.goal.model_dump(mode="json"),
        },
        "analysis_result": far.analysis_result.model_dump(mode="json"),
        "function_results": function_results,
        "warnings": far.warnings,
        "constraints": constraints.model_dump(mode="json"),
        "style": style.model_dump(mode="json"),
    }
    return json.dumps(payload, ensure_ascii=False)


def build_editor_context_json(
    *,
    original_user_message: str,
    agent_outputs: list[dict[str, Any]],
    style: StyleInput,
    warnings: list[str],
    required_fixes: list[str] | None = None,
) -> str:
    payload = {
        "original_user_message": original_user_message,
        "agent_outputs": agent_outputs,
        "style": style.model_dump(mode="json"),
        "warnings": warnings,
        "required_fixes": required_fixes or [],
    }
    return json.dumps(payload, ensure_ascii=False)
