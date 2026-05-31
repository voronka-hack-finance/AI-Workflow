"""SafetyAgent."""
from app.agents.base_agent import BaseAgent
from app.prompts.safety_agent_prompt import build_safety_agent_messages


class SafetyAgent(BaseAgent):
    name = "safety"
    build_messages = staticmethod(build_safety_agent_messages)
