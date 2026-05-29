"""One-off scaffold generator for AI services monorepo."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def pyproject(name: str, description: str) -> str:
    return f'''[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "httpx>=0.27.0",
]

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.9.0",
]

[tool.uv]
package = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"
'''


def dockerfile(service: str, port: int) -> str:
    return f"""FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \\
    UV_LINK_MODE=copy \\
    UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \\
    uv sync --frozen --no-dev

COPY app ./app

EXPOSE {port}

CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{port}"]
"""


def service_readme(title: str, purpose: str, port: int, main_endpoint: str) -> str:
    return f"""# {title}

{purpose}

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port {port}
uv run pytest
uv run ruff check .
```

## Endpoints

- `GET /health` — health check
- `{main_endpoint}` — main API (skeleton)

## Status

Skeleton only — business logic marked with `TODO`.
"""


def core_config(service_env_prefix: str = "") -> str:
    extra = ""
    if service_env_prefix:
        extra = f'''
    # Service URLs (workflow orchestrator)
    intent_parser_service_url: str = "http://localhost:8011"
    context_builder_service_url: str = "http://localhost:8012"
    analytics_service_url: str = "http://localhost:8013"
    response_agent_service_url: str = "http://localhost:8014"
    rabbitmq_url: str = "amqp://finance_ai:finance_ai@localhost:5672/"
    ai_workflow_max_concurrency: int = 3
    ai_workflow_timeout_seconds: int = 120
'''
    if service_env_prefix == "llm":
        extra = '''
    llm_provider: str = "openai"
    llm_model: str = "gpt-4.1-mini"
    llm_api_key: str = ""
'''
    return f'''"""Application configuration."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    service_port: int = 8000
{extra}

@lru_cache
def get_settings() -> Settings:
    # TODO: validate required secrets in production
    return Settings()
'''


def core_logging() -> str:
    return '''"""Logging setup placeholder."""
import logging

# TODO: integrate shared_logging package


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
'''


def core_errors() -> str:
    return '''"""Application errors."""


class AppError(Exception):
    """Base application error."""


class ServiceUnavailableError(AppError):
    """Raised when a downstream service is unavailable."""


class ValidationError(AppError):
    """Raised when input validation fails."""
'''


def health_router() -> str:
    return '''"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
'''


def test_health() -> str:
    return '''"""Health endpoint tests."""
from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
'''


def init_py() -> str:
    return '"""Package."""\n'


def main_py(routers: list[tuple[str, str]]) -> str:
    imports = "\n".join(
        f"from app.api.v1.{mod} import router as {alias}"
        for mod, alias in routers
    )
    includes = "\n".join(f"app.include_router({alias})" for _, alias in routers)
    return f'''"""FastAPI application entrypoint."""
from fastapi import FastAPI

from app.core.logging import setup_logging
{imports}

setup_logging()

app = FastAPI(
    title="AI Service",
    version="0.1.0",
)

{includes}
'''


def scaffold_ai_workflow() -> None:
    base = ROOT / "ai-workflow-service"
    port = 8010
    write(base / "pyproject.toml", pyproject("ai-workflow-service", "AI workflow orchestrator"))
    write(base / "Dockerfile", dockerfile("ai-workflow-service", port))
    write(
        base / "README.md",
        service_readme(
            "AI Workflow Service",
            "Orchestrates AI pipeline steps via RabbitMQ and HTTP clients.",
            port,
            "POST /api/v1/workflows (skeleton)",
        ),
    )
    write(base / "tests" / "__init__.py", "")
    write(base / "tests" / "test_health.py", test_health())

    cfg = core_config("workflow")
    cfg = cfg.replace("service_port: int = 8000", "service_port: int = 8010")
    write(base / "app" / "__init__.py", init_py())
    write(base / "app" / "core" / "__init__.py", init_py())
    write(base / "app" / "core" / "config.py", cfg)
    write(base / "app" / "core" / "logging.py", core_logging())
    write(base / "app" / "core" / "errors.py", core_errors())

    write(base / "app" / "api" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "health.py", health_router())
    write(
        base / "app" / "api" / "v1" / "workflows.py",
        '''"""Workflow HTTP API (skeleton)."""
from fastapi import APIRouter

from app.schemas.workflow_task import WorkflowTask
from app.schemas.workflow_result import WorkflowResult

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowResult)
async def trigger_workflow(task: WorkflowTask) -> WorkflowResult:
    # TODO: enqueue workflow task to RabbitMQ
    return WorkflowResult(task_id=task.task_id, status="pending")
''',
    )

    write(
        base / "app" / "main.py",
        main_py([("health", "health_router"), ("workflows", "workflows_router")]),
    )

    # schemas
    for name, content in [
        (
            "workflow_task.py",
            '''"""Workflow task schema."""
from pydantic import BaseModel, Field


class WorkflowTask(BaseModel):
    task_id: str
    user_id: str
    message_id: str
    raw_message: str = ""
    # TODO: extend with chat_context, active_workflow
''',
        ),
        (
            "workflow_result.py",
            '''"""Workflow result schema."""
from pydantic import BaseModel

from app.schemas.workflow_status import WorkflowStatus


class WorkflowResult(BaseModel):
    task_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    # TODO: add final_answer, error details
''',
        ),
        (
            "workflow_status.py",
            '''"""Workflow status enum."""
from enum import Enum


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_CLARIFICATION = "needs_clarification"
''',
        ),
        (
            "service_contracts.py",
            '''"""Cross-service contract placeholders."""
from pydantic import BaseModel

# TODO: align with packages/shared-contracts
''',
        ),
    ]:
        write(base / "app" / "schemas" / name, content)
    write(base / "app" / "schemas" / "__init__.py", init_py())

    # orchestrator
    write(
        base / "app" / "orchestrator" / "workflow_orchestrator.py",
        '''"""Workflow orchestration."""
from app.schemas.workflow_task import WorkflowTask
from app.schemas.workflow_result import WorkflowResult


class WorkflowOrchestrator:
    """Coordinates intent -> context -> analytics -> response pipeline."""

    async def run_workflow(self, task: WorkflowTask) -> WorkflowResult:
        # TODO: implement actual workflow execution
        # TODO: call intent_parser, context_builder, analytics, response_agent clients
        return WorkflowResult(task_id=task.task_id, status="pending")
''',
    )
    for f in [
        "workflow_steps.py",
        "workflow_state.py",
        "clarification_handler.py",
        "workflow_errors.py",
    ]:
        cls = "".join(w.capitalize() for w in f.replace(".py", "").split("_"))
        write(
            base / "app" / "orchestrator" / f,
            f'''"""{cls} placeholder."""


class {cls}:
    # TODO: implement
    pass
''',
        )
    write(base / "app" / "orchestrator" / "__init__.py", init_py())

    # queue
    write(
        base / "app" / "queue" / "rabbit_consumer.py",
        '''"""RabbitMQ workflow consumer."""
from app.orchestrator.workflow_orchestrator import WorkflowOrchestrator


class RabbitWorkflowConsumer:
    """Consumes workflow tasks from RabbitMQ."""

    def __init__(self, orchestrator: WorkflowOrchestrator | None = None) -> None:
        self._orchestrator = orchestrator or WorkflowOrchestrator()

    async def start(self) -> None:
        # TODO: connect to RabbitMQ and consume workflow queue
        pass

    async def stop(self) -> None:
        # TODO: graceful shutdown
        pass
''',
    )
    for f, cls in [
        ("rabbit_producer.py", "RabbitWorkflowProducer"),
        ("schemas.py", "QueueMessage"),
        ("retry_policy.py", "RetryPolicy"),
    ]:
        write(
            base / "app" / "queue" / f,
            f'''"""{cls} placeholder."""


class {cls}:
    # TODO: implement
    pass
''',
        )
    write(base / "app" / "queue" / "__init__.py", init_py())

    # clients
    for client in [
        "intent_parser_client",
        "context_builder_client",
        "analytics_client",
        "response_agent_client",
        "chat_service_client",
    ]:
        cls = "".join(w.capitalize() for w in client.split("_"))
        write(
            base / "app" / "clients" / f"{client}.py",
            f'''"""HTTP client for downstream service."""
from app.core.config import get_settings


class {cls}:
    def __init__(self) -> None:
        self._settings = get_settings()

    async def call(self, payload: dict) -> dict:
        # TODO: implement HTTP call with shared_http
        return {{}}
''',
        )
    write(base / "app" / "clients" / "__init__.py", init_py())

    # persistence
    for f, cls in [
        ("models.py", "WorkflowRunModel"),
        ("repositories.py", "WorkflowRepository"),
        ("db.py", "Database"),
    ]:
        write(
            base / "app" / "persistence" / f,
            f'''"""{cls} placeholder."""


class {cls}:
    # TODO: implement
    pass
''',
        )
    write(base / "app" / "persistence" / "__init__.py", init_py())


def scaffold_intent_parser() -> None:
    base = ROOT / "llm-intent-parser-service"
    port = 8011
    write(base / "pyproject.toml", pyproject("llm-intent-parser-service", "LLM intent parser"))
    write(base / "Dockerfile", dockerfile("llm-intent-parser-service", port))
    write(
        base / "README.md",
        service_readme(
            "LLM Intent Parser Service",
            "Parses user messages into structured intent JSON via LLM.",
            port,
            "POST /api/v1/intent/parse",
        ),
    )
    write(base / "tests" / "__init__.py", "")
    write(base / "tests" / "test_health.py", test_health())

    cfg = core_config("llm")
    cfg = cfg.replace("service_port: int = 8000", "service_port: int = 8011")
    write(base / "app" / "__init__.py", init_py())
    write(base / "app" / "core" / "__init__.py", init_py())
    write(base / "app" / "core" / "config.py", cfg)
    write(base / "app" / "core" / "logging.py", core_logging())
    write(base / "app" / "core" / "errors.py", core_errors())
    write(base / "app" / "api" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "health.py", health_router())
    write(
        base / "app" / "api" / "v1" / "parse_intent.py",
        '''"""Intent parsing endpoint."""
from fastapi import APIRouter

from app.schemas.intent_request import IntentParseRequest
from app.schemas.intent_result import IntentParseResponse

router = APIRouter(prefix="/api/v1/intent", tags=["intent"])


@router.post("/parse", response_model=IntentParseResponse)
async def parse_intent(request: IntentParseRequest) -> IntentParseResponse:
    # TODO: call IntentParserService and LLM client
    return IntentParseResponse(intent="unknown", confidence=0.0)
''',
    )
    write(
        base / "app" / "main.py",
        main_py([("health", "health_router"), ("parse_intent", "parse_intent_router")]),
    )
    write(
        base / "app" / "schemas" / "intent_request.py",
        '''"""Intent parse request schema."""
from pydantic import BaseModel, Field

from app.schemas.chat_context import ChatContext


class IntentParseRequest(BaseModel):
    raw_message: str
    chat_context: ChatContext | None = None
    active_workflow: str | None = None
    current_date: str | None = None
    timezone: str = "UTC"
''',
    )
    write(
        base / "app" / "schemas" / "intent_result.py",
        '''"""Intent parse response schema."""
from pydantic import BaseModel, Field


class IntentParseResponse(BaseModel):
    intent: str = "unknown"
    confidence: float = 0.0
    entities: dict = Field(default_factory=dict)
    # TODO: align with full intent_result JSON from docs
''',
    )
    write(
        base / "app" / "schemas" / "chat_context.py",
        '''"""Chat context schema."""
from pydantic import BaseModel


class ChatContext(BaseModel):
    messages: list[dict] = []
    # TODO: extend per chat API contract
''',
    )
    write(base / "app" / "schemas" / "__init__.py", init_py())

    for mod, cls in [
        ("intent_parser_service.py", "IntentParserService"),
        ("prompt_builder.py", "PromptBuilder"),
        ("output_parser.py", "OutputParser"),
        ("validators.py", "IntentValidators"),
        ("examples.py", "IntentExamples"),
    ]:
        write(
            base / "app" / "parser" / mod,
            f'''"""{cls}."""


class {cls}:
    async def run(self, *args, **kwargs):
        # TODO: implement
        pass
''',
        )
    write(base / "app" / "parser" / "__init__.py", init_py())
    for mod, cls in [
        ("llm_client.py", "LLMClient"),
        ("provider.py", "LLMProvider"),
        ("json_mode.py", "JsonMode"),
        ("retry_policy.py", "LLMRetryPolicy"),
    ]:
        write(
            base / "app" / "llm" / mod,
            f'''"""{cls}."""


class {cls}:
    # TODO: implement
    pass
''',
        )
    write(base / "app" / "llm" / "__init__.py", init_py())


def scaffold_context_builder() -> None:
    base = ROOT / "ai-context-builder-service"
    port = 8012
    write(base / "pyproject.toml", pyproject("ai-context-builder-service", "AI context builder"))
    write(base / "Dockerfile", dockerfile("ai-context-builder-service", port))
    write(
        base / "README.md",
        service_readme(
            "AI Context Builder Service",
            "Builds context package and execution plan from intent.",
            port,
            "POST /api/v1/context/build",
        ),
    )
    write(base / "tests" / "__init__.py", "")
    write(base / "tests" / "test_health.py", test_health())
    cfg = core_config()
    cfg = cfg.replace("service_port: int = 8000", "service_port: int = 8012")
    write(base / "app" / "__init__.py", init_py())
    write(base / "app" / "core" / "__init__.py", init_py())
    write(base / "app" / "core" / "config.py", cfg)
    write(base / "app" / "core" / "logging.py", core_logging())
    write(base / "app" / "core" / "errors.py", core_errors())
    write(base / "app" / "api" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "health.py", health_router())
    write(
        base / "app" / "api" / "v1" / "build_context.py",
        '''"""Context build endpoint."""
from fastapi import APIRouter

from app.schemas.context_builder_request import ContextBuilderRequest
from app.schemas.context_package import ContextPackage

router = APIRouter(prefix="/api/v1/context", tags=["context"])


@router.post("/build", response_model=ContextPackage)
async def build_context(request: ContextBuilderRequest) -> ContextPackage:
    # TODO: call ContextBuilderService
    return ContextPackage(user_id=request.user_id)
''',
    )
    write(
        base / "app" / "main.py",
        main_py([("health", "health_router"), ("build_context", "build_context_router")]),
    )
    schemas = {
        "context_builder_request.py": '''"""Context builder request."""
from pydantic import BaseModel


class ContextBuilderRequest(BaseModel):
    user_id: str
    intent_result: dict = {}
    # TODO: extend fields
''',
        "context_package.py": '''"""Context package response."""
from pydantic import BaseModel, Field

from app.schemas.data_quality import DataQuality


class ContextPackage(BaseModel):
    user_id: str
    execution_plan: list[str] = Field(default_factory=list)
    data_quality: DataQuality | None = None
    # TODO: normalized data blocks
''',
        "normalized_transaction.py": '''"""Normalized transaction."""
from pydantic import BaseModel


class NormalizedTransaction(BaseModel):
    id: str
    amount: float = 0.0
    # TODO: extend
''',
        "normalized_user_context.py": '''"""Normalized user context."""
from pydantic import BaseModel


class NormalizedUserContext(BaseModel):
    user_id: str
    # TODO: extend
''',
        "category_profile.py": '''"""Category profile."""
from pydantic import BaseModel


class CategoryProfile(BaseModel):
    category_id: str
    name: str = ""
''',
        "data_quality.py": '''"""Data quality metadata."""
from pydantic import BaseModel


class DataQuality(BaseModel):
    completeness: float = 1.0
    warnings: list[str] = []
''',
    }
    write(base / "app" / "schemas" / "__init__.py", init_py())
    for name, content in schemas.items():
        write(base / "app" / "schemas" / name, content)

    modules = {
        "builder": [
            "context_builder_service",
            "context_package_builder",
            "missing_data_checker",
            "data_quality_builder",
        ],
        "registry": ["function_registry", "function_dependencies", "function_requirements"],
        "planning": [
            "function_expander",
            "execution_plan_builder",
            "data_requirements_resolver",
            "date_resolver",
        ],
        "data_clients": [
            "transactions_client",
            "user_context_client",
            "goals_client",
            "debts_client",
            "categories_client",
            "accounts_client",
        ],
        "data_adapters": [
            "transaction_mapper",
            "user_context_mapper",
            "goal_mapper",
            "debt_mapper",
            "category_mapper",
            "account_mapper",
        ],
    }
    for folder, files in modules.items():
        write(base / "app" / folder / "__init__.py", init_py())
        for f in files:
            cls = "".join(w.capitalize() for w in f.split("_"))
            write(
                base / "app" / folder / f"{f}.py",
                f'''"""{cls}."""


class {cls}:
    # TODO: implement
    pass
''',
            )


def scaffold_analytics() -> None:
    base = ROOT / "analytics-service"
    port = 8013
    write(base / "pyproject.toml", pyproject("analytics-service", "Financial analytics engine"))
    write(base / "Dockerfile", dockerfile("analytics-service", port))
    write(
        base / "README.md",
        service_readme(
            "Analytics Service",
            "Runs execution plan functions on context package.",
            port,
            "POST /api/v1/analytics/run",
        ),
    )
    write(base / "tests" / "__init__.py", "")
    write(base / "tests" / "test_health.py", test_health())
    write(
        base / "tests" / "test_safe_math.py",
        '''"""Safe math helper tests."""
from app.helpers.safe_math import safe_divide


def test_safe_divide() -> None:
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
''',
    )
    cfg = core_config()
    cfg = cfg.replace("service_port: int = 8000", "service_port: int = 8013")
    write(base / "app" / "__init__.py", init_py())
    write(base / "app" / "core" / "__init__.py", init_py())
    write(base / "app" / "core" / "config.py", cfg)
    write(base / "app" / "core" / "logging.py", core_logging())
    write(base / "app" / "core" / "errors.py", core_errors())
    write(base / "app" / "api" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "health.py", health_router())
    write(
        base / "app" / "api" / "v1" / "run_analysis.py",
        '''"""Analytics run endpoint."""
from fastapi import APIRouter

from app.schemas.context_package import ContextPackageInput
from app.schemas.analysis_result import AnalysisResult

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.post("/run", response_model=AnalysisResult)
async def run_analysis(package: ContextPackageInput) -> AnalysisResult:
    # TODO: call AnalyticsEngine
    return AnalysisResult()
''',
    )
    write(
        base / "app" / "main.py",
        main_py([("health", "health_router"), ("run_analysis", "run_analysis_router")]),
    )
    for name, content in [
        (
            "context_package.py",
            '''"""Context package input for analytics."""
from pydantic import BaseModel, Field


class ContextPackageInput(BaseModel):
    user_id: str = ""
    execution_plan: list[str] = Field(default_factory=list)
''',
        ),
        ("function_result.py", '''"""Single function result."""
from pydantic import BaseModel


class FunctionResult(BaseModel):
    function_name: str
    data: dict = {}
'''),
        (
            "financial_analysis_result.py",
            '''"""Aggregated financial analysis."""
from pydantic import BaseModel, Field

from app.schemas.function_result import FunctionResult


class FinancialAnalysisResult(BaseModel):
    function_results: list[FunctionResult] = Field(default_factory=list)
''',
        ),
        ("analysis_result.py", '''"""Full analysis response."""
from pydantic import BaseModel

from app.schemas.financial_analysis_result import FinancialAnalysisResult


class AnalysisResult(BaseModel):
    financial_analysis: FinancialAnalysisResult = FinancialAnalysisResult()
'''),
    ]:
        write(base / "app" / "schemas" / name, content)
    write(base / "app" / "schemas" / "__init__.py", init_py())

    write(
        base / "app" / "helpers" / "safe_math.py",
        '''"""Safe math utilities."""


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator
''',
    )
    for f in ["money.py", "filters.py", "grouping.py", "dates.py"]:
        cls = "".join(w.capitalize() for w in f.replace(".py", "").split("_"))
        write(
            base / "app" / "helpers" / f,
            f'''"""{cls} helpers."""
# TODO: implement
''',
        )
    write(base / "app" / "helpers" / "__init__.py", init_py())

    engine_files = [
        "analytics_engine",
        "execution_plan_runner",
        "result_collector",
        "analysis_result_builder",
    ]
    write(base / "app" / "engine" / "__init__.py", init_py())
    for f in engine_files:
        cls = "".join(w.capitalize() for w in f.split("_"))
        write(
            base / "app" / "engine" / f"{f}.py",
            f'''"""{cls}."""


class {cls}:
    # TODO: implement
    pass
''',
        )

    funcs = [
        "base",
        "period_analysis",
        "expense_breakdown",
        "income_analysis",
        "cashflow_analysis",
        "category_analysis",
        "transfer_analysis",
        "spending_leak_detection",
        "budget_recommendation",
        "budget_plan",
        "action_plan",
        "goal_analysis",
        "emergency_fund_analysis",
        "debt_analysis",
    ]
    write(
        base / "app" / "functions" / "base.py",
        '''"""Base analytics function."""
from abc import ABC, abstractmethod


class BaseAnalyticsFunction(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, context: dict) -> dict:
        # TODO: implement
        return {}
''',
    )
    write(base / "app" / "functions" / "__init__.py", init_py())
    for f in funcs[1:]:
        cls = "".join(w.capitalize() for w in f.split("_"))
        write(
            base / "app" / "functions" / f"{f}.py",
            f'''"""{cls} function."""
from app.functions.base import BaseAnalyticsFunction


class {cls}(BaseAnalyticsFunction):
    name = "{f}"

    async def run(self, context: dict) -> dict:
        # TODO: implement
        return {{}}
''',
        )

    for f in ["risk_score", "priority_score", "problem_tags", "recommendation_type"]:
        cls = "".join(w.capitalize() for w in f.split("_"))
        write(
            base / "app" / "scoring" / f"{f}.py",
            f'''"""{cls}."""
# TODO: implement
''',
        )
    write(base / "app" / "scoring" / "__init__.py", init_py())


def scaffold_response_agent() -> None:
    base = ROOT / "llm-response-agent-service"
    port = 8014
    write(base / "pyproject.toml", pyproject("llm-response-agent-service", "LLM response agent"))
    write(base / "Dockerfile", dockerfile("llm-response-agent-service", port))
    write(
        base / "README.md",
        service_readme(
            "LLM Response Agent Service",
            "Generates final user-facing response via agent pipeline.",
            port,
            "POST /api/v1/response/generate",
        ),
    )
    write(base / "tests" / "__init__.py", "")
    write(base / "tests" / "test_health.py", test_health())
    cfg = core_config("llm")
    cfg = cfg.replace("service_port: int = 8000", "service_port: int = 8014")
    write(base / "app" / "__init__.py", init_py())
    write(base / "app" / "core" / "__init__.py", init_py())
    write(base / "app" / "core" / "config.py", cfg)
    write(base / "app" / "core" / "logging.py", core_logging())
    write(base / "app" / "core" / "errors.py", core_errors())
    write(base / "app" / "api" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "__init__.py", init_py())
    write(base / "app" / "api" / "v1" / "health.py", health_router())
    write(
        base / "app" / "api" / "v1" / "generate_response.py",
        '''"""Response generation endpoint."""
from fastapi import APIRouter

from app.schemas.response_request import ResponseGenerateRequest
from app.schemas.response_result import ResponseGenerateResult

router = APIRouter(prefix="/api/v1/response", tags=["response"])


@router.post("/generate", response_model=ResponseGenerateResult)
async def generate_response(request: ResponseGenerateRequest) -> ResponseGenerateResult:
    # TODO: run ResponseAgentService pipeline
    return ResponseGenerateResult(answer="")
''',
    )
    write(
        base / "app" / "main.py",
        main_py([("health", "health_router"), ("generate_response", "generate_response_router")]),
    )
    for name, content in [
        (
            "response_request.py",
            '''"""Response generation request."""
from pydantic import BaseModel


class ResponseGenerateRequest(BaseModel):
    intent_result: dict = {}
    financial_analysis_result: dict = {}
''',
        ),
        (
            "agent_output.py",
            '''"""Single agent output."""
from pydantic import BaseModel


class AgentOutput(BaseModel):
    agent_name: str
    content: str = ""
''',
        ),
        ("final_answer.py", '''"""Final edited answer."""
from pydantic import BaseModel


class FinalAnswer(BaseModel):
    text: str = ""
'''),
        (
            "response_result.py",
            '''"""Response API result."""
from pydantic import BaseModel

from app.schemas.final_answer import FinalAnswer


class ResponseGenerateResult(BaseModel):
    answer: str = ""
    final_answer: FinalAnswer | None = None
''',
        ),
    ]:
        write(base / "app" / "schemas" / name, content)
    write(base / "app" / "schemas" / "__init__.py", init_py())

    pipeline = [
        "response_agent_service",
        "response_pipeline",
        "agent_router",
        "final_editor",
        "output_builder",
    ]
    write(base / "app" / "response_pipeline" / "__init__.py", init_py())
    for f in pipeline:
        cls = "".join(w.capitalize() for w in f.split("_"))
        write(
            base / "app" / "response_pipeline" / f"{f}.py",
            f'''"""{cls}."""


class {cls}:
    # TODO: implement
    pass
''',
        )

    validators = [
        "safety_validator",
        "input_validator",
        "output_validator",
        "hallucination_guard",
    ]
    write(base / "app" / "validators" / "__init__.py", init_py())
    for f in validators:
        cls = "".join(w.capitalize() for w in f.split("_"))
        write(
            base / "app" / "validators" / f"{f}.py",
            f'''"""{cls}."""


class {cls}:
    # TODO: implement
    pass
''',
        )

    agents = [
        ("base_agent.py", "BaseAgent", True),
        ("safety_agent.py", "SafetyAgent", False),
        ("spending_detective_agent.py", "SpendingDetectiveAgent", False),
        ("growth_agent.py", "GrowthAgent", False),
        ("budget_planner_agent.py", "BudgetPlannerAgent", False),
        ("habit_coach_agent.py", "HabitCoachAgent", False),
    ]
    write(
        base / "app" / "agents" / "base_agent.py",
        '''"""Base response agent."""
from abc import ABC, abstractmethod

from app.schemas.agent_output import AgentOutput


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, context: dict) -> AgentOutput:
        # TODO: implement
        return AgentOutput(agent_name=self.name)
''',
    )
    write(base / "app" / "agents" / "__init__.py", init_py())
    for fname, cls, skip in agents[1:]:
        write(
            base / "app" / "agents" / fname,
            f'''"""{cls}."""
from app.agents.base_agent import BaseAgent
from app.schemas.agent_output import AgentOutput


class {cls}(BaseAgent):
    name = "{cls.replace('Agent', '').lower()}"

    async def run(self, context: dict) -> AgentOutput:
        # TODO: implement LLM call
        return AgentOutput(agent_name=self.name)
''',
        )

    prompts = [
        "safety_agent_prompt",
        "spending_detective_prompt",
        "growth_agent_prompt",
        "budget_planner_prompt",
        "habit_coach_prompt",
        "final_editor_prompt",
    ]
    write(base / "app" / "prompts" / "__init__.py", init_py())
    for p in prompts:
        var = p.upper()
        write(
            base / "app" / "prompts" / f"{p}.py",
            f'"""Prompt template."""\n\n{var} = ""  # TODO: fill prompt\n',
        )

    write(base / "app" / "llm" / "__init__.py", init_py())
    for mod, cls in [
        ("llm_client.py", "LLMClient"),
        ("provider.py", "LLMProvider"),
        ("json_mode.py", "JsonMode"),
        ("retry_policy.py", "LLMRetryPolicy"),
    ]:
        write(
            base / "app" / "llm" / mod,
            f'''"""{cls}."""


class {cls}:
    # TODO: implement
    pass
''',
        )


def scaffold_packages() -> None:
    contracts = [
        ("intent_parser/intent_request.py", "IntentRequest", "raw_message: str = ''"),
        ("intent_parser/intent_result.py", "IntentResult", "intent: str = 'unknown'"),
        (
            "context_builder/context_builder_request.py",
            "ContextBuilderRequest",
            "user_id: str",
        ),
        ("context_builder/context_package.py", "ContextPackage", "user_id: str = ''"),
        ("analytics/function_result.py", "FunctionResult", "function_name: str = ''"),
        (
            "analytics/financial_analysis_result.py",
            "FinancialAnalysisResult",
            "summary: dict = {}",
        ),
        ("analytics/analysis_result.py", "AnalysisResult", "status: str = 'ok'"),
        ("response_agents/response_request.py", "ResponseRequest", "intent_result: dict = {}"),
        ("response_agents/agent_output.py", "AgentOutput", "agent_name: str = ''"),
        ("response_agents/final_answer.py", "FinalAnswer", "text: str = ''"),
        ("workflow/workflow_task.py", "WorkflowTask", "task_id: str"),
        ("workflow/workflow_status.py", "WorkflowStatus", "value: str = 'pending'"),
        ("workflow/workflow_result.py", "WorkflowResult", "task_id: str"),
    ]
    pkg_base = ROOT / "packages" / "shared-contracts"
    write(
        pkg_base / "pyproject.toml",
        '''[project]
name = "shared-contracts"
version = "0.1.0"
description = "Shared Pydantic contracts across AI services"
requires-python = ">=3.11"
dependencies = ["pydantic>=2.9.0"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["shared_contracts"]
''',
    )
    write(pkg_base / "README.md", "# shared-contracts\n\nShared Pydantic models for AI services.\n")
    write(pkg_base / "shared_contracts" / "__init__.py", init_py())

    for path, cls, fields in contracts:
        folder = path.split("/")[0]
        write(pkg_base / "shared_contracts" / folder / "__init__.py", init_py())
        if "WorkflowStatus" in cls:
            content = f'''"""Workflow status."""
from enum import Enum


class {cls}(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
'''
        else:
            content = f'''"""{cls} contract."""
from pydantic import BaseModel, Field


class {cls}(BaseModel):
    {fields}
    # TODO: extend fields per architecture docs
'''
        write(pkg_base / "shared_contracts" / path.replace("/", "\\").replace("\\", "/") if False else pkg_base / "shared_contracts" / path.split("/")[0] / path.split("/")[1], content)

    # fix path writing for contracts
    for path, cls, fields in contracts:
        parts = path.split("/")
        file_path = pkg_base / "shared_contracts" / parts[0] / parts[1]
        write(pkg_base / "shared_contracts" / parts[0] / "__init__.py", init_py())
        if "WorkflowStatus" in cls:
            content = f'''"""Workflow status."""
from enum import Enum


class {cls}(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
'''
        elif "summary" in fields:
            content = f'''"""{cls} contract."""
from pydantic import BaseModel, Field


class {cls}(BaseModel):
    summary: dict = Field(default_factory=dict)
'''
        elif "intent_result" in fields:
            content = f'''"""{cls} contract."""
from pydantic import BaseModel, Field


class {cls}(BaseModel):
    intent_result: dict = Field(default_factory=dict)
'''
        elif "task_id" in fields and cls == "WorkflowTask":
            content = f'''"""{cls} contract."""
from pydantic import BaseModel


class {cls}(BaseModel):
    task_id: str
    user_id: str = ""
'''
        elif cls == "WorkflowResult":
            content = f'''"""{cls} contract."""
from pydantic import BaseModel


class {cls}(BaseModel):
    task_id: str
    status: str = "pending"
'''
        else:
            field_lines = fields
            content = f'''"""{cls} contract."""
from pydantic import BaseModel


class {cls}(BaseModel):
    {field_lines}
'''
        write(file_path, content)

    for pkg, module, files_content in [
        (
            "shared-logging",
            "shared_logging",
            {
                "logger.py": '''"""Shared logger factory."""
import logging


def get_logger(name: str) -> logging.Logger:
    # TODO: structured logging, correlation ids
    return logging.getLogger(name)
''',
            },
        ),
        (
            "shared-http",
            "shared_http",
            {
                "client.py": '''"""HTTP client wrapper."""
import httpx


class ServiceHttpClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def post(self, path: str, json: dict) -> dict:
        # TODO: retries, error mapping
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(f"{self._base_url}{path}", json=json)
            response.raise_for_status()
            return response.json()
''',
                "errors.py": '''"""HTTP errors."""


class HttpClientError(Exception):
    pass
''',
            },
        ),
        (
            "shared-config",
            "shared_config",
            {
                "settings.py": '''"""Base settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
''',
            },
        ),
    ]:
        pb = ROOT / "packages" / pkg
        write(
            pb / "pyproject.toml",
            f'''[project]
name = "{pkg}"
version = "0.1.0"
description = "{pkg} shared package"
requires-python = ">=3.11"
dependencies = [{"pydantic-settings>=2.6.0" if "config" in pkg else '"httpx>=0.27.0"' if "http" in pkg else ""}]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["{module}"]
'''.replace(
                '{"pydantic-settings>=2.6.0"',
                '"pydantic-settings>=2.6.0"',
            ).replace(
                '""]', "]"
            ),
        )
        if "logging" in pkg:
            deps = ""
            write(
                pb / "pyproject.toml",
                f'''[project]
name = "{pkg}"
version = "0.1.0"
description = "{pkg} shared package"
requires-python = ">=3.11"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["{module}"]
''',
            )
        write(pb / "README.md", f"# {pkg}\n\nShared package for AI monorepo.\n")
        write(pb / module / "__init__.py", init_py())
        for fname, content in files_content.items():
            write(pb / module / fname, content)


def scaffold_infra() -> None:
    infra = ROOT / "infra"
    services = [
        "ai-workflow-service",
        "llm-intent-parser-service",
        "ai-context-builder-service",
        "analytics-service",
        "llm-response-agent-service",
    ]
    ports = [8010, 8011, 8012, 8013, 8014]
    for svc, port in zip(services, ports):
        write(
            infra / "docker" / f"{svc}.Dockerfile",
            f"""# Build from monorepo root: docker build -f infra/docker/{svc}.Dockerfile .
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \\
    UV_LINK_MODE=copy \\
    UV_PYTHON_DOWNLOADS=never

COPY {svc}/pyproject.toml {svc}/uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \\
    uv sync --frozen --no-dev

COPY {svc}/app ./app

EXPOSE {port}

CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{port}"]
""",
        )

    write(
        infra / "rabbitmq" / "definitions.json",
        '''{
  "users": [
    {
      "name": "finance_ai",
      "password": "finance_ai",
      "tags": "administrator"
    }
  ],
  "vhosts": [{ "name": "/" }],
  "permissions": [
    {
      "user": "finance_ai",
      "vhost": "/",
      "configure": ".*",
      "write": ".*",
      "read": ".*"
    }
  ],
  "queues": [
    {
      "name": "ai.workflow.tasks",
      "vhost": "/",
      "durable": true
    }
  ],
  "exchanges": [
    {
      "name": "ai.workflow",
      "vhost": "/",
      "type": "topic",
      "durable": true
    }
  ]
}
''',
    )
    write(
        infra / "rabbitmq" / "rabbitmq.conf",
        "management.load_definitions = /etc/rabbitmq/definitions.json\n",
    )
    write(
        infra / "nginx" / "nginx.conf",
        """events {}
http {
    upstream ai_workflow { server ai-workflow-service:8010; }
    upstream intent_parser { server llm-intent-parser-service:8011; }
    upstream context_builder { server ai-context-builder-service:8012; }
    upstream analytics { server analytics-service:8013; }
    upstream response_agent { server llm-response-agent-service:8014; }

    server {
        listen 80;
        # TODO: route paths to upstreams
    }
}
""",
    )


def scaffold_root() -> None:
    write(
        ROOT / ".env.example",
        """APP_ENV=development

RABBITMQ_URL=amqp://finance_ai:finance_ai@rabbitmq:5672/

AI_WORKFLOW_SERVICE_PORT=8010
LLM_INTENT_PARSER_SERVICE_PORT=8011
AI_CONTEXT_BUILDER_SERVICE_PORT=8012
ANALYTICS_SERVICE_PORT=8013
LLM_RESPONSE_AGENT_SERVICE_PORT=8014

LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
LLM_API_KEY=

AI_WORKFLOW_MAX_CONCURRENCY=3
AI_WORKFLOW_TIMEOUT_SECONDS=120

INTENT_PARSER_SERVICE_URL=http://llm-intent-parser-service:8011
CONTEXT_BUILDER_SERVICE_URL=http://ai-context-builder-service:8012
ANALYTICS_SERVICE_URL=http://analytics-service:8013
RESPONSE_AGENT_SERVICE_URL=http://llm-response-agent-service:8014
""",
    )
    write(
        ROOT / "docker-compose.yml",
        """# Production-oriented compose (extend docker-compose.dev.yml for local dev)
services: {}
""",
    )
    write(
        ROOT / "docker-compose.dev.yml",
        """services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: finance_ai
      RABBITMQ_DEFAULT_PASS: finance_ai
    volumes:
      - ./infra/rabbitmq/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf:ro
      - ./infra/rabbitmq/definitions.json:/etc/rabbitmq/definitions.json:ro

  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./infra/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - ai-workflow-service
      - llm-intent-parser-service
      - ai-context-builder-service
      - analytics-service
      - llm-response-agent-service

  ai-workflow-service:
    build:
      context: .
      dockerfile: ai-workflow-service/Dockerfile
    ports:
      - "8010:8010"
    env_file:
      - .env.example
    depends_on:
      - rabbitmq
      - llm-intent-parser-service
      - ai-context-builder-service
      - analytics-service
      - llm-response-agent-service

  llm-intent-parser-service:
    build:
      context: .
      dockerfile: llm-intent-parser-service/Dockerfile
    ports:
      - "8011:8011"
    env_file:
      - .env.example

  ai-context-builder-service:
    build:
      context: .
      dockerfile: ai-context-builder-service/Dockerfile
    ports:
      - "8012:8012"
    env_file:
      - .env.example

  analytics-service:
    build:
      context: .
      dockerfile: analytics-service/Dockerfile
    ports:
      - "8013:8013"
    env_file:
      - .env.example

  llm-response-agent-service:
    build:
      context: .
      dockerfile: llm-response-agent-service/Dockerfile
    ports:
      - "8014:8014"
    env_file:
      - .env.example
""",
    )
    write(
        ROOT / "Makefile",
        """.PHONY: dev-up dev-down test

dev-up:
\tdocker compose -f docker-compose.dev.yml up --build -d

dev-down:
\tdocker compose -f docker-compose.dev.yml down

test:
\tcd ai-workflow-service && pytest -q || true
\tcd llm-intent-parser-service && pytest -q || true
\tcd ai-context-builder-service && pytest -q || true
\tcd analytics-service && pytest -q || true
\tcd llm-response-agent-service && pytest -q || true
""",
    )
    readme_path = ROOT / "README.md"
    if not readme_path.read_text(encoding="utf-8").strip():
        write(
            readme_path,
            """# AI Financial Assistant — Services Monorepo

Skeleton monorepo for the AI pipeline: workflow orchestration, intent parsing, context building, analytics, and response generation.

## Services

| Service | Port | Main endpoint |
|---------|------|---------------|
| ai-workflow-service | 8010 | RabbitMQ + `/api/v1/workflows` |
| llm-intent-parser-service | 8011 | `POST /api/v1/intent/parse` |
| ai-context-builder-service | 8012 | `POST /api/v1/context/build` |
| analytics-service | 8013 | `POST /api/v1/analytics/run` |
| llm-response-agent-service | 8014 | `POST /api/v1/response/generate` |

## Quick start

```bash
cp .env.example .env
make dev-up
```

## Documentation

See `docs/` for architecture (do not replace when extending).

## Status

Skeleton only — implement business logic behind `TODO` markers.
""",
        )


def main() -> None:
    scaffold_packages()
    scaffold_ai_workflow()
    scaffold_intent_parser()
    scaffold_context_builder()
    scaffold_analytics()
    scaffold_response_agent()
    scaffold_infra()
    scaffold_root()
    print("Scaffold complete.")


if __name__ == "__main__":
    main()
