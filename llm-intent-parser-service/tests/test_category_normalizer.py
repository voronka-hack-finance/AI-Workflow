"""Category normalization tests."""
from __future__ import annotations

from app.parser.category_normalizer import (
    detect_categories_in_text,
    normalize_category_value,
    normalize_focus_category,
)
from app.parser.validator import validate_intent_payload


def test_llm_category_kino_maps_to_canonical() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "requested_functions": ["category_analysis"],
            "focus": {"category": "кино", "direction": "expense"},
        }
    )
    assert result.focus.categories == ["Кино"]
    assert result.focus.category == "Кино"
    assert result.clarification.required is False


def test_llm_category_hotels_maps_to_canonical() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "requested_functions": ["category_analysis"],
            "focus": {"category": "отели", "direction": "expense"},
        }
    )
    assert result.focus.categories == ["Отели"]
    assert result.focus.category == "Отели"


def test_llm_combined_category_value_keeps_all_categories() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "requested_functions": ["category_analysis"],
            "focus": {"category": "Отели и Кино", "direction": "expense"},
        }
    )
    assert result.focus.categories == ["Отели", "Кино"]
    assert result.focus.category is None
    assert result.clarification.required is False


def test_llm_combined_products_and_pharmacy_keeps_all_categories() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "requested_functions": ["category_analysis"],
            "focus": {"category": "продукты и аптеки", "direction": "expense"},
        }
    )
    assert result.focus.categories == ["Супермаркеты", "Аптеки"]
    assert result.focus.category is None


def test_alias_normalization_for_fastfood() -> None:
    resolved = normalize_category_value("фастфуд")
    assert resolved.categories == ["Фастфуд"]


def test_canonical_multiword_category_is_preserved() -> None:
    resolved = normalize_category_value("Одежда и обувь")
    assert resolved.categories == ["Одежда и обувь"]


def test_detect_categories_in_text_finds_multiple() -> None:
    detected = detect_categories_in_text("сколько ушло на продукты и аптеки")
    assert detected == ["Супермаркеты", "Аптеки"]


def test_normalize_focus_category_keeps_requested_functions() -> None:
    payload = {
        "primary_intent": "category_analysis",
        "requested_functions": ["category_analysis", "budget_recommendation"],
        "focus": {"category": "Отели и Кино", "direction": "expense"},
    }
    normalize_focus_category(payload)
    assert payload["focus"]["categories"] == ["Отели", "Кино"]
    assert payload["focus"]["category"] is None
    assert payload["requested_functions"] == ["category_analysis", "budget_recommendation"]


def test_llm_categories_array_is_merged() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "requested_functions": ["category_analysis"],
            "focus": {
                "categories": ["отели", "кино"],
                "direction": "expense",
            },
        }
    )
    assert result.focus.categories == ["Отели", "Кино"]
    assert result.focus.category is None


def test_unknown_llm_category_requests_clarification() -> None:
    result = validate_intent_payload(
        {
            "primary_intent": "category_analysis",
            "requested_functions": ["category_analysis"],
            "focus": {"category": "неизвестная категория", "direction": "expense"},
        }
    )
    assert result.focus.categories == []
    assert result.focus.category is None
    assert result.clarification.required is True
    assert "focus.categories" in result.clarification.missing_fields
