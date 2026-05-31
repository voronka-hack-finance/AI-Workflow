"""Spending detective agent prompt."""

from __future__ import annotations

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput

from app.helpers.prompt_context import build_agent_context_json
from app.prompts.common import AGENT_OUTPUT_SCHEMA, SAFETY_RULES


def build_spending_detective_messages(
    *,
    intent: IntentResult,
    far: FinancialAnalysisResult,
    constraints: ConstraintsInput,
    style: StyleInput,
    original_user_message: str,
) -> list[BaseMessage]:
    context = build_agent_context_json(
        agent_name="spending_detective",
        intent=intent,
        far=far,
        constraints=constraints,
        style=style,
        original_user_message=original_user_message,
    )

    spending_agent_rules = """
You are the spending_detective content agent.

Your focus:
- where money goes;
- expense structure;
- category analysis;
- spending leaks;
- suspicious or unclear transfers if relevant.

Use mainly these analytics facts if present:
- expense_breakdown
- category_analysis
- spending_leak_detection
- transfer_analysis
- period_analysis.top_categories
- period_analysis.top_merchants
- analysis_result.category_to_optimize
- analysis_result.expected_savings
- financial_analysis_result.warnings

You must:
- identify the main spending pattern;
- name only categories/merchants that exist in analytics JSON;
- explain avoidable or suspicious spending only if analytics supports it;
- respect protected_categories.

You must not:
- say that all spending is bad;
- recommend cutting protected categories;
- invent categories;
- invent savings amount;
- recalculate category shares.
""".strip()

    return [
        SystemMessage(content=(f"{spending_agent_rules}\n\n{SAFETY_RULES}\n{AGENT_OUTPUT_SCHEMA}")),
        HumanMessage(content=context),
    ]
