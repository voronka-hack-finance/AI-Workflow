"""Conditional routing for the workflow LangGraph."""
from __future__ import annotations

from typing import Literal

from app.workflow.state import WorkflowGraphState

RouteAfterParseIntent = Literal["build_context", "fail_workflow"]
RouteAfterBuildContext = Literal["run_analytics", "fail_workflow"]
RouteAfterRunAnalytics = Literal["generate_response", "fail_workflow"]
RouteAfterGenerateResponse = Literal["send_final_answer", "fail_workflow"]


def route_after_parse_intent(state: WorkflowGraphState) -> RouteAfterParseIntent:
    if state.get("error"):
        return "fail_workflow"
    return "build_context"


def route_after_build_context(state: WorkflowGraphState) -> RouteAfterBuildContext:
    if state.get("error"):
        return "fail_workflow"
    return "run_analytics"


def route_after_run_analytics(state: WorkflowGraphState) -> RouteAfterRunAnalytics:
    if state.get("error"):
        return "fail_workflow"
    return "generate_response"


def route_after_generate_response(state: WorkflowGraphState) -> RouteAfterGenerateResponse:
    if state.get("error"):
        return "fail_workflow"
    return "send_final_answer"
