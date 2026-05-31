"""Boundary and contract tests."""
import json

from app.runner.analytics_runner import AnalyticsRunner


def test_no_raw_transactions_in_output(context_package_with_transactions):
    result = AnalyticsRunner().run(context_package_with_transactions)
    serialized = json.dumps(result.model_dump())
    assert "tx_1" not in serialized or '"transactions"' not in serialized
    for fn_result in result.function_results.values():
        assert "transactions" not in fn_result.result


def test_can_run_analytics_false_returns_empty_results(blocked_context_package):
    result = AnalyticsRunner().run(blocked_context_package)
    assert result.executed_functions == []
    assert not result.function_results
