"""LangGraph workflow graph builder."""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.workflow.deps import WorkflowDeps
from app.workflow.nodes import (
    make_build_context,
    make_fail_workflow,
    make_generate_response,
    make_parse_intent,
    make_run_analytics,
    make_send_final_answer,
)
from app.workflow.routing import (
    route_after_build_context,
    route_after_generate_response,
    route_after_parse_intent,
    route_after_run_analytics,
)
from app.workflow.state import WorkflowGraphState


def build_workflow_graph(deps: WorkflowDeps):
    graph = StateGraph(WorkflowGraphState)

    graph.add_node("parse_intent", make_parse_intent(deps))
    graph.add_node("build_context", make_build_context(deps))
    graph.add_node("run_analytics", make_run_analytics(deps))
    graph.add_node("generate_response", make_generate_response(deps))
    graph.add_node("send_final_answer", make_send_final_answer(deps))
    graph.add_node("fail_workflow", make_fail_workflow(deps))

    graph.set_entry_point("parse_intent")

    graph.add_conditional_edges("parse_intent", route_after_parse_intent)
    graph.add_conditional_edges("build_context", route_after_build_context)
    graph.add_conditional_edges("run_analytics", route_after_run_analytics)
    graph.add_conditional_edges("generate_response", route_after_generate_response)

    graph.add_edge("send_final_answer", END)
    graph.add_edge("fail_workflow", END)

    return graph.compile()
