"""FinancialAnalysisResult builder."""
from __future__ import annotations

from shared_contracts.common import WarningItem
from shared_contracts.context_package import ContextPackage
from shared_contracts.financial_analysis_result import (
    FinancialAnalysisMetadata,
    FinancialAnalysisResult,
    FunctionResult,
)
from shared_contracts.intent_result import PeriodInput

from app.builders.analysis_result_builder import AnalysisResultBuilder
from app.core.config import get_settings
from app.helpers.dates import utc_now_iso


class FinancialAnalysisResultBuilder:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._analysis_builder = AnalysisResultBuilder()

    def build(
        self,
        package: ContextPackage,
        *,
        executed_functions: list[str],
        function_results: dict[str, FunctionResult],
        extra_warnings: list[str] | None = None,
    ) -> FinancialAnalysisResult:
        period = PeriodInput(
            type=package.context_builder.resolved_period.type,
            start_date=package.context_builder.resolved_period.start_date,
            end_date=package.context_builder.resolved_period.end_date,
        )
        warnings = self._collect_warnings(package, function_results, extra_warnings)
        return FinancialAnalysisResult(
            request_id=package.request_id,
            user_id=package.user_id,
            period=period,
            executed_functions=executed_functions,
            function_results=function_results,
            analysis_result=self._analysis_builder.build(function_results),
            warnings=warnings,
            metadata=FinancialAnalysisMetadata(
                rules_version=self._settings.rules_version,
                calculated_at=utc_now_iso(),
            ),
        )

    def build_blocked(self, package: ContextPackage) -> FinancialAnalysisResult:
        warnings = [
            "Analytics cannot run: required data is missing.",
            *[
                f"Missing: {item}"
                for item in package.data_quality.missing_hard_required_data
            ],
        ]
        return FinancialAnalysisResult(
            request_id=package.request_id,
            user_id=package.user_id,
            period=PeriodInput(
                type=package.context_builder.resolved_period.type,
                start_date=package.context_builder.resolved_period.start_date,
                end_date=package.context_builder.resolved_period.end_date,
            ),
            executed_functions=[],
            function_results={},
            analysis_result=self._analysis_builder.build({}),
            warnings=warnings,
            metadata=FinancialAnalysisMetadata(
                rules_version=self._settings.rules_version,
                calculated_at=utc_now_iso(),
            ),
        )

    def _collect_warnings(
        self,
        package: ContextPackage,
        function_results: dict[str, FunctionResult],
        extra_warnings: list[str] | None,
    ) -> list[str | WarningItem]:
        warnings: list[str | WarningItem] = list(extra_warnings or [])
        warnings.extend(package.data_quality.normalization_warnings)
        if package.data_quality.calculation_mode == "partial":
            warnings.append("Calculation mode is partial; some metrics may be limited.")
        for fn_result in function_results.values():
            warnings.extend(fn_result.warnings)
        return warnings
