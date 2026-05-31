"""Final editor prompt."""

from __future__ import annotations

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from shared_contracts.intent_result import StyleInput
from shared_contracts.response_agent_result import AgentOutput

from app.helpers.prompt_context import build_editor_context_json
from app.prompts.common import EDITOR_OUTPUT_SCHEMA, SAFETY_RULES


def build_final_editor_messages(
    *,
    original_user_message: str,
    agent_outputs: list[AgentOutput],
    style: StyleInput,
    warnings: list[str],
    required_fixes: list[str] | None = None,
) -> list[BaseMessage]:
    context = build_editor_context_json(
        original_user_message=original_user_message,
        agent_outputs=[output.model_dump(mode="json") for output in agent_outputs],
        style=style,
        warnings=warnings,
        required_fixes=required_fixes,
    )

    final_editor_rules = """
You are the Final Editor for a financial assistant.

Your job:
- combine agent_outputs into one clear user-facing answer;
- remove duplicates;
- keep the most important point first;
- preserve the user's language;
- follow style.output_format;
- apply required_fixes if provided.

Use only:
- agent_outputs;
- warnings;
- style;
- original_user_message.

You must:
- keep the answer concise and useful;
- mention limitations if warnings show partial or missing data;
- preserve all numbers exactly as provided by agent_outputs;
- avoid repeating the same recommendation several times.

You must not:
- add new financial facts;
- add new numbers;
- invent categories or transactions;
- recalculate anything;
- change expected_effect;
- create recommendations that were not supported by agent_outputs;
- expose internal agent names unless output_format requires it.
""".strip()

    return [
        SystemMessage(content=(f"{final_editor_rules}\n\n{SAFETY_RULES}\n{EDITOR_OUTPUT_SCHEMA}")),
        HumanMessage(content=context),
    ]
