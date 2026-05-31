"""HabitCoachAgent."""
from app.agents.base_agent import BaseAgent
from app.prompts.habit_coach_prompt import build_habit_coach_messages


class HabitCoachAgent(BaseAgent):
    name = "habit_coach"
    build_messages = staticmethod(build_habit_coach_messages)
