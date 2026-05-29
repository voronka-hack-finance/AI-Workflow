"""GrowthAgent."""
from app.agents.base_agent import BaseAgent
from app.schemas.agent_output import AgentOutput


class GrowthAgent(BaseAgent):
    name = "growth"

    async def run(self, context: dict) -> AgentOutput:
        # TODO: implement LLM call
        return AgentOutput(agent_name=self.name)
