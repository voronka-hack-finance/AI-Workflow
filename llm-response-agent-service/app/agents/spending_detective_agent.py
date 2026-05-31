"""SpendingDetectiveAgent."""
from app.agents.base_agent import BaseAgent
from app.prompts.spending_detective_prompt import build_spending_detective_messages


class SpendingDetectiveAgent(BaseAgent):
    name = "spending_detective"
    build_messages = staticmethod(build_spending_detective_messages)
