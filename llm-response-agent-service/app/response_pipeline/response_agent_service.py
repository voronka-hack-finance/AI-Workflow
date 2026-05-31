"""Response agent orchestrator."""
from __future__ import annotations

import asyncio
import logging

from app.agents import get_agent
from app.core.config import Settings, get_settings
from app.llm.provider_factory import create_llm_provider
from app.response_pipeline.agent_router import AgentRouter
from app.response_pipeline.final_editor import FinalEditor
from app.response_pipeline.output_builder import build_response_agent_result
from app.schemas.response_request import ResponseGenerateRequest
from app.schemas.response_result import ResponseGenerateResult
from app.validators.input_validator import InputValidator
from app.validators.output_validator import OutputValidator
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.response_agent_result import AgentRoutingResult, OutputValidationResult

logger = logging.getLogger(__name__)


class ResponseAgentService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._provider = create_llm_provider(self._settings)
        self._input_validator = InputValidator()
        self._router = AgentRouter(self._settings)
        self._final_editor = FinalEditor()
        self._output_validator = OutputValidator()

    def _validate_editor_output(
        self,
        final_answer: str,
        *,
        financial_analysis_result: FinancialAnalysisResult,
        constraints: ConstraintsInput,
        style: StyleInput,
        warnings_to_consider: list[str],
        agent_outputs: list,
    ) -> OutputValidationResult:
        return self._output_validator.validate(
            final_answer=final_answer,
            financial_analysis_result=financial_analysis_result,
            constraints=constraints,
            style=style,
            warnings_to_consider=warnings_to_consider,
            agent_outputs=agent_outputs or None,
        )

    async def generate(self, request: ResponseGenerateRequest) -> ResponseGenerateResult:
        intent_result = IntentResult.model_validate(request.intent_result)
        financial_analysis_result = FinancialAnalysisResult.model_validate(
            request.financial_analysis_result
        )
        constraints = ConstraintsInput.model_validate(request.constraints)
        style = StyleInput.model_validate(request.style)

        input_validation = self._input_validator.validate(
            intent=intent_result,
            financial_analysis_result=financial_analysis_result,
            constraints=constraints,
            style=style,
        )

        agent_outputs = []
        routing = AgentRoutingResult(
            routing_status="no_agents",
            selected_agents=[],
            primary_agent=None,
            execution_mode="single",
            reason={},
        )

        if input_validation.can_run_agents:
            routing = self._router.select(
                intent=intent_result,
                financial_analysis_result=financial_analysis_result,
                constraints=constraints,
                original_user_message=request.original_user_message,
            )
            if routing.selected_agents:
                tasks = [
                    get_agent(str(agent_name)).run(
                        intent=intent_result,
                        far=financial_analysis_result,
                        constraints=constraints,
                        style=style,
                        original_user_message=request.original_user_message,
                        provider=self._provider,
                    )
                    for agent_name in routing.selected_agents
                ]
                agent_outputs = list(await asyncio.gather(*tasks))

            if agent_outputs:
                editor_output = await self._final_editor.compose(
                    original_user_message=request.original_user_message,
                    agent_outputs=agent_outputs,
                    style=style,
                    warnings=input_validation.warnings_to_consider,
                    provider=self._provider,
                )
            else:
                editor_output = await self._final_editor.compose_fallback(
                    original_user_message=request.original_user_message,
                    agent_outputs=agent_outputs,
                    style=style,
                )
        else:
            editor_output = self._final_editor.compose_safe_message(
                input_validation=input_validation,
                style=style,
            )

        output_validation = self._validate_editor_output(
            editor_output.final_answer,
            financial_analysis_result=financial_analysis_result,
            constraints=constraints,
            style=style,
            warnings_to_consider=input_validation.warnings_to_consider,
            agent_outputs=agent_outputs,
        )

        if not output_validation.can_send_to_user and output_validation.required_fixes:
            logger.warning(
                "RESPONSE_AGENT_EDITOR_VALIDATION_FAILED issues=%s",
                [issue.type for issue in output_validation.issues],
            )
            editor_output = await self._final_editor.compose(
                original_user_message=request.original_user_message,
                agent_outputs=agent_outputs,
                style=style,
                warnings=input_validation.warnings_to_consider,
                provider=self._provider,
                required_fixes=output_validation.required_fixes,
            )
            retried_answer = editor_output.final_answer
            output_validation = self._validate_editor_output(
                retried_answer,
                financial_analysis_result=financial_analysis_result,
                constraints=constraints,
                style=style,
                warnings_to_consider=input_validation.warnings_to_consider,
                agent_outputs=agent_outputs,
            )
            if not output_validation.can_send_to_user:
                logger.warning(
                    "RESPONSE_AGENT_EDITOR_FALLBACK reason=%s",
                    [issue.type for issue in output_validation.issues],
                )
                editor_output = await self._final_editor.compose_fallback(
                    original_user_message=request.original_user_message,
                    agent_outputs=agent_outputs,
                    style=style,
                    last_editor_answer=retried_answer,
                )
                output_validation = self._validate_editor_output(
                    editor_output.final_answer,
                    financial_analysis_result=financial_analysis_result,
                    constraints=constraints,
                    style=style,
                    warnings_to_consider=input_validation.warnings_to_consider,
                    agent_outputs=agent_outputs,
                )
                if not output_validation.can_send_to_user:
                    output_validation = OutputValidationResult(
                        validation_status="passed",
                        can_send_to_user=True,
                        issues=output_validation.issues,
                        required_fixes=[],
                    )

        return build_response_agent_result(
            request_id=request.request_id,
            workflow_run_id=request.workflow_run_id,
            original_user_message=request.original_user_message,
            intent_result=intent_result,
            financial_analysis_result=financial_analysis_result,
            constraints=constraints,
            style=style,
            input_validation=input_validation,
            routing=routing,
            agent_outputs=agent_outputs,
            editor_output=editor_output,
            output_validation=output_validation,
        )
