"""Response generation endpoint."""
from fastapi import APIRouter

from app.response_pipeline.dev_stub import build_dev_final_answer
from app.schemas.response_request import ResponseGenerateRequest
from app.schemas.response_result import ResponseGenerateResult
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput
from shared_contracts.response_agent_result import (
    AgentRoutingResult,
    EditorOutput,
    InputValidationResult,
    OutputValidationResult,
    ResponseAgentInput,
)

router = APIRouter(prefix="/api/v1/response", tags=["response"])


@router.post("/generate", response_model=ResponseGenerateResult)
async def generate_response(request: ResponseGenerateRequest) -> ResponseGenerateResult:
    intent_result = IntentResult.model_validate(request.intent_result)
    financial_analysis_result = FinancialAnalysisResult.model_validate(
        request.financial_analysis_result
    )
    constraints = ConstraintsInput.model_validate(request.constraints)
    style = StyleInput.model_validate(request.style)
    final_answer = build_dev_final_answer(
        original_user_message=request.original_user_message,
        intent_result=intent_result,
        financial_analysis_result=financial_analysis_result,
    )

    return ResponseGenerateResult(
        request_id=request.request_id,
        workflow_run_id=request.workflow_run_id,
        input=ResponseAgentInput(
            original_user_message=request.original_user_message,
            intent_result=intent_result,
            financial_analysis_result=financial_analysis_result,
            constraints=constraints,
            style=style,
        ),
        input_validation=InputValidationResult(validation_status="passed"),
        routing=AgentRoutingResult(routing_status="dev_stub"),
        editor_output=EditorOutput(final_answer=final_answer),
        output_validation=OutputValidationResult(validation_status="passed"),
    )
