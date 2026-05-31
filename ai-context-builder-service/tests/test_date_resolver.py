"""Date resolver tests."""
from shared_contracts.common import ComparisonType, PeriodType
from shared_contracts.intent_result import ComparisonInput, IntentResult, PeriodInput

from app.planning.date_resolver import DateResolver


def test_resolve_current_month() -> None:
    resolver = DateResolver()
    period = PeriodInput(type=PeriodType.CURRENT_MONTH)
    resolved = resolver.resolve_period(
        period,
        current_date="2026-05-29",
        timezone="Europe/Moscow",
    )
    assert resolved.start_date == "2026-05-01"
    assert resolved.end_date == "2026-05-31"
    assert resolved.source == "DateResolver"


def test_resolve_comparison_disabled() -> None:
    resolver = DateResolver()
    comparison = ComparisonInput(enabled=False)
    resolved_period = resolver.resolve_period(
        PeriodInput(type=PeriodType.CURRENT_MONTH),
        current_date="2026-05-29",
        timezone="Europe/Moscow",
    )
    resolved = resolver.resolve_comparison(
        comparison,
        current_date="2026-05-29",
        timezone="Europe/Moscow",
        resolved_period=resolved_period,
    )
    assert resolved.enabled is False
    assert resolved.start_date is None
    assert resolved.end_date is None


def test_resolve_last_6_months() -> None:
    resolver = DateResolver()
    resolved = resolver.resolve_period(
        PeriodInput(type="last_6_months"),
        current_date="2026-05-30",
        timezone="Europe/Moscow",
    )
    assert resolved.start_date == "2025-12-01"
    assert resolved.end_date == "2026-05-30"


def test_resolve_last_6_months_string_from_llm() -> None:
    resolver = DateResolver()
    resolved = resolver.resolve_period(
        PeriodInput(type="last_6_months"),
        current_date="2026-05-30",
        timezone="Europe/Moscow",
    )
    assert resolved.start_date == "2025-12-01"
    assert resolved.end_date == "2026-05-30"


def test_resolve_last_7_months() -> None:
    resolver = DateResolver()
    resolved = resolver.resolve_period(
        PeriodInput(type="last_7_months"),
        current_date="2026-05-30",
        timezone="Europe/Moscow",
    )
    assert resolved.start_date == "2025-11-01"
    assert resolved.end_date == "2026-05-30"


def test_resolve_last_14_days() -> None:
    resolver = DateResolver()
    resolved = resolver.resolve_period(
        PeriodInput(type="last_14_days"),
        current_date="2026-05-30",
        timezone="Europe/Moscow",
    )
    assert resolved.start_date == "2026-05-17"
    assert resolved.end_date == "2026-05-30"


def test_resolve_last_3_weeks() -> None:
    resolver = DateResolver()
    resolved = resolver.resolve_period(
        PeriodInput(type="past_3_weeks"),
        current_date="2026-05-30",
        timezone="Europe/Moscow",
    )
    assert resolved.start_date == "2026-05-10"
    assert resolved.end_date == "2026-05-30"


def test_resolve_last_2_years() -> None:
    resolver = DateResolver()
    resolved = resolver.resolve_period(
        PeriodInput(type="last_2_years"),
        current_date="2026-05-30",
        timezone="Europe/Moscow",
    )
    assert resolved.start_date == "2025-01-01"
    assert resolved.end_date == "2026-05-30"


def test_resolve_explicit_dates_any_type() -> None:
    resolver = DateResolver()
    resolved = resolver.resolve_period(
        PeriodInput(
            type="last_7_months",
            start_date="2025-11-01T00:00:00Z",
            end_date="2026-05-30T00:00:00Z",
        ),
        current_date="2026-05-30",
        timezone="Europe/Moscow",
    )
    assert resolved.start_date == "2025-11-01"
    assert resolved.end_date == "2026-05-30"


def test_resolve_last_6_months_with_comparison() -> None:
    resolver = DateResolver()
    intent = IntentResult(
        period=PeriodInput(type="last_6_months"),
        comparison=ComparisonInput(enabled=True, type=ComparisonType.PREVIOUS_PERIOD),
    )
    resolved_period, resolved_comparison = resolver.resolve_from_intent(
        intent,
        current_date="2026-05-30",
        timezone="Europe/Moscow",
    )
    assert resolved_period.start_date == "2025-12-01"
    assert resolved_period.end_date == "2026-05-30"
    assert resolved_comparison.enabled is True
    assert resolved_comparison.end_date == "2025-11-30"
    assert resolved_comparison.start_date == "2025-06-03"


def test_resolve_comparison_enabled() -> None:
    resolver = DateResolver()
    intent = IntentResult(
        period=PeriodInput(type=PeriodType.CURRENT_MONTH),
        comparison=ComparisonInput(enabled=True),
    )
    resolved_period, resolved_comparison = resolver.resolve_from_intent(
        intent,
        current_date="2026-05-29",
        timezone="Europe/Moscow",
    )
    assert resolved_period.start_date == "2026-05-01"
    assert resolved_comparison.enabled is True
    assert resolved_comparison.start_date is not None
    assert resolved_comparison.end_date is not None
