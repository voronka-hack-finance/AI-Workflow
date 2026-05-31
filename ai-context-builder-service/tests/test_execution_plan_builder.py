"""Execution plan builder tests."""
from app.planning.execution_plan_builder import ExecutionPlanBuilder
from app.planning.function_expander import FunctionExpander


def test_execution_plan_order_and_dependencies() -> None:
    expander = FunctionExpander()
    expanded = expander.expand(["budget_recommendation"])
    builder = ExecutionPlanBuilder()
    plan = builder.build(expanded)

    assert len(plan) == len(expanded)
    assert plan[0].function_name == "income_analysis"
    assert plan[0].depends_on == []
    assert plan[-1].function_name == "budget_recommendation"
    assert "debt_analysis" in plan[-1].depends_on

    seen: set[str] = set()
    for item in plan:
        for dep in item.depends_on:
            assert dep in seen
        seen.add(item.function_name)
