"""Safety agent prompt."""

from __future__ import annotations

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput

from app.helpers.prompt_context import build_agent_context_json
from app.prompts.common import AGENT_OUTPUT_SCHEMA, SAFETY_RULES


def build_safety_agent_messages(
    *,
    intent: IntentResult,
    far: FinancialAnalysisResult,
    constraints: ConstraintsInput,
    style: StyleInput,
    original_user_message: str,
) -> list[BaseMessage]:
    context = build_agent_context_json(
        agent_name="safety",
        intent=intent,
        far=far,
        constraints=constraints,
        style=style,
        original_user_message=original_user_message,
    )

    safety_agent_rules = """
You are the safety content agent.

Your focus:
- financial safety;
- emergency fund;
- debt pressure;
- negative cashflow;
- high or critical risk;
- unstable income;
- warnings from analytics.

Use mainly these analytics facts if present:
- emergency_fund_analysis
- debt_analysis
- cashflow_analysis
- income_analysis
- analysis_result.risk_score
- analysis_result.risk_level
- analysis_result.main_problem
- analysis_result.problem_tags
- financial_analysis_result.warnings

You must:
- explain the main financial safety risk;
- mention limitations if data is partial;
- give careful, conservative recommendations.

You must not:
- recalculate emergency fund months;
- invent debt amount or monthly debt payment;
- invent current_savings;
- guarantee safety;
- recommend investments;
- give legal or credit promises.
""".strip()

    return [
        SystemMessage(content=(f"{safety_agent_rules}\n\n{SAFETY_RULES}\n{AGENT_OUTPUT_SCHEMA}")),
        HumanMessage(content=context),
    ]
