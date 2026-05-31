"""FunctionResult builder."""
from __future__ import annotations

from shared_contracts.common import FunctionResultStatus, JsonDict
from shared_contracts.financial_analysis_result import FunctionResult, FunctionResultMetadata

from app.core.config import get_settings
from app.helpers.dates import utc_now_iso


class FunctionResultBuilder:
    def __init__(self) -> None:
        self._settings = get_settings()

    def build(
        self,
        function_name: str,
        status: FunctionResultStatus | str,
        *,
        result: JsonDict | None = None,
        input_used: JsonDict | None = None,
        warnings: list[str] | None = None,
    ) -> FunctionResult:
        return FunctionResult(
            function_name=function_name,
            status=status,
            input_used=input_used or {},
            result=result or {},
            warnings=warnings or [],
            metadata=FunctionResultMetadata(
                rules_version=self._settings.rules_version,
                calculated_at=utc_now_iso(),
            ),
        )

    def success(
        self,
        function_name: str,
        result: JsonDict,
        *,
        input_used: JsonDict | None = None,
        warnings: list[str] | None = None,
    ) -> FunctionResult:
        return self.build(
            function_name,
            FunctionResultStatus.SUCCESS,
            result=result,
            input_used=input_used,
            warnings=warnings,
        )

    def empty(
        self,
        function_name: str,
        *,
        input_used: JsonDict | None = None,
        warnings: list[str] | None = None,
    ) -> FunctionResult:
        return self.build(
            function_name,
            FunctionResultStatus.EMPTY_RESULT,
            input_used=input_used,
            warnings=warnings,
        )

    def needs_clarification(
        self,
        function_name: str,
        *,
        result: JsonDict | None = None,
        input_used: JsonDict | None = None,
        warnings: list[str] | None = None,
    ) -> FunctionResult:
        return self.build(
            function_name,
            FunctionResultStatus.NEEDS_CLARIFICATION,
            result=result,
            input_used=input_used,
            warnings=warnings,
        )

    def error(
        self,
        function_name: str,
        *,
        warnings: list[str] | None = None,
    ) -> FunctionResult:
        return self.build(
            function_name,
            FunctionResultStatus.ERROR,
            warnings=warnings,
        )
