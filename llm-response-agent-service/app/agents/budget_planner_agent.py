"""BudgetPlannerAgent."""
from app.agents.base_agent import BaseAgent
from app.prompts.budget_planner_prompt import build_budget_planner_messages


class BudgetPlannerAgent(BaseAgent):
    name = "budget_planner"
    build_messages = staticmethod(build_budget_planner_messages)
