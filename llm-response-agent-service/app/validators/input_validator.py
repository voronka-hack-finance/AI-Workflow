"""Input safety validator."""
from __future__ import annotations

from shared_contracts.common import FunctionResultStatus
from shared_contracts.financial_analysis_result import FinancialAnalysisResult
from shared_contracts.intent_result import ConstraintsInput, IntentResult, StyleInput
from shared_contracts.response_agent_result import InputValidationResult

_EXPENSE_FUNCTIONS = frozenset(
    {"expense_breakdown", "spending_leak_detection", "category_analysis"}
)
_DEBT_FUNCTIONS = frozenset({"debt_analysis"})


class InputValidator:
    def validate(
        self,
        *,
        intent: IntentResult,
        financial_analysis_result: FinancialAnalysisResult | None,
        constraints: ConstraintsInput,
        style: StyleInput,
    ) -> InputValidationResult:
        del constraints, style
        missing_fields: list[str] = []
        warnings_to_consider: list[str] = list(financial_analysis_result.warnings) if financial_analysis_result else []

        if financial_analysis_result is None:
            return InputValidationResult(
                validation_status="error",
                can_run_agents=False,
                missing_fields=["financial_analysis_result"],
                warnings_to_consider=warnings_to_consider,
                message="Не удалось получить результаты анализа.",
            )

        far = financial_analysis_result
        requested = list(intent.requested_functions or [intent.primary_intent])
        requested_set = set(requested)

        if not far.analysis_result:
            missing_fields.append("analysis_result")

        for function_name in requested:
            fn_result = far.function_results.get(function_name)
            if fn_result is None:
                missing_fields.append(f"function_results.{function_name}")
                continue
            if fn_result.status in {FunctionResultStatus.ERROR, "error"}:
                return InputValidationResult(
                    validation_status="error",
                    can_run_agents=False,
                    missing_fields=[f"function_results.{function_name}.status"],
                    warnings_to_consider=warnings_to_consider,
                    message="Анализ завершился с ошибкой. Попробуйте позже.",
                )
            if fn_result.status in {FunctionResultStatus.NEEDS_CLARIFICATION, "needs_clarification"}:
                return InputValidationResult(
                    validation_status="needs_clarification",
                    can_run_agents=False,
                    missing_fields=[f"function_results.{function_name}.status"],
                    warnings_to_consider=warnings_to_consider,
                    message="Для ответа нужны дополнительные данные.",
                )
            if fn_result.status in {FunctionResultStatus.EMPTY_RESULT, "empty_result"}:
                missing_fields.append(f"function_results.{function_name}.empty_result")

        if requested_set & _EXPENSE_FUNCTIONS:
            expense_result = next(
                (far.function_results[name] for name in requested_set & _EXPENSE_FUNCTIONS if name in far.function_results),
                None,
            )
            if expense_result and expense_result.status in {"empty_result", FunctionResultStatus.EMPTY_RESULT}:
                return InputValidationResult(
                    validation_status="needs_clarification",
                    can_run_agents=False,
                    missing_fields=["transactions"],
                    warnings_to_consider=warnings_to_consider,
                    message="Недостаточно данных о расходах за выбранный период.",
                )

        if "emergency_fund_analysis" in requested_set:
            emergency = far.function_results.get("emergency_fund_analysis")
            current_savings = None
            if emergency and emergency.result:
                current_savings = emergency.result.get("current_savings")
            if current_savings is None:
                return InputValidationResult(
                    validation_status="needs_clarification",
                    can_run_agents=False,
                    missing_fields=["current_savings"],
                    warnings_to_consider=warnings_to_consider,
                    message="Укажите текущие накопления для оценки финансовой подушки.",
                )

        if "goal_analysis" in requested_set:
            goal = intent.goal
            if goal.amount is None or goal.deadline_months is None:
                return InputValidationResult(
                    validation_status="needs_clarification",
                    can_run_agents=False,
                    missing_fields=["goal.amount", "goal.deadline_months"],
                    warnings_to_consider=warnings_to_consider,
                    message="Уточните сумму цели и срок, к которому хотите её достичь.",
                )

        if requested_set & _DEBT_FUNCTIONS:
            debt = far.function_results.get("debt_analysis")
            income_missing = debt is None or debt.result.get("monthly_income") in (None, 0)
            if income_missing:
                return InputValidationResult(
                    validation_status="needs_clarification",
                    can_run_agents=False,
                    missing_fields=["income"],
                    warnings_to_consider=warnings_to_consider,
                    message="Недостаточно данных о доходе для оценки долговой нагрузки.",
                )

        if missing_fields:
            return InputValidationResult(
                validation_status="needs_clarification",
                can_run_agents=False,
                missing_fields=missing_fields,
                warnings_to_consider=warnings_to_consider,
                message="Для ответа не хватает части результатов анализа.",
            )

        return InputValidationResult(
            validation_status="passed",
            can_run_agents=True,
            missing_fields=[],
            warnings_to_consider=warnings_to_consider,
            message=None,
        )
