"""Single agent output."""
from pydantic import BaseModel


class AgentOutput(BaseModel):
    agent_name: str
    content: str = ""
