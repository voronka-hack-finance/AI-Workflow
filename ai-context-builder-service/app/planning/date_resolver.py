"""Resolve relative periods and comparison dates."""
from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

from shared_contracts.common import ComparisonType, PeriodType
from shared_contracts.context_package import ResolvedComparison, ResolvedPeriod
from shared_contracts.intent_result import ComparisonInput, IntentResult, PeriodInput

_RELATIVE_PERIOD_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^(?:last|past)_(\d+)_days?$"), "days"),
    (re.compile(r"^(?:last|past)_(\d+)_weeks?$"), "weeks"),
    (re.compile(r"^(?:last|past)_(\d+)_months?$"), "months"),
    (re.compile(r"^(?:last|past)_(\d+)_years?$"), "years"),
)


class DateResolver:
    def resolve_period(
        self,
        period: PeriodInput,
        *,
        current_date: str,
        timezone: str,
    ) -> ResolvedPeriod:
        if period.start_date and period.end_date:
            return ResolvedPeriod(
                type=period.type,
                start_date=self._normalize_date(period.start_date),
                end_date=self._normalize_date(period.end_date),
                source="DateResolver",
            )

        anchor = self._parse_date(current_date, timezone)
        start, end = self._resolve_range(period.type, anchor)

        return ResolvedPeriod(
            type=period.type,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            source="DateResolver",
        )

    def resolve_comparison(
        self,
        comparison: ComparisonInput,
        *,
        current_date: str,
        timezone: str,
        resolved_period: ResolvedPeriod,
    ) -> ResolvedComparison:
        if not comparison.enabled:
            return ResolvedComparison(
                enabled=False,
                type=None,
                start_date=None,
                end_date=None,
                source="DateResolver",
            )

        if comparison.start_date and comparison.end_date:
            return ResolvedComparison(
                enabled=True,
                type=comparison.type,
                start_date=self._normalize_date(comparison.start_date),
                end_date=self._normalize_date(comparison.end_date),
                source="DateResolver",
            )

        period_start = self._parse_date(resolved_period.start_date or current_date, timezone)
        period_end = self._parse_date(resolved_period.end_date or current_date, timezone)
        comp_type = comparison.type or ComparisonType.PREVIOUS_PERIOD

        if comp_type == ComparisonType.PREVIOUS_MONTH:
            start, end = self._previous_month(period_start)
        elif comp_type == ComparisonType.PREVIOUS_WEEK:
            start, end = self._previous_week(period_start, period_end)
        else:
            delta = period_end - period_start
            start = period_start - delta - timedelta(days=1)
            end = period_start - timedelta(days=1)

        return ResolvedComparison(
            enabled=True,
            type=comp_type,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            source="DateResolver",
        )

    def resolve_from_intent(
        self,
        intent_result: IntentResult,
        *,
        current_date: str,
        timezone: str,
    ) -> tuple[ResolvedPeriod, ResolvedComparison]:
        resolved_period = self.resolve_period(
            intent_result.period,
            current_date=current_date,
            timezone=timezone,
        )
        resolved_comparison = self.resolve_comparison(
            intent_result.comparison,
            current_date=current_date,
            timezone=timezone,
            resolved_period=resolved_period,
        )
        return resolved_period, resolved_comparison

    def _normalize_date(self, value: str) -> str:
        return value[:10]

    def _parse_date(self, value: str, timezone: str) -> date:
        del timezone
        return date.fromisoformat(value[:10])

    def _resolve_range(self, period_type: PeriodType | str, anchor: date) -> tuple[date, date]:
        if period_type == PeriodType.TODAY:
            return anchor, anchor
        if period_type == PeriodType.YESTERDAY:
            yesterday = anchor - timedelta(days=1)
            return yesterday, yesterday
        if period_type == PeriodType.LAST_7_DAYS:
            return anchor - timedelta(days=6), anchor
        if period_type == PeriodType.LAST_30_DAYS:
            return anchor - timedelta(days=29), anchor
        if period_type == PeriodType.CURRENT_WEEK:
            start = anchor - timedelta(days=anchor.weekday())
            return start, anchor
        if period_type == PeriodType.PREVIOUS_MONTH:
            return self._previous_month(anchor)
        if period_type == PeriodType.CURRENT_MONTH:
            last_day = calendar.monthrange(anchor.year, anchor.month)[1]
            return date(anchor.year, anchor.month, 1), date(anchor.year, anchor.month, last_day)

        relative = self._parse_relative_period(period_type)
        if relative is not None:
            unit, count = relative
            return self._relative_range(anchor, unit, count)

        if period_type == PeriodType.UNKNOWN:
            last_day = calendar.monthrange(anchor.year, anchor.month)[1]
            return date(anchor.year, anchor.month, 1), date(anchor.year, anchor.month, last_day)

        last_day = calendar.monthrange(anchor.year, anchor.month)[1]
        return date(anchor.year, anchor.month, 1), date(anchor.year, anchor.month, last_day)

    def _parse_relative_period(self, period_type: PeriodType | str) -> tuple[str, int] | None:
        normalized = str(period_type).strip().lower().replace("-", "_")
        for pattern, unit in _RELATIVE_PERIOD_PATTERNS:
            match = pattern.match(normalized)
            if match is None:
                continue
            count = int(match.group(1))
            if count < 1:
                return None
            return unit, count
        return None

    def _relative_range(self, anchor: date, unit: str, count: int) -> tuple[date, date]:
        if unit == "days":
            return anchor - timedelta(days=count - 1), anchor
        if unit == "weeks":
            return anchor - timedelta(days=count * 7 - 1), anchor
        if unit == "months":
            return self._last_n_calendar_months(anchor, count)
        if unit == "years":
            start_year = anchor.year - (count - 1)
            return date(start_year, 1, 1), anchor
        raise ValueError(f"Unsupported relative period unit: {unit}")

    def _previous_month(self, anchor: date) -> tuple[date, date]:
        if anchor.month == 1:
            year, month = anchor.year - 1, 12
        else:
            year, month = anchor.year, anchor.month - 1
        last_day = calendar.monthrange(year, month)[1]
        return date(year, month, 1), date(year, month, last_day)

    def _previous_week(self, period_start: date, period_end: date) -> tuple[date, date]:
        delta = period_end - period_start
        comp_end = period_start - timedelta(days=1)
        comp_start = comp_end - delta
        return comp_start, comp_end

    def _last_n_calendar_months(self, anchor: date, months: int) -> tuple[date, date]:
        """Inclusive window of N calendar months ending on anchor (current month included)."""
        month_index = anchor.year * 12 + anchor.month - 1 - (months - 1)
        year, month = divmod(month_index, 12)
        start = date(year, month + 1, 1)
        return start, anchor
