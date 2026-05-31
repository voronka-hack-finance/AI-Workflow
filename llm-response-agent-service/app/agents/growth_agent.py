"""GrowthAgent."""
from app.agents.base_agent import BaseAgent
from app.prompts.growth_agent_prompt import build_growth_agent_messages


class GrowthAgent(BaseAgent):
    name = "growth"
    build_messages = staticmethod(build_growth_agent_messages)
