"""Budget planner agent prompt."""

from __future__ import annotations

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput

from app.helpers.prompt_context import build_agent_context_json
from app.prompts.common import AGENT_OUTPUT_SCHEMA, SAFETY_RULES


def build_budget_planner_messages(
    *,
    intent: IntentResult,
    far: FinancialAnalysisResult,
    constraints: ConstraintsInput,
    style: StyleInput,
    original_user_message: str,
) -> list[BaseMessage]:
    context = build_agent_context_json(
        agent_name="budget_planner",
        intent=intent,
        far=far,
        constraints=constraints,
        style=style,
        original_user_message=original_user_message,
    )

    budget_agent_rules = """
You are the budget_planner content agent.

Your focus:
- budget recommendation;
- spending plan;
- daily/category limits if already calculated;
- safe optimization of expenses.

Use mainly these analytics facts if present:
- budget_recommendation
- budget_plan
- cashflow_analysis
- expense_breakdown
- income_analysis
- spending_leak_detection
- analysis_result.risk_level
- analysis_result.category_to_optimize
- analysis_result.expected_savings
- constraints

You must:
- explain the recommended budget direction;
- suggest cuts only for allowed or optimizable categories;
- keep recommendations realistic and not too strict unless style/constraints allow it;
- use expected_savings only if analytics JSON provides it.

You must not:
- invent mandatory expenses;
- invent daily limit;
- cut protected_categories;
- create a strict plan when max_cut_level is low;
- change risk_level or expected_savings.
""".strip()

    return [
        SystemMessage(content=(f"{budget_agent_rules}\n\n{SAFETY_RULES}\n{AGENT_OUTPUT_SCHEMA}")),
        HumanMessage(content=context),
    ]
