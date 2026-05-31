"""Agent router."""
from __future__ import annotations

from shared_contracts.common import ContentAgentName
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult
from shared_contracts.response_agent_result import AgentRoutingResult

from app.core.config import Settings, get_settings
from app.helpers.message_hints import has_action_plan_hints

_EXPENSE_FUNCTIONS = frozenset(
    {
        "expense_breakdown",
        "spending_leak_detection",
        "category_analysis",
        "period_analysis",
        "transfer_analysis",
    }
)
_INCOME_FUNCTIONS = frozenset({"income_analysis"})
_CASHFLOW_FUNCTIONS = frozenset({"cashflow_analysis"})
_BUDGET_FUNCTIONS = frozenset({"budget_plan", "budget_recommendation"})
_GROWTH_RECOMMENDATION_HINTS = ("goal", "save", "saving", "накоп")


class AgentRouter:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def select(
        self,
        *,
        intent: IntentResult,
        financial_analysis_result: FinancialAnalysisResult,
        constraints: ConstraintsInput,
        original_user_message: str,
    ) -> AgentRoutingResult:
        del constraints
        requested = set(intent.requested_functions or [])
        if intent.primary_intent:
            requested.add(intent.primary_intent)

        tags = set(financial_analysis_result.analysis_result.problem_tags or [])
        risk_level = str(financial_analysis_result.analysis_result.risk_level or "").lower()
        recommendation_type = (financial_analysis_result.analysis_result.recommendation_type or "").lower()

        selected: list[ContentAgentName] = []
        reason: dict[str, list[str]] = {}

        if (
            "emergency_fund_analysis" in requested
            or "low_emergency_fund" in tags
            or risk_level in {"high", "critical"}
        ):
            selected.append(ContentAgentName.SAFETY)
            reason["safety"] = ["risk_or_emergency_fund"]

        if requested & _EXPENSE_FUNCTIONS or tags & {
            "high_marketplace_spending",
            "high_food_outside_spending",
        }:
            selected.append(ContentAgentName.SPENDING_DETECTIVE)
            reason["spending_detective"] = ["expense_functions_or_tags"]

        if requested & _INCOME_FUNCTIONS:
            selected.append(ContentAgentName.GROWTH)
            reason["growth"] = ["income_analysis"]

        if requested & _CASHFLOW_FUNCTIONS:
            selected.append(ContentAgentName.SAFETY)
            reason.setdefault("safety", []).append("cashflow_analysis")

        if "goal_analysis" in requested or any(
            hint in recommendation_type for hint in _GROWTH_RECOMMENDATION_HINTS
        ):
            selected.append(ContentAgentName.GROWTH)
            reason["growth"] = ["goal_or_saving_recommendation"]

        if requested & _BUDGET_FUNCTIONS:
            selected.append(ContentAgentName.BUDGET_PLANNER)
            reason["budget_planner"] = ["budget_functions"]

        if "action_plan" in requested or has_action_plan_hints(original_user_message):
            selected.append(ContentAgentName.HABIT_COACH)
            reason["habit_coach"] = ["action_plan_or_message_hints"]

        deduped: list[ContentAgentName] = []
        for agent in selected:
            if agent not in deduped:
                deduped.append(agent)

        max_agents = self._settings.response_agent_max_selected_agents
        limited = deduped[:max_agents]

        if not limited:
            return AgentRoutingResult(
                routing_status="no_agents",
                selected_agents=[],
                primary_agent=None,
                execution_mode="single",
                reason=reason,
            )

        return AgentRoutingResult(
            routing_status="success",
            selected_agents=limited,
            primary_agent=limited[0],
            execution_mode="parallel" if len(limited) > 1 else "single",
            reason=reason,
        )
