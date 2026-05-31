"""Content agents registry."""
from __future__ import annotations

from app.agents.base_agent import BaseAgent
from app.agents.budget_planner_agent import BudgetPlannerAgent
from app.agents.growth_agent import GrowthAgent
from app.agents.habit_coach_agent import HabitCoachAgent
from app.agents.safety_agent import SafetyAgent
from app.agents.spending_detective_agent import SpendingDetectiveAgent
from shared_contracts.common import ContentAgentName

AGENT_REGISTRY: dict[str, BaseAgent] = {
    ContentAgentName.SAFETY: SafetyAgent(),
    ContentAgentName.SPENDING_DETECTIVE: SpendingDetectiveAgent(),
    ContentAgentName.GROWTH: GrowthAgent(),
    ContentAgentName.BUDGET_PLANNER: BudgetPlannerAgent(),
    ContentAgentName.HABIT_COACH: HabitCoachAgent(),
}


def get_agent(agent_name: str) -> BaseAgent:
    agent = AGENT_REGISTRY.get(agent_name)
    if agent is None:
        raise KeyError(f"Unknown content agent: {agent_name}")
    return agent
