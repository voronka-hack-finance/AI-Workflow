"""Base response agent."""
from __future__ import annotations

from abc import ABC, abstractmethod
from langchain_core.messages import BaseMessage

from app.llm.output_parser import parse_agent_output
from app.llm.mock_provider import MockProvider
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput
from shared_contracts.response_agent_result import AgentOutput


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def build_messages(
        self,
        *,
        intent: IntentResult,
        far: FinancialAnalysisResult,
        constraints: ConstraintsInput,
        style: StyleInput,
        original_user_message: str,
    ) -> list[BaseMessage]:
        raise NotImplementedError

    async def run(
        self,
        *,
        intent: IntentResult,
        far: FinancialAnalysisResult,
        constraints: ConstraintsInput,
        style: StyleInput,
        original_user_message: str,
        provider: LLMProvider,
    ) -> AgentOutput:
        messages = self.build_messages(
            intent=intent,
            far=far,
            constraints=constraints,
            style=style,
            original_user_message=original_user_message,
        )

        active_provider = provider
        if isinstance(provider, MockProvider):
            active_provider = provider.bind_call(
                mode="agent",
                agent_name=self.name,
                intent=intent,
                far=far,
                constraints=constraints,
                style=style,
                original_user_message=original_user_message,
            )

        raw_output = await active_provider.generate(messages)
        return parse_agent_output(raw_output, self.name)
