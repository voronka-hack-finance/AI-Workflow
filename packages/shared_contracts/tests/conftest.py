"""Shared fixtures for contract tests."""
from __future__ import annotations

from shared_contracts.common import FunctionResultStatus
from shared_contracts.context_package import (
    AnalyticsRequest,
    AppliedFilters,
    ContextBuilderMetadata,
    ContextPackage,
    ContextPackageData,
    ContextPackageMetadata,
    ResolvedComparison,
    ResolvedPeriod,
    SourceMessage,
)
from shared_contracts.financial_analysis_result import (
    AnalysisResult,
    FinancialAnalysisMetadata,
    FinancialAnalysisResult,
    FunctionResult,
    FunctionResultMetadata,
)
from shared_contracts.intent_result import IntentParserResponse, IntentResult
from shared_contracts.normalized_data import CategoryProfile, TransactionNormalized
from shared_contracts.response_agent_result import (
    AgentOutput,
    AgentRoutingResult,
    EditorOutput,
    InputValidationResult,
    OutputValidationResult,
    ResponseAgentInput,
    ResponseAgentResult,
)


def minimal_intent_result() -> IntentResult:
    return IntentResult(
        primary_intent="budget_recommendation",
        intents=["budget_recommendation"],
        intent_confidence=0.92,
        requested_functions=["budget_recommendation"],
    )


def minimal_intent_parser_response() -> IntentParserResponse:
    return IntentParserResponse(
        request_id="req_001",
        user_id="user_123",
        chat_id="chat_001",
        raw_message="Дай рекомендацию по бюджету.",
        intent_result=minimal_intent_result(),
    )


def minimal_context_builder_metadata() -> ContextBuilderMetadata:
    return ContextBuilderMetadata(
        requested_functions=["budget_recommendation"],
        expanded_functions=["income_analysis", "budget_recommendation"],
        resolved_period=ResolvedPeriod(
            type="current_month",
            start_date="2026-05-01",
            end_date="2026-05-31",
        ),
        resolved_comparison=ResolvedComparison(enabled=False),
        applied_filters=AppliedFilters(
            period={"start_date": "2026-05-01", "end_date": "2026-05-31"},
            direction="all",
        ),
    )


def minimal_context_package_data() -> ContextPackageData:
    return ContextPackageData(
        category_profiles=[
            CategoryProfile(
                category="Фастфуд",
                category_group="food_outside",
            )
        ]
    )


def minimal_context_package() -> ContextPackage:
    return ContextPackage(
        request_id="req_001",
        workflow_run_id="run_001",
        user_id="user_123",
        chat_id="chat_001",
        source_message=SourceMessage(
            raw_message="Дай рекомендацию по бюджету.",
            current_date="2026-05-29",
            timezone="Europe/Moscow",
        ),
        intent_result=minimal_intent_result(),
        context_builder=minimal_context_builder_metadata(),
        data=minimal_context_package_data(),
        analytics_request=AnalyticsRequest(
            functions_to_execute=["income_analysis", "budget_recommendation"]
        ),
        metadata=ContextPackageMetadata(created_at="2026-05-29T12:00:00Z"),
    )


def minimal_financial_analysis_result() -> FinancialAnalysisResult:
    return FinancialAnalysisResult(
        request_id="req_001",
        user_id="user_123",
        period={"type": "current_month", "start_date": "2026-05-01", "end_date": "2026-05-31"},
        executed_functions=["budget_recommendation"],
        function_results={
            "budget_recommendation": FunctionResult(
                function_name="budget_recommendation",
                status=FunctionResultStatus.SUCCESS,
                result={"expected_savings": 6000},
                metadata=FunctionResultMetadata(calculated_at="2026-05-29T12:00:00Z"),
            )
        },
        analysis_result=AnalysisResult(expected_savings=6000),
        metadata=FinancialAnalysisMetadata(calculated_at="2026-05-29T12:00:00Z"),
    )


def minimal_response_agent_result() -> ResponseAgentResult:
    intent = minimal_intent_result()
    financial = minimal_financial_analysis_result()
    return ResponseAgentResult(
        request_id="req_001",
        workflow_run_id="run_001",
        input=ResponseAgentInput(
            original_user_message="Дай рекомендацию по бюджету.",
            intent_result=intent,
            financial_analysis_result=financial,
        ),
        input_validation=InputValidationResult(validation_status="passed"),
        routing=AgentRoutingResult(
            routing_status="success",
            selected_agents=["budget_planner"],
            primary_agent="budget_planner",
        ),
        agent_outputs=[
            AgentOutput(
                agent_name="budget_planner",
                status="success",
                summary="Рекомендация готова.",
            )
        ],
        editor_output=EditorOutput(final_answer="Вот рекомендация по бюджету."),
        output_validation=OutputValidationResult(validation_status="passed"),
    )


def minimal_transaction() -> TransactionNormalized:
    return TransactionNormalized(
        transaction_id="tx_1",
        operation_datetime="2026-05-10T18:25:00",
        operation_amount=-1294,
        operation_currency="RUB",
        direction="expense",
    )
