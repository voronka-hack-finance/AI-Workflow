"""AgentOutput contract."""
from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    agent_name: str = ''
    # TODO: extend fields per architecture docs
