"""Response agent result builder."""
from __future__ import annotations

from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput
from shared_contracts.response_agent_result import (
    AgentOutput,
    AgentRoutingResult,
    EditorOutput,
    InputValidationResult,
    OutputValidationResult,
    ResponseAgentInput,
    ResponseAgentResult,
)


def build_response_agent_result(
    *,
    request_id: str,
    workflow_run_id: str,
    original_user_message: str,
    intent_result: IntentResult,
    financial_analysis_result: FinancialAnalysisResult,
    constraints: ConstraintsInput,
    style: StyleInput,
    input_validation: InputValidationResult,
    routing: AgentRoutingResult,
    agent_outputs: list[AgentOutput],
    editor_output: EditorOutput,
    output_validation: OutputValidationResult,
) -> ResponseAgentResult:
    return ResponseAgentResult(
        request_id=request_id,
        workflow_run_id=workflow_run_id,
        input=ResponseAgentInput(
            original_user_message=original_user_message,
            intent_result=intent_result,
            financial_analysis_result=financial_analysis_result,
            constraints=constraints,
            style=style,
        ),
        input_validation=input_validation,
        routing=routing,
        agent_outputs=agent_outputs,
        editor_output=editor_output,
        output_validation=output_validation,
    )
