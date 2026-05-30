"""Conditional routing for the workflow LangGraph."""
from __future__ import annotations

from typing import Literal

from app.workflow import clarification
from app.workflow.state import WorkflowGraphState

RouteAfterParseIntent = Literal["build_context", "send_clarification", "fail_workflow"]
RouteAfterBuildContext = Literal["run_analytics", "send_clarification", "fail_workflow"]
RouteAfterRunAnalytics = Literal["generate_response", "send_clarification", "fail_workflow"]
RouteAfterGenerateResponse = Literal["send_final_answer", "send_clarification", "fail_workflow"]


def resolve_clarification_question(state: WorkflowGraphState) -> str:
    if question := state.get("clarification_question"):
        return question
    intent_response = state.get("intent_response")
    if intent_response and clarification.intent_requires_clarification(intent_response):
        return clarification.intent_clarification_question(intent_response)
    context_package = state.get("context_package")
    if context_package and clarification.context_requires_clarification(context_package):
        return clarification.context_clarification_question(context_package)
    analysis_result = state.get("analysis_result")
    if analysis_result and clarification.analytics_requires_clarification(analysis_result):
        return clarification.analytics_clarification_question(analysis_result)
    response_result = state.get("response_result")
    if response_result and clarification.response_agent_requires_clarification(response_result):
        return clarification.response_agent_clarification_question(response_result)
    return clarification.GENERIC_CLARIFICATION


def route_after_parse_intent(state: WorkflowGraphState) -> RouteAfterParseIntent:
    if state.get("error"):
        return "fail_workflow"
    intent_response = state.get("intent_response")
    if intent_response and clarification.intent_requires_clarification(intent_response):
        return "send_clarification"
    return "build_context"


def route_after_build_context(state: WorkflowGraphState) -> RouteAfterBuildContext:
    if state.get("error"):
        return "fail_workflow"
    context_package = state.get("context_package")
    if context_package and clarification.context_requires_clarification(context_package):
        return "send_clarification"
    return "run_analytics"


def route_after_run_analytics(state: WorkflowGraphState) -> RouteAfterRunAnalytics:
    if state.get("error"):
        return "fail_workflow"
    analysis_result = state.get("analysis_result")
    if analysis_result and clarification.analytics_requires_clarification(analysis_result):
        return "send_clarification"
    return "generate_response"


def route_after_generate_response(state: WorkflowGraphState) -> RouteAfterGenerateResponse:
    if state.get("error"):
        return "fail_workflow"
    response_result = state.get("response_result")
    if response_result and clarification.response_agent_requires_clarification(response_result):
        return "send_clarification"
    return "send_final_answer"
