"""Shared test fixtures."""
from __future__ import annotations

import os

import pytest

os.environ.setdefault("AI_WORKFLOW_ENABLE_RABBITMQ_CONSUMER", "false")

from app.clients.mock_backend_chat_client import MockBackendChatClient
from app.schemas.workflow_task import WorkflowTask
from app.workflow.orchestrator import WorkflowOrchestrator
from shared_contracts.common import FunctionResultStatus
from shared_contracts.context_package import ContextPackage, DataQuality
from shared_contracts.financial_analysis_result import (
    FinancialAnalysisMetadata,
    FinancialAnalysisResult,
    FunctionResult,
    FunctionResultMetadata,
)
from shared_contracts.intent_result import (
    ClarificationInput,
    IntentParserResponse,
    IntentResult,
    PeriodInput,
)
from shared_contracts.response_agent_result import (
    AgentRoutingResult,
    EditorOutput,
    InputValidationResult,
    OutputValidationResult,
    ResponseAgentInput,
    ResponseAgentResult,
)


def sample_task() -> WorkflowTask:
    return WorkflowTask(
        request_id="req_001",
        workflow_run_id="run_001",
        user_id="user_123",
        chat_id="chat_001",
        message_id="msg_001",
        raw_message="Дай рекомендацию по бюджету на месяц.",
        current_date="2026-05-29",
        timezone="Europe/Moscow",
        created_at="2026-05-29T12:00:00Z",
    )


@pytest.fixture
def backend_chat() -> MockBackendChatClient:
    return MockBackendChatClient()


@pytest.fixture
def task() -> WorkflowTask:
    return sample_task()


@pytest.fixture
def orchestrator(backend_chat: MockBackendChatClient) -> WorkflowOrchestrator:
    return WorkflowOrchestrator(backend_chat=backend_chat)


def minimal_intent_response(*, clarification_required: bool = False) -> IntentParserResponse:
    return IntentParserResponse(
        request_id="req_001",
        user_id="user_123",
        chat_id="chat_001",
        raw_message="Дай рекомендацию по бюджету на месяц.",
        intent_result=IntentResult(
            primary_intent="budget_recommendation",
            clarification=ClarificationInput(
                required=clarification_required,
                question="Какой период вас интересует?" if clarification_required else None,
            ),
        ),
    )


def minimal_context_package(*, can_run_analytics: bool = True) -> ContextPackage:
    from shared_contracts.context_package import (
        AppliedFilters,
        ContextBuilderMetadata,
        ContextPackageMetadata,
        ResolvedComparison,
        ResolvedPeriod,
        SourceMessage,
    )

    return ContextPackage(
        request_id="req_001",
        workflow_run_id="run_001",
        user_id="user_123",
        chat_id="chat_001",
        source_message=SourceMessage(
            raw_message="Дай рекомендацию по бюджету на месяц.",
            current_date="2026-05-29",
            timezone="Europe/Moscow",
        ),
        intent_result=IntentResult(primary_intent="budget_recommendation"),
        context_builder=ContextBuilderMetadata(
            resolved_period=ResolvedPeriod(type="current_month"),
            resolved_comparison=ResolvedComparison(enabled=False),
            applied_filters=AppliedFilters(period={"start_date": None, "end_date": None}),
        ),
        data_quality=DataQuality(
            can_run_analytics=can_run_analytics,
            missing_hard_required_data=[] if can_run_analytics else ["transactions"],
        ),
        metadata=ContextPackageMetadata(created_at="2026-05-29T12:00:00Z"),
    )


def minimal_analysis_result(*, needs_clarification: bool = False) -> FinancialAnalysisResult:
    status = (
        FunctionResultStatus.NEEDS_CLARIFICATION
        if needs_clarification
        else FunctionResultStatus.SUCCESS
    )
    return FinancialAnalysisResult(
        request_id="req_001",
        user_id="user_123",
        period=PeriodInput(type="current_month"),
        function_results={
            "budget_recommendation": FunctionResult(
                function_name="budget_recommendation",
                status=status,
                warnings=["Нужны данные о цели"] if needs_clarification else [],
                metadata=FunctionResultMetadata(calculated_at="2026-05-29T12:00:00Z"),
            )
        },
        metadata=FinancialAnalysisMetadata(calculated_at="2026-05-29T12:00:00Z"),
    )


def minimal_response_result(
    *,
    final_answer: str = "Вот рекомендация по бюджету.",
    needs_clarification: bool = False,
) -> ResponseAgentResult:
    analysis = minimal_analysis_result()
    return ResponseAgentResult(
        request_id="req_001",
        workflow_run_id="run_001",
        input=ResponseAgentInput(
            original_user_message="Дай рекомендацию по бюджету на месяц.",
            intent_result=IntentResult(primary_intent="budget_recommendation"),
            financial_analysis_result=analysis,
        ),
        input_validation=InputValidationResult(
            validation_status="needs_clarification" if needs_clarification else "passed",
            can_run_agents=not needs_clarification,
        ),
        routing=AgentRoutingResult(routing_status="success"),
        editor_output=EditorOutput(final_answer=final_answer),
        output_validation=OutputValidationResult(
            validation_status="needs_clarification" if needs_clarification else "passed",
            can_send_to_user=not needs_clarification,
        ),
    )
