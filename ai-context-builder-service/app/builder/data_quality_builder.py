"""Build data_quality section for Context Package."""
from __future__ import annotations

from shared_contracts.common import CalculationMode
from shared_contracts.context_package import (
    ContextPackageData,
    DataCoverage,
    DataQuality,
    DataRequirements,
)
from shared_contracts.intent_result import IntentResult

from app.data_adapters.warnings import NormalizationWarnings


class DataQualityBuilder:
    def build(
        self,
        *,
        data: ContextPackageData,
        requirements: DataRequirements,
        intent_result: IntentResult,
        normalization: NormalizationWarnings,
    ) -> DataQuality:
        missing_hard_data = self._missing_data(data, requirements.hard_required_data)
        missing_soft_data = self._missing_data(data, requirements.soft_required_data)
        missing_optional_data = self._missing_data(data, requirements.optional_data)

        missing_hard_fields = self._missing_fields(intent_result, data, requirements.hard_required_fields)
        missing_soft_fields = self._missing_fields(intent_result, data, requirements.soft_required_fields)
        missing_optional_fields = self._missing_fields(
            intent_result,
            data,
            requirements.optional_enrichment_fields,
        )

        has_missing_hard = bool(missing_hard_data or missing_hard_fields)
        has_missing_soft = bool(missing_soft_data or missing_soft_fields)

        if has_missing_hard:
            can_run = True
            mode = CalculationMode.PARTIAL
        elif has_missing_soft:
            can_run = True
            mode = CalculationMode.PARTIAL
        else:
            can_run = True
            mode = CalculationMode.FULL

        coverage = DataCoverage(
            transactions_count=len(data.transactions),
            previous_period_transactions_count=len(data.previous_period_transactions),
            has_user_context=self._has_user_context(data),
            has_category_profiles=bool(data.category_profiles),
            has_existing_financial_analysis_result=data.existing_financial_analysis_result
            is not None,
        )

        return DataQuality(
            can_run_analytics=can_run,
            calculation_mode=mode,
            has_missing_hard_required_data=has_missing_hard,
            has_missing_soft_required_data=has_missing_soft,
            missing_hard_required_data=missing_hard_data,
            missing_soft_required_data=missing_soft_data,
            missing_optional_data=missing_optional_data,
            missing_hard_required_fields=missing_hard_fields,
            missing_soft_required_fields=missing_soft_fields,
            missing_optional_enrichment_fields=missing_optional_fields,
            normalization_warnings=list(normalization.warnings),
            unmapped_categories=list(normalization.unmapped_categories),
            ambiguous_transactions=list(normalization.ambiguous_transactions),
            data_coverage=coverage,
        )

    def _missing_data(self, data: ContextPackageData, required: list[str]) -> list[str]:
        missing: list[str] = []
        for key in required:
            if key == "transactions" and not data.transactions:
                missing.append(key)
            elif key == "previous_period_transactions" and not data.previous_period_transactions:
                missing.append(key)
            elif key == "user_context" and not self._has_user_context(data):
                missing.append(key)
            elif key == "category_profiles" and not data.category_profiles:
                missing.append(key)
            elif key == "existing_financial_analysis_result" and data.existing_financial_analysis_result is None:
                missing.append(key)
        return missing

    def _missing_fields(
        self,
        intent_result: IntentResult,
        data: ContextPackageData,
        required_fields: list[str],
    ) -> list[str]:
        missing: list[str] = []
        for field_path in required_fields:
            if not self._field_present(field_path, intent_result, data):
                missing.append(field_path)
        return missing

    def _field_present(
        self,
        field_path: str,
        intent_result: IntentResult,
        data: ContextPackageData,
    ) -> bool:
        if field_path == "goal.amount":
            return intent_result.goal.amount is not None
        if field_path == "goal.deadline_months":
            return intent_result.goal.deadline_months is not None
        if field_path == "focus.category":
            return bool(intent_result.focus.category)

        user = data.user_context
        field_map = {
            "current_savings": user.current_savings,
            "stable_monthly_income": user.stable_monthly_income,
            "has_debt": user.has_debt,
            "monthly_debt_payment": user.monthly_debt_payment,
            "debt_amount": user.debt_amount,
        }
        if field_path in field_map:
            return field_map[field_path] is not None
        return True

    def _has_user_context(self, data: ContextPackageData) -> bool:
        user = data.user_context
        return any(
            value is not None
            for value in (
                user.current_savings,
                user.stable_monthly_income,
                user.has_debt,
                user.monthly_debt_payment,
                user.debt_amount,
                user.financial_goal,
                user.goal_amount,
                user.goal_deadline_months,
                user.salary_day,
                user.current_balance,
            )
        )
