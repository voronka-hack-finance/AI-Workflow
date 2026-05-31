"""Habit coach agent prompt."""

from __future__ import annotations

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput

from app.helpers.prompt_context import build_agent_context_json
from app.prompts.common import AGENT_OUTPUT_SCHEMA, SAFETY_RULES


def build_habit_coach_messages(
    *,
    intent: IntentResult,
    far: FinancialAnalysisResult,
    constraints: ConstraintsInput,
    style: StyleInput,
    original_user_message: str,
) -> list[BaseMessage]:
    context = build_agent_context_json(
        agent_name="habit_coach",
        intent=intent,
        far=far,
        constraints=constraints,
        style=style,
        original_user_message=original_user_message,
    )

    habit_agent_rules = """
You are the habit_coach content agent.

Your focus:
- simple next actions;
- weekly habits;
- practical steps;
- behavior changes based on analytics.

Use mainly these analytics facts if present:
- action_plan
- budget_recommendation
- spending_leak_detection
- analysis_result.problem_tags
- analysis_result.recommendation_type
- analysis_result.expected_savings
- financial_analysis_result.warnings
- style
- constraints

You must:
- give 2-4 practical actions;
- keep actions simple if style.difficulty is easy;
- be stricter only if style.agent_style is strict or max_cut_level allows it;
- use expected_effect only from analytics JSON or null.

You must not:
- create too many actions;
- invent expected savings;
- ignore protected_categories;
- shame the user;
- make the plan unrealistically strict.
""".strip()

    return [
        SystemMessage(content=(f"{habit_agent_rules}\n\n{SAFETY_RULES}\n{AGENT_OUTPUT_SCHEMA}")),
        HumanMessage(content=context),
    ]
