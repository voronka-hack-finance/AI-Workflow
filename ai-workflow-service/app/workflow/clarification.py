"""Clarification detection and message extraction."""
from __future__ import annotations

from shared_contracts.common import CalculationMode, FunctionResultStatus
from shared_contracts.context_package import ContextPackage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import IntentParserResponse
from shared_contracts.response_agent_result import ResponseAgentResult

GENERIC_CLARIFICATION = "Нужны дополнительные данные для продолжения. Уточните запрос."


def intent_requires_clarification(response: IntentParserResponse) -> bool:
    return response.intent_result.clarification.required


def intent_clarification_question(response: IntentParserResponse) -> str:
    clarification = response.intent_result.clarification
    if clarification.question:
        return clarification.question
    if clarification.missing_fields:
        return f"Уточните: {', '.join(clarification.missing_fields)}."
    return GENERIC_CLARIFICATION


def context_requires_clarification(package: ContextPackage) -> bool:
    quality = package.data_quality
    if not quality.can_run_analytics:
        return True
    return quality.calculation_mode == CalculationMode.CLARIFICATION_REQUIRED


def context_clarification_question(package: ContextPackage) -> str:
    quality = package.data_quality
    parts: list[str] = []
    if quality.missing_hard_required_data:
        parts.append(f"Недостающие данные: {', '.join(quality.missing_hard_required_data)}.")
    if quality.missing_hard_required_fields:
        parts.append(f"Недостающие поля: {', '.join(quality.missing_hard_required_fields)}.")
    if quality.normalization_warnings:
        parts.append(quality.normalization_warnings[0])
    return " ".join(parts) if parts else GENERIC_CLARIFICATION


def analytics_requires_clarification(result: FinancialAnalysisResult) -> bool:
    for function_result in result.function_results.values():
        if function_result.status == FunctionResultStatus.NEEDS_CLARIFICATION:
            return True
        if function_result.status == "needs_clarification":
            return True
    return False


def analytics_clarification_question(result: FinancialAnalysisResult) -> str:
    for function_result in result.function_results.values():
        status = function_result.status
        if status in (FunctionResultStatus.NEEDS_CLARIFICATION, "needs_clarification"):
            warnings = function_result.warnings
            if warnings:
                return warnings[0]
            message = function_result.result.get("message")
            if isinstance(message, str) and message:
                return message
    if result.analysis_result.main_problem:
        return result.analysis_result.main_problem
    return GENERIC_CLARIFICATION


def response_agent_requires_clarification(result: ResponseAgentResult) -> bool:
    if not result.editor_output.final_answer.strip():
        return True
    if not result.input_validation.can_run_agents:
        return True
    if result.input_validation.validation_status == "needs_clarification":
        return True
    if result.output_validation.validation_status == "needs_clarification":
        return True
    if not result.output_validation.can_send_to_user:
        return True
    return False


def response_agent_clarification_question(result: ResponseAgentResult) -> str:
    if result.editor_output.final_answer:
        return result.editor_output.final_answer
    if result.input_validation.message:
        return result.input_validation.message
    for issue in result.output_validation.issues:
        return issue.message
    return GENERIC_CLARIFICATION
