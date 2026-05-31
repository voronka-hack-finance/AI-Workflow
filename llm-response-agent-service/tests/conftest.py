"""Shared test fixtures."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.response_pipeline.response_agent_service import ResponseAgentService
from shared_contracts.common import FunctionResultStatus
from shared_contracts.financial_analysis_result import (
    AnalysisResult,
    FinancialAnalysisMetadata,
    FinancialAnalysisResult,
    FunctionResult,
    FunctionResultMetadata,
)
from shared_contracts.intent_result import IntentResult


def _load_dotenv_keys(*keys: str) -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    wanted = set(keys)
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key not in wanted:
            continue
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv_keys("RUN_REAL_LLM_RESPONSE_TESTS")
os.environ["RESPONSE_AGENT_LLM_PROVIDER"] = "mock"
get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def service() -> ResponseAgentService:
    get_settings.cache_clear()
    return ResponseAgentService(settings=get_settings())


def minimal_intent(**overrides: object) -> IntentResult:
    payload = {
        "primary_intent": "budget_recommendation",
        "intents": ["budget_recommendation"],
        "intent_confidence": 0.92,
        "requested_functions": ["budget_recommendation"],
    }
    payload.update(overrides)
    return IntentResult.model_validate(payload)


def minimal_far(**overrides: object) -> FinancialAnalysisResult:
    payload = {
        "request_id": "req_001",
        "user_id": "user_123",
        "period": {"type": "current_month", "start_date": "2026-05-01", "end_date": "2026-05-31"},
        "executed_functions": ["budget_recommendation"],
        "function_results": {
            "budget_recommendation": {
                "function_name": "budget_recommendation",
                "status": FunctionResultStatus.SUCCESS,
                "result": {"expected_savings": 6000},
                "metadata": {"calculated_at": "2026-05-29T12:00:00Z"},
            }
        },
        "analysis_result": {
            "expected_savings": 6000,
            "recommendation_type": "budget_optimization",
            "risk_level": "medium",
        },
        "metadata": {"calculated_at": "2026-05-29T12:00:00Z"},
    }
    payload.update(overrides)
    return FinancialAnalysisResult.model_validate(payload)


def generate_payload(**overrides: object) -> dict[str, object]:
    intent = minimal_intent()
    far = minimal_far()
    payload: dict[str, object] = {
        "request_id": "req_002",
        "workflow_run_id": "run_002",
        "original_user_message": "Дай рекомендацию по бюджету",
        "intent_result": intent.model_dump(mode="json"),
        "financial_analysis_result": far.model_dump(mode="json"),
        "constraints": {"protected_categories": ["Здоровье"]},
        "style": {"agent_style": "balanced", "difficulty": "medium", "output_format": "chat_text"},
    }
    payload.update(overrides)
    return payload
