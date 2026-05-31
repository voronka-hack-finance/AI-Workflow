"""Data requirements resolver tests."""
from app.planning.data_requirements_resolver import DataRequirementsResolver
from app.planning.function_expander import FunctionExpander
from tests.conftest import category_intent_missing_focus, comparison_intent, goal_intent_missing_amount


def test_goal_analysis_missing_amount_fields() -> None:
    resolver = DataRequirementsResolver()
    expanded = FunctionExpander().expand(["goal_analysis"])
    requirements = resolver.resolve(expanded, goal_intent_missing_amount())
    assert "goal.amount" in requirements.hard_required_fields
    assert "goal.deadline_months" in requirements.hard_required_fields


def test_comparison_adds_previous_period_transactions() -> None:
    resolver = DataRequirementsResolver()
    expanded = FunctionExpander().expand(["expense_breakdown"])
    requirements = resolver.resolve(expanded, comparison_intent())
    assert "previous_period_transactions" in requirements.hard_required_data


def test_category_analysis_missing_focus() -> None:
    resolver = DataRequirementsResolver()
    expanded = FunctionExpander().expand(["category_analysis"])
    requirements = resolver.resolve(expanded, category_intent_missing_focus())
    assert "focus.category" in requirements.hard_required_fields
