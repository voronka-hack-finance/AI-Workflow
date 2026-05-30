"""Workflow orchestrator — thin wrapper around LangGraph."""
from __future__ import annotations

import logging

from app.clients.analytics_client import AnalyticsClient
from app.clients.backend_chat_client import BackendChatClient
from app.clients.context_builder_client import ContextBuilderClient
from app.clients.intent_parser_client import IntentParserClient
from app.clients.response_agent_client import ResponseAgentClient
from app.schemas.workflow_debug_result import WorkflowDebugResult
from app.schemas.workflow_result import WorkflowResult
from app.schemas.workflow_task import WorkflowTask
from app.workflow.debug_runner import run_workflow_debug
from app.workflow.deps import WorkflowDeps
from app.workflow.graph import build_workflow_graph
from app.workflow.state import initial_state, to_workflow_result
from app.workflow.statuses import WorkflowStatus

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Coordinates intent -> context -> analytics -> response pipeline via LangGraph."""

    def __init__(
        self,
        *,
        intent_parser: IntentParserClient | None = None,
        context_builder: ContextBuilderClient | None = None,
        analytics: AnalyticsClient | None = None,
        response_agent: ResponseAgentClient | None = None,
        backend_chat: BackendChatClient | None = None,
    ) -> None:
        if backend_chat is None:
            raise ValueError("backend_chat client is required")

        self._intent_parser = intent_parser or IntentParserClient()
        self._context_builder = context_builder or ContextBuilderClient()
        self._analytics = analytics or AnalyticsClient()
        self._response_agent = response_agent or ResponseAgentClient()
        self._backend_chat = backend_chat

        self._deps = WorkflowDeps(
            intent_parser=self._intent_parser,
            context_builder=self._context_builder,
            analytics=self._analytics,
            response_agent=self._response_agent,
            backend_chat=self._backend_chat,
        )
        self._graph = build_workflow_graph(self._deps)

    async def run_workflow(self, task: WorkflowTask) -> WorkflowResult:
        await self._backend_chat.update_workflow_status(
            request_id=task.request_id,
            workflow_run_id=task.workflow_run_id,
            user_id=task.user_id,
            chat_id=task.chat_id,
            status=WorkflowStatus.RUNNING,
        )
        logger.info(
            "Workflow started",
            extra={
                "request_id": task.request_id,
                "workflow_run_id": task.workflow_run_id,
                "event": "workflow_started",
            },
        )
        final_state = await self._graph.ainvoke(initial_state(task))
        return to_workflow_result(final_state)

    async def run_workflow_debug(
        self,
        task: WorkflowTask,
        *,
        stop_after: str | None = None,
    ) -> WorkflowDebugResult:
        return await run_workflow_debug(
            self._deps,
            self._graph,
            task,
            stop_after=stop_after,
        )
