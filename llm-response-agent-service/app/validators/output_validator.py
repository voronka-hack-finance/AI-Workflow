"""Output safety validator."""
from __future__ import annotations

from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, StyleInput
from shared_contracts.response_agent_result import AgentOutput, OutputValidationIssue, OutputValidationResult

from app.helpers.facts import extract_allowed_numbers, extract_allowed_numbers_from_agent_outputs
from app.validators.hallucination_guard import (
    find_guarantee_phrases,
    find_hallucinated_numbers_with_allowed,
    find_protected_category_violations,
    find_risk_level_mismatch,
)


class OutputValidator:
    def validate(
        self,
        *,
        final_answer: str,
        financial_analysis_result: FinancialAnalysisResult,
        constraints: ConstraintsInput,
        style: StyleInput,
        warnings_to_consider: list[str],
        agent_outputs: list[AgentOutput] | None = None,
    ) -> OutputValidationResult:
        del style, warnings_to_consider
        issues: list[OutputValidationIssue] = []
        required_fixes: list[str] = []

        if not final_answer.strip():
            issues.append(OutputValidationIssue(type="empty_answer", message="Final answer is empty"))
            required_fixes.append("Provide a non-empty final answer.")

        allowed_numbers = extract_allowed_numbers(financial_analysis_result)
        if agent_outputs:
            allowed_numbers |= extract_allowed_numbers_from_agent_outputs(agent_outputs)

        for message in find_hallucinated_numbers_with_allowed(final_answer, allowed_numbers):
            issues.append(OutputValidationIssue(type="hallucinated_number", message=message))
            required_fixes.append("Remove numbers that are not present in analytics facts.")

        for message in find_guarantee_phrases(final_answer):
            issues.append(OutputValidationIssue(type="financial_guarantee", message=message))
            required_fixes.append("Avoid financial guarantees and investment promises.")

        for message in find_protected_category_violations(final_answer, constraints):
            issues.append(OutputValidationIssue(type="protected_category", message=message))
            required_fixes.append("Do not recommend cutting protected categories.")

        for message in find_risk_level_mismatch(
            final_answer,
            financial_analysis_result.analysis_result.risk_level,
        ):
            issues.append(OutputValidationIssue(type="risk_level_mismatch", message=message))
            required_fixes.append("Do not change risk_level from analytics.")

        if issues:
            return OutputValidationResult(
                validation_status="failed",
                can_send_to_user=False,
                issues=issues,
                required_fixes=list(dict.fromkeys(required_fixes)),
            )

        return OutputValidationResult(
            validation_status="passed",
            can_send_to_user=True,
            issues=[],
            required_fixes=[],
        )
