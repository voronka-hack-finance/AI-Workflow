"""Dev-mode final answer builder until full ResponseAgentService is wired."""
from __future__ import annotations

from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import IntentResult


def build_dev_final_answer(
    *,
    original_user_message: str,
    intent_result: IntentResult,
    financial_analysis_result: FinancialAnalysisResult,
) -> str:
    del financial_analysis_result

    lines = [f"Запрос: {original_user_message}"]

    functions = intent_result.requested_functions or [intent_result.primary_intent]
    lines.append(f"Выполненный анализ: {', '.join(functions)}.")

    if intent_result.focus.categories:
        lines.append(f"Категории: {', '.join(intent_result.focus.categories)}.")
    elif intent_result.focus.category:
        lines.append(f"Категория: {intent_result.focus.category}.")
    if intent_result.period.type and intent_result.period.type != "unknown":
        lines.append(f"Период: {intent_result.period.type}.")

    lines.extend(
        [
            "",
            "Ответ сформирован в dev-режиме: analytics и response agent пока возвращают заглушки.",
            "Pipeline intent → context → analytics отработал успешно.",
        ]
    )
    return "\n".join(lines)
