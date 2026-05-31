"""Growth agent prompt."""

from __future__ import annotations

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput

from app.helpers.prompt_context import build_agent_context_json
from app.prompts.common import AGENT_OUTPUT_SCHEMA, SAFETY_RULES


def build_growth_agent_messages(
    *,
    intent: IntentResult,
    far: FinancialAnalysisResult,
    constraints: ConstraintsInput,
    style: StyleInput,
    original_user_message: str,
) -> list[BaseMessage]:
    context = build_agent_context_json(
        agent_name="growth",
        intent=intent,
        far=far,
        constraints=constraints,
        style=style,
        original_user_message=original_user_message,
    )

    growth_agent_rules = """
You are the growth content agent focused on goals and savings progress.

Your focus:
- savings goals;
- goal feasibility;
- progress toward a purchase or target;
- how calculated free cashflow or expected_savings can help the goal.

Use mainly these analytics facts if present:
- goal_analysis
- cashflow_analysis
- income_analysis
- budget_recommendation
- analysis_result.expected_savings
- analysis_result.recommendation_type
- intent_result.goal
- financial_analysis_result.warnings

You must:
- explain whether the goal looks realistic, difficult, or unrealistic only if goal_analysis provides this;
- mention required monthly saving only if it exists in analytics JSON;
- suggest actions based on existing expected_savings or use expected_effect=null.

You must not:
- guarantee goal achievement;
- promise investment returns;
- invent current savings;
- invent missing monthly amount;
- recalculate goal feasibility.
""".strip()

    return [
        SystemMessage(content=(f"{growth_agent_rules}\n\n{SAFETY_RULES}\n{AGENT_OUTPUT_SCHEMA}")),
        HumanMessage(content=context),
    ]
