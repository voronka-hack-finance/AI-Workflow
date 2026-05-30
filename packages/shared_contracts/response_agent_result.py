"""Response agent result contract models."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from shared_contracts.common import (
    ContentAgentName,
    JsonDict,
    OutputFormat,
    Priority,
    RequestId,
    SchemaVersion,
    WorkflowRunId,
)
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput


class ResponseAgentInput(BaseModel):
    original_user_message: str
    intent_result: IntentResult
    financial_analysis_result: FinancialAnalysisResult
    constraints: ConstraintsInput = Field(default_factory=ConstraintsInput)
    style: StyleInput = Field(default_factory=StyleInput)


class InputValidationResult(BaseModel):
    validation_status: str
    can_run_agents: bool = True
    missing_fields: list[str] = Field(default_factory=list)
    warnings_to_consider: list[str] = Field(default_factory=list)
    message: str | None = None


class AgentRoutingResult(BaseModel):
    routing_status: str
    selected_agents: list[ContentAgentName | str] = Field(default_factory=list)
    primary_agent: ContentAgentName | str | None = None
    execution_mode: str = "single"
    reason: JsonDict = Field(default_factory=dict)


class AgentRecommendation(BaseModel):
    title: str
    description: str
    expected_effect: float | None = None


class AgentOutput(BaseModel):
    agent_name: ContentAgentName | str
    status: str = "skipped"
    priority: Priority | str = Priority.MEDIUM
    used_facts: list[str] = Field(default_factory=list)
    summary: str = ""
    facts: list[str] = Field(default_factory=list)
    recommendations: list[AgentRecommendation] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    confidence: str = "medium"


class EditorOutput(BaseModel):
    format: OutputFormat | str = OutputFormat.CHAT_TEXT
    final_answer: str


class OutputValidationIssue(BaseModel):
    type: str
    message: str


class OutputValidationResult(BaseModel):
    validation_status: str
    can_send_to_user: bool = True
    issues: list[OutputValidationIssue] = Field(default_factory=list)
    required_fixes: list[str] = Field(default_factory=list)


class ResponseAgentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = "1.0"
    request_id: RequestId
    workflow_run_id: WorkflowRunId
    input: ResponseAgentInput
    input_validation: InputValidationResult
    routing: AgentRoutingResult
    agent_outputs: list[AgentOutput] = Field(default_factory=list)
    editor_output: EditorOutput
    output_validation: OutputValidationResult
