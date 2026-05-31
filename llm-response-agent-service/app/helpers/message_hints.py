"""Message hints for habit coach routing."""
from __future__ import annotations

_ACTION_HINTS = (
    "что делать",
    "что мне делать",
    "дай шаги",
    "give me steps",
    "how to start",
    "с чего начать",
    "как начать",
)


def has_action_plan_hints(message: str) -> bool:
    lowered = message.strip().lower()
    return any(hint in lowered for hint in _ACTION_HINTS)
