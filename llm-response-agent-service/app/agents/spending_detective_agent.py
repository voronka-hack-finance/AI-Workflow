"""SpendingDetectiveAgent."""
from app.agents.base_agent import BaseAgent
from app.schemas.agent_output import AgentOutput


class SpendingDetectiveAgent(BaseAgent):
    name = "spendingdetective"

    async def run(self, context: dict) -> AgentOutput:
        # TODO: implement LLM call
        return AgentOutput(agent_name=self.name)
