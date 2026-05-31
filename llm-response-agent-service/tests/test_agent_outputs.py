"""Agent output tests."""
import pytest

from app.agents import get_agent
from app.llm.provider_factory import create_llm_provider
from tests.conftest import minimal_far, minimal_intent


@pytest.mark.asyncio
async def test_mock_agents_return_valid_outputs() -> None:
    provider = create_llm_provider()
    intent = minimal_intent()
    far = minimal_far()
    for agent_name in ("safety", "budget_planner", "growth"):
        output = await get_agent(agent_name).run(
            intent=intent,
            far=far,
            constraints=intent.constraints,
            style=intent.style,
            original_user_message="Тест",
            provider=provider,
        )
        assert output.agent_name == agent_name
        assert output.status == "success"
        assert output.summary
