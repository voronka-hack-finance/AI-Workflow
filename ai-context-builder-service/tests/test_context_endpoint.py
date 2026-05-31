"""Context build endpoint and scenario tests."""
from fastapi.testclient import TestClient

from app.main import app
from shared_contracts.common import CalculationMode, PeriodType

from tests.conftest import (
    budget_intent,
    build_request,
    category_intent_missing_focus,
    comparison_intent,
    goal_intent_full,
    goal_intent_missing_amount,
)

client = TestClient(app)


def _post_build(request_payload: dict) -> dict:
    response = client.post("/api/v1/context/build", json=request_payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_build_context_budget_recommendation_scenario() -> None:
    payload = build_request(budget_intent()).model_dump(mode="json")
    body = _post_build(payload)

    assert body["context_builder"]["requested_functions"] == ["budget_recommendation"]
    expanded = body["context_builder"]["expanded_functions"]
    assert "income_analysis" in expanded
    assert "budget_recommendation" in expanded
    assert len(body["context_builder"]["execution_plan"]) == len(expanded)
    assert body["analytics_request"]["functions_to_execute"] == expanded
    assert isinstance(body["data"]["transactions"], list)
    assert isinstance(body["data"]["category_profiles"], list)


def test_build_context_goal_analysis_full() -> None:
    payload = build_request(goal_intent_full()).model_dump(mode="json")
    body = _post_build(payload)
    assert body["data_quality"]["can_run_analytics"] is True


def test_build_context_goal_analysis_missing_amount() -> None:
    payload = build_request(goal_intent_missing_amount()).model_dump(mode="json")
    body = _post_build(payload)
    assert body["data_quality"]["can_run_analytics"] is True
    assert body["data_quality"]["calculation_mode"] == CalculationMode.PARTIAL
    assert "goal.amount" in body["data_quality"]["missing_hard_required_fields"]


def test_build_context_missing_savings_partial() -> None:
    payload = build_request(budget_intent(), user_id="user_missing_savings").model_dump(mode="json")
    body = _post_build(payload)
    assert body["data_quality"]["can_run_analytics"] is True
    assert body["data_quality"]["calculation_mode"] == CalculationMode.PARTIAL
    assert "current_savings" in body["data_quality"]["missing_soft_required_fields"]


def test_build_context_comparison_requests_previous_period() -> None:
    payload = build_request(comparison_intent()).model_dump(mode="json")
    body = _post_build(payload)
    assert "previous_period_transactions" in body["context_builder"]["data_requirements"]["hard_required_data"]
    assert len(body["data"]["previous_period_transactions"]) > 0


def test_build_context_category_analysis_missing_focus() -> None:
    payload = build_request(category_intent_missing_focus()).model_dump(mode="json")
    body = _post_build(payload)
    assert "focus.category" in body["data_quality"]["missing_hard_required_fields"]
    assert body["data_quality"]["calculation_mode"] == CalculationMode.PARTIAL


def test_build_context_invalid_payload_returns_422() -> None:
    response = client.post("/api/v1/context/build", json={"user_id": "only_user"})
    assert response.status_code == 422


def test_build_context_resolves_period() -> None:
    payload = build_request(budget_intent()).model_dump(mode="json")
    body = _post_build(payload)
    resolved = body["context_builder"]["resolved_period"]
    assert resolved["type"] == PeriodType.CURRENT_MONTH
    assert resolved["start_date"] == "2026-05-01"
    assert resolved["end_date"] == "2026-05-31"
    assert resolved["source"] == "DateResolver"
