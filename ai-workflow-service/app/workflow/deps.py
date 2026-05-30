"""Injectable workflow dependencies for LangGraph nodes."""
from __future__ import annotations

from dataclasses import dataclass

from app.clients.analytics_client import AnalyticsClient
from app.clients.backend_chat_client import BackendChatClient
from app.clients.context_builder_client import ContextBuilderClient
from app.clients.intent_parser_client import IntentParserClient
from app.clients.response_agent_client import ResponseAgentClient


@dataclass
class WorkflowDeps:
    intent_parser: IntentParserClient
    context_builder: ContextBuilderClient
    analytics: AnalyticsClient
    response_agent: ResponseAgentClient
    backend_chat: BackendChatClient
