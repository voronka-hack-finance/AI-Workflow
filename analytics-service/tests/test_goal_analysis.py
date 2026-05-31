"""Goal analysis tests."""
from app.runner.analytics_runner import AnalyticsRunner
from shared_contracts.context_package import ContextPackage, ExecutionPlanItem


def _package_with_goal(base: ContextPackage) -> ContextPackage:
    base.data.user_context.goal_amount = 120000.0
    base.data.user_context.goal_deadline_months = 6
    base.analytics_request.functions_to_execute = [
        "income_analysis",
        "expense_breakdown",
        "cashflow_analysis",
        "goal_analysis",
    ]
    base.context_builder.execution_plan = [
        ExecutionPlanItem(step=1, function_name="income_analysis", depends_on=[]),
        ExecutionPlanItem(step=2, function_name="expense_breakdown", depends_on=[]),
        ExecutionPlanItem(
            step=3,
            function_name="cashflow_analysis",
            depends_on=["income_analysis", "expense_breakdown"],
        ),
        ExecutionPlanItem(
            step=4,
            function_name="goal_analysis",
            depends_on=["cashflow_analysis"],
        ),
    ]
    return base


def test_goal_needs_clarification_without_goal(context_package_with_transactions):
    pkg = context_package_with_transactions.model_copy(deep=True)
    pkg.analytics_request.functions_to_execute = ["goal_analysis"]
    pkg.context_builder.execution_plan = [
        ExecutionPlanItem(step=1, function_name="goal_analysis", depends_on=[])
    ]
    result = AnalyticsRunner().run(pkg)
    goal = result.function_results["goal_analysis"]
    assert goal.status == "needs_clarification"


def test_goal_success_with_goal_fields(context_package_with_transactions):
    pkg = _package_with_goal(context_package_with_transactions.model_copy(deep=True))
    result = AnalyticsRunner().run(pkg)
    goal = result.function_results.get("goal_analysis")
    assert goal is not None
    assert goal.status == "success"
    assert goal.result["goal_amount"] == 120000.0
