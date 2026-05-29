"""Base response agent."""
from abc import ABC, abstractmethod

from app.schemas.agent_output import AgentOutput


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, context: dict) -> AgentOutput:
        # TODO: implement
        return AgentOutput(agent_name=self.name)
