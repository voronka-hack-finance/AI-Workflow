"""Final editor."""
from __future__ import annotations

from app.llm.output_parser import parse_editor_output
from app.llm.mock_provider import MockProvider
from app.prompts.final_editor_prompt import build_final_editor_messages
from shared_contracts.response_agent_result import AgentOutput, EditorOutput, InputValidationResult
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import StyleInput


class FinalEditor:
    def compose_safe_message(
        self,
        *,
        input_validation: InputValidationResult,
        style: StyleInput,
    ) -> EditorOutput:
        message = input_validation.message or "Не удалось сформировать ответ."
        if input_validation.validation_status == "needs_clarification":
            message = f"{message} Пожалуйста, уточните запрос."
        elif input_validation.validation_status == "error":
            message = "Сейчас не удалось подготовить ответ. Попробуйте повторить запрос позже."
        return EditorOutput(format=style.output_format, final_answer=message)

    async def compose(
        self,
        *,
        original_user_message: str,
        agent_outputs: list[AgentOutput],
        style: StyleInput,
        warnings: list[str],
        provider: LLMProvider,
        required_fixes: list[str] | None = None,
    ) -> EditorOutput:
        messages = build_final_editor_messages(
            original_user_message=original_user_message,
            agent_outputs=agent_outputs,
            style=style,
            warnings=warnings,
            required_fixes=required_fixes,
        )

        active_provider = provider
        if isinstance(provider, MockProvider):
            active_provider = provider.bind_call(
                mode="editor",
                original_user_message=original_user_message,
                agent_outputs=[output.model_dump(mode="json") for output in agent_outputs],
                style=style,
            )

        raw_output = await active_provider.generate(messages)
        return parse_editor_output(raw_output, style)

    async def compose_fallback(
        self,
        *,
        original_user_message: str,
        agent_outputs: list[AgentOutput],
        style: StyleInput,
        last_editor_answer: str | None = None,
    ) -> EditorOutput:
        del original_user_message
        return self.compose_degraded(
            agent_outputs=agent_outputs,
            style=style,
            last_editor_answer=last_editor_answer,
        )

    def compose_degraded(
        self,
        *,
        agent_outputs: list[AgentOutput],
        style: StyleInput,
        last_editor_answer: str | None = None,
    ) -> EditorOutput:
        """User-facing answer when editor validation fails — prefer last editor draft."""
        if last_editor_answer:
            cleaned = last_editor_answer.strip()
            if len(cleaned) >= 80 and not cleaned.startswith("Запрос:"):
                return EditorOutput(format=style.output_format, final_answer=cleaned)

        parts: list[str] = []
        for output in agent_outputs:
            if output.summary.strip():
                parts.append(output.summary.strip())
            for fact in output.facts[:5]:
                fact_text = fact.strip()
                if fact_text:
                    parts.append(f"• {fact_text}")
            for recommendation in output.recommendations[:3]:
                title = recommendation.title.strip()
                description = recommendation.description.strip()
                if title and description:
                    parts.append(f"**{title}**: {description}")
                elif description:
                    parts.append(description)

        if not parts:
            parts.append("Анализ выполнен. Попробуйте уточнить запрос, если нужны детали.")

        return EditorOutput(format=style.output_format, final_answer="\n\n".join(parts))
