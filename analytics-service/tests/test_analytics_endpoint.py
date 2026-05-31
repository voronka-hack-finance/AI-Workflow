"""Analytics endpoint tests."""
from shared_contracts.context_package import ContextPackage


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_run_analysis_returns_financial_analysis_result(
    client, context_package_with_transactions: ContextPackage
):
    response = client.post(
        "/api/v1/analytics/run",
        json=context_package_with_transactions.model_dump(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["request_id"] == "req_test_001"
    assert body["user_id"] == "user_123"
    assert "function_results" in body
    assert "analysis_result" in body
    assert "metadata" in body
    assert "period_analysis" in body["function_results"]
    forbidden = {"result_type", "workflow_run_id", "chat_id", "status", "calculation_mode", "comparison"}
    assert forbidden.isdisjoint(body.keys())


def test_run_analysis_blocked(client, blocked_context_package: ContextPackage):
    response = client.post(
        "/api/v1/analytics/run",
        json=blocked_context_package.model_dump(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["executed_functions"] == []
    assert body["function_results"] == {}
    assert body["analysis_result"]["expected_savings"] == 0.0
