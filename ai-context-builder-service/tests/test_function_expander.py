"""Function expander tests."""
from app.planning.function_expander import FunctionExpander


def test_expander_budget_recommendation() -> None:
    expander = FunctionExpander()
    expanded = expander.expand(["budget_recommendation"])
    assert expanded == [
        "income_analysis",
        "expense_breakdown",
        "cashflow_analysis",
        "transfer_analysis",
        "spending_leak_detection",
        "emergency_fund_analysis",
        "debt_analysis",
        "budget_recommendation",
    ]


def test_expander_deduplicates_shared_dependencies() -> None:
    expander = FunctionExpander()
    expanded = expander.expand(["budget_recommendation", "goal_analysis"])
    assert expanded.count("income_analysis") == 1
    assert expanded.count("cashflow_analysis") == 1
    assert expanded[-2:] == ["budget_recommendation", "goal_analysis"]
