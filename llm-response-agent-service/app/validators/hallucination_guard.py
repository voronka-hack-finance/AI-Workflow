"""Hallucination guard for final answer validation."""
from __future__ import annotations

import re

from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput

from app.helpers.facts import extract_answer_numbers

_GUARANTEE_PATTERNS = (
    r"\bгарантиру",
    r"\b100\s*%",
    r"\bguarantee\b",
    r"\binvestment return\b",
    r"\bдоходность\s+\d",
)

_CUT_PATTERNS = (
    r"сократ(ить|ите|и)",
    r"уреж(ь|ьте|ьте)",
    r"сокращ",
    r"cut ",
)


def find_hallucinated_numbers(final_answer: str, far: FinancialAnalysisResult) -> list[str]:
    from app.helpers.facts import extract_allowed_numbers

    return find_hallucinated_numbers_with_allowed(final_answer, extract_allowed_numbers(far))


def find_hallucinated_numbers_with_allowed(final_answer: str, allowed: set[str]) -> list[str]:
    issues: list[str] = []
    for number in extract_answer_numbers(final_answer):
        if number not in allowed:
            issues.append(f"Unexpected number in final answer: {number}")
    return issues


_RISK_LEVEL_ALIASES: dict[str, tuple[str, ...]] = {
    "low": ("low", "низк"),
    "medium": ("medium", "средн"),
    "high": ("high", "высок"),
    "critical": ("critical", "критич"),
}


def _answer_mentions_risk_level(final_answer: str, level: str) -> bool:
    lowered = final_answer.lower()
    for alias in _RISK_LEVEL_ALIASES.get(level, (level,)):
        if alias in lowered:
            return True
    return False


def find_risk_level_mismatch(final_answer: str, risk_level: str | None) -> list[str]:
    if not risk_level:
        return []

    expected = str(risk_level).lower()
    issues: list[str] = []
    for other_level in _RISK_LEVEL_ALIASES:
        if other_level == expected:
            continue
        if _answer_mentions_risk_level(final_answer, other_level):
            issues.append(
                f"Final answer mentions risk level '{other_level}' "
                f"but analytics risk_level is '{expected}'"
            )
            break
    return issues


def find_guarantee_phrases(final_answer: str) -> list[str]:
    issues: list[str] = []
    lowered = final_answer.lower()
    for pattern in _GUARANTEE_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            issues.append(f"Potential financial guarantee detected: {pattern}")
    return issues


def find_protected_category_violations(
    final_answer: str,
    constraints: ConstraintsInput,
) -> list[str]:
    issues: list[str] = []
    if not constraints.protected_categories:
        return issues
    lowered = final_answer.lower()
    for category in constraints.protected_categories:
        category_lower = category.lower()
        if category_lower not in lowered:
            continue
        for pattern in _CUT_PATTERNS:
            if re.search(pattern, lowered):
                issues.append(f"Protected category may be recommended for cutting: {category}")
                break
    return issues
