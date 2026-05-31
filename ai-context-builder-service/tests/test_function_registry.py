"""Function registry tests."""
import pytest

from app.registry.function_registry import FunctionRegistry, UnknownFunctionError


def test_registry_knows_mvp_functions() -> None:
    registry = FunctionRegistry()
    assert registry.is_known("budget_recommendation")
    assert not registry.is_known("unknown_fn")


def test_registry_rejects_unknown_function() -> None:
    registry = FunctionRegistry()
    with pytest.raises(UnknownFunctionError):
        registry.validate_known("unknown_fn")


def test_budget_recommendation_dependencies() -> None:
    registry = FunctionRegistry()
    deps = registry.get_dependencies("budget_recommendation")
    assert "income_analysis" in deps
    assert "debt_analysis" in deps


def test_expand_budget_recommendation_includes_dependencies() -> None:
    registry = FunctionRegistry()
    expanded = registry.expand(["budget_recommendation"])
    assert expanded[0] == "income_analysis"
    assert "budget_recommendation" in expanded
    assert len(expanded) == len(set(expanded))


def test_expand_detects_unknown_function() -> None:
    registry = FunctionRegistry()
    with pytest.raises(UnknownFunctionError):
        registry.expand(["not_a_function"])


def test_expand_no_cycle_for_valid_graph() -> None:
    registry = FunctionRegistry()
    expanded = registry.expand(["action_plan"])
    assert "budget_recommendation" in expanded


def test_get_data_requirements_includes_comparison_data() -> None:
    registry = FunctionRegistry()
    req = registry.get_data_requirements(["expense_breakdown"], comparison_enabled=True)
    assert "previous_period_transactions" in req.hard_required_data
