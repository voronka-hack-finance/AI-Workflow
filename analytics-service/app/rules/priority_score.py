"""Priority mapping from risk score."""
from __future__ import annotations

from shared_contracts.common import Priority


def risk_to_priority(risk_score: float) -> Priority:
    if risk_score >= 70:
        return Priority.CRITICAL
    if risk_score >= 50:
        return Priority.HIGH
    if risk_score >= 30:
        return Priority.MEDIUM
    return Priority.LOW
