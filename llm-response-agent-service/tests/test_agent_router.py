"""Agent router tests."""
from app.response_pipeline.agent_router import AgentRouter
from tests.conftest import minimal_far, minimal_intent


def test_router_selects_budget_planner() -> None:
    routing = AgentRouter().select(
        intent=minimal_intent(requested_functions=["budget_recommendation"]),
        financial_analysis_result=minimal_far(),
        constraints=minimal_intent().constraints,
        original_user_message="Дай рекомендацию по бюджету",
    )
    assert "budget_planner" in routing.selected_agents


def test_router_selects_spending_detective() -> None:
    routing = AgentRouter().select(
        intent=minimal_intent(
            primary_intent="expense_breakdown",
            requested_functions=["expense_breakdown"],
        ),
        financial_analysis_result=minimal_far(
            executed_functions=["expense_breakdown"],
            function_results={
                "expense_breakdown": {
                    "function_name": "expense_breakdown",
                    "status": "success",
                    "result": {"total_expenses": 50000},
                    "metadata": {"calculated_at": "2026-05-29T12:00:00Z"},
                }
            },
        ),
        constraints=minimal_intent().constraints,
        original_user_message="Куда уходят деньги?",
    )
    assert "spending_detective" in routing.selected_agents


def test_router_selects_growth_for_goal_analysis() -> None:
    routing = AgentRouter().select(
        intent=minimal_intent(
            primary_intent="goal_analysis",
            requested_functions=["goal_analysis"],
            goal={"name": "ноутбук", "amount": 120000, "deadline_months": 8},
        ),
        financial_analysis_result=minimal_far(
            executed_functions=["goal_analysis"],
            function_results={
                "goal_analysis": {
                    "function_name": "goal_analysis",
                    "status": "success",
                    "result": {"progress_percent": 20},
                    "metadata": {"calculated_at": "2026-05-29T12:00:00Z"},
                }
            },
            analysis_result={"recommendation_type": "save_for_goal"},
        ),
        constraints=minimal_intent().constraints,
        original_user_message="Как накопить на ноутбук?",
    )
    assert "growth" in routing.selected_agents


def test_router_selects_safety_for_high_risk() -> None:
    routing = AgentRouter().select(
        intent=minimal_intent(requested_functions=["emergency_fund_analysis"]),
        financial_analysis_result=minimal_far(
            analysis_result={"risk_level": "high", "problem_tags": ["low_emergency_fund"]},
        ),
        constraints=minimal_intent().constraints,
        original_user_message="Оцени финансовую подушку",
    )
    assert "safety" in routing.selected_agents


def test_router_selects_spending_detective_for_period_analysis() -> None:
    routing = AgentRouter().select(
        intent=minimal_intent(
            primary_intent="period_analysis",
            requested_functions=["period_analysis"],
            focus={"direction": "expense"},
        ),
        financial_analysis_result=minimal_far(
            executed_functions=["period_analysis"],
            function_results={
                "period_analysis": {
                    "function_name": "period_analysis",
                    "status": "success",
                    "result": {
                        "total_expenses": 1447762.38,
                        "top_categories": [{"name": "Переводы", "amount": 546879.55}],
                    },
                    "metadata": {"calculated_at": "2026-05-31T03:07:12Z"},
                }
            },
            analysis_result={"main_problem": "period_summary"},
        ),
        constraints=minimal_intent().constraints,
        original_user_message="проанализируй расходы за последние 6 месяцев",
    )
    assert routing.routing_status == "success"
    assert "spending_detective" in routing.selected_agents


def test_router_selects_habit_coach_for_action_plan() -> None:
    routing = AgentRouter().select(
        intent=minimal_intent(requested_functions=["action_plan"]),
        financial_analysis_result=minimal_far(
            executed_functions=["action_plan"],
            function_results={
                "action_plan": {
                    "function_name": "action_plan",
                    "status": "success",
                    "result": {"steps": ["step1"]},
                    "metadata": {"calculated_at": "2026-05-29T12:00:00Z"},
                }
            },
        ),
        constraints=minimal_intent().constraints,
        original_user_message="Что мне делать дальше?",
    )
    assert "habit_coach" in routing.selected_agents
