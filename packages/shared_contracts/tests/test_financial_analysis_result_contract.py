"""Financial analysis result contract tests."""
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from conftest import minimal_financial_analysis_result


def test_financial_analysis_result_can_be_created() -> None:
    result = minimal_financial_analysis_result()
    assert result.executed_functions == ["budget_recommendation"]
    assert "budget_recommendation" in result.function_results
    assert result.analysis_result.expected_savings == 6000


def test_financial_analysis_result_has_function_results_dict() -> None:
    result = minimal_financial_analysis_result()
    assert isinstance(result.function_results, dict)


def test_financial_analysis_result_model_fields() -> None:
    fields = set(FinancialAnalysisResult.model_fields)
    assert "function_results" in fields
    assert "analysis_result" in fields
    assert "executed_functions" in fields
    assert "result_type" not in fields
    assert "calculation_mode" not in fields
    assert "status" not in fields
