"""Data quality gate tests."""
from app.runner.analytics_runner import AnalyticsRunner


def test_blocked_does_not_invent_values(blocked_context_package):
    result = AnalyticsRunner().run(blocked_context_package)
    assert result.analysis_result.expected_savings == 0.0
    assert result.analysis_result.risk_score == 0.0
    assert any("cannot run" in w.lower() for w in result.warnings if isinstance(w, str))
