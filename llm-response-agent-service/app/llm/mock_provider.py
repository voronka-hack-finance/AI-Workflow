"""Deterministic mock LLM provider for tests and CI."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage

from shared_contracts.common import ContentAgentName
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput


@dataclass
class MockCallContext:
    mode: str = "agent"
    agent_name: str | None = None
    intent: IntentResult | None = None
    far: FinancialAnalysisResult | None = None
    constraints: ConstraintsInput | None = None
    style: StyleInput | None = None
    original_user_message: str = ""
    agent_outputs: list[dict[str, Any]] = field(default_factory=list)


def _collect_facts(far: FinancialAnalysisResult) -> list[str]:
    facts: list[str] = []
    analysis = far.analysis_result
    if analysis.main_problem:
        facts.append(analysis.main_problem)
    if analysis.risk_level:
        facts.append(f"risk_level={analysis.risk_level}")
    if analysis.expected_savings:
        facts.append(f"expected_savings={analysis.expected_savings}")
    for name, fn_result in far.function_results.items():
        if fn_result.status == "success" and fn_result.result:
            facts.append(f"{name}: {json.dumps(fn_result.result, ensure_ascii=False)}")
    return facts[:5]


def _build_agent_payload(ctx: MockCallContext) -> dict[str, Any]:
    far = ctx.far
    facts = _collect_facts(far) if far else []
    expected_savings = far.analysis_result.expected_savings if far else None
    agent_name = ctx.agent_name or ContentAgentName.BUDGET_PLANNER

    summaries = {
        ContentAgentName.SAFETY: "Финансовая подушка и риски требуют внимания.",
        ContentAgentName.SPENDING_DETECTIVE: "Основные траты сосредоточены в нескольких категориях.",
        ContentAgentName.GROWTH: "Прогресс к цели можно ускорить за счёт регулярных накоплений.",
        ContentAgentName.BUDGET_PLANNER: "Есть возможность оптимизировать бюджет без резких сокращений.",
        ContentAgentName.HABIT_COACH: "Начните с небольших шагов и закрепите привычку контроля расходов.",
    }

    return {
        "agent_name": str(agent_name),
        "status": "success",
        "priority": "medium",
        "used_facts": facts[:3],
        "summary": summaries.get(str(agent_name), "Анализ выполнен."),
        "facts": facts[:3],
        "recommendations": [
            {
                "title": "Следующий шаг",
                "description": "Сфокусируйтесь на главной рекомендации из анализа.",
                "expected_effect": expected_savings or None,
            }
        ],
        "warnings": list(far.warnings[:2]) if far else [],
        "confidence": "high",
    }


def _build_editor_payload(ctx: MockCallContext) -> dict[str, Any]:
    parts = [f"Запрос: {ctx.original_user_message}"]
    for output in ctx.agent_outputs:
        summary = output.get("summary") or ""
        if summary:
            parts.append(summary)
    if len(parts) == 1:
        parts.append("Анализ выполнен. Данных для детального ответа пока недостаточно.")
    return {
        "format": ctx.style.output_format if ctx.style else "chat_text",
        "final_answer": "\n\n".join(parts),
    }


class MockProvider:
    def __init__(self) -> None:
        self._context = MockCallContext()

    def bind_call(self, **kwargs: Any) -> MockProvider:
        merged = {**self._context.__dict__, **kwargs}
        clone = MockProvider()
        clone._context = MockCallContext(**merged)
        return clone

    async def generate(self, messages: list[BaseMessage]) -> str:
        del messages
        ctx = self._context
        if ctx.mode == "editor":
            return json.dumps(_build_editor_payload(ctx), ensure_ascii=False)
        return json.dumps(_build_agent_payload(ctx), ensure_ascii=False)

    @staticmethod
    def detect_mode(messages: list[BaseMessage]) -> str:
        for message in messages:
            content = message.content if isinstance(message.content, str) else str(message.content)
            if "final editor" in content.lower() or "final_answer" in content.lower():
                return "editor"
        return "agent"

    @staticmethod
    def extract_user_message(messages: list[BaseMessage]) -> str:
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                content = message.content
                return content if isinstance(content, str) else str(content)
        return ""
