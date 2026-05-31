"""Normalize focus categories to canonical values from LLM output only."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

CANONICAL_CATEGORIES: tuple[str, ...] = (
    "Автоуслуги",
    "Аптеки",
    "Госуслуги",
    "Другое",
    "Ж/д билеты",
    "Животные",
    "ЖКХ",
    "Заправки",
    "Искусство",
    "Канцтовары",
    "Кино",
    "Книги и канцтовары",
    "Красота",
    "Маркетплейсы",
    "Медицина",
    "Местный транспорт",
    "Мобильная связь",
    "Наличные",
    "Образование",
    "Одежда и обувь",
    "Отели",
    "Переводы",
    "Развлечения",
    "Различные товары",
    "Различные услуги",
    "Ремонт и мебель",
    "Рестораны",
    "Связь",
    "Сервис",
    "Спорттовары",
    "Супермаркеты",
    "Такси",
    "Транспорт",
    "Тренировки",
    "Услуги банка",
    "Фастфуд",
    "Финансы",
    "Фото и копицентры",
    "Цветы",
    "Цифровые товары",
    "Штрафы",
    "Экосистема Яндекс",
)

CANONICAL_CATEGORY_SET = set(CANONICAL_CATEGORIES)
CANONICAL_BY_LOWER = {category.lower(): category for category in CANONICAL_CATEGORIES}

CATEGORY_ALIASES: dict[str, str] = {
    "фастфуд": "Фастфуд",
    "кино": "Кино",
    "отели": "Отели",
    "отель": "Отели",
    "гостиницы": "Отели",
    "гостиница": "Отели",
    "такси": "Такси",
    "продукты": "Супермаркеты",
    "супермаркеты": "Супермаркеты",
    "супермаркет": "Супермаркеты",
    "аптека": "Аптеки",
    "аптеки": "Аптеки",
    "медицина": "Медицина",
    "врач": "Медицина",
    "клиника": "Медицина",
    "маркетплейсы": "Маркетплейсы",
    "ozon": "Маркетплейсы",
    "озон": "Маркетплейсы",
    "wildberries": "Маркетплейсы",
    "wb": "Маркетплейсы",
    "одежда": "Одежда и обувь",
    "обувь": "Одежда и обувь",
    "коммуналка": "ЖКХ",
    "жкх": "ЖКХ",
}

CATEGORY_CLARIFICATION_QUESTION = "Уточни, пожалуйста, категории расходов."


@dataclass(frozen=True)
class CategoryResolveResult:
    categories: list[str] = field(default_factory=list)
    needs_clarification: bool = False
    question: str | None = None


def _strip_category_prefix(value: str) -> str:
    stripped = value.strip()
    lowered = stripped.lower()
    for prefix in ("на ", "по ", "в "):
        if lowered.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return stripped


def _ranges_overlap(start: int, end: int, used_ranges: list[tuple[int, int]]) -> bool:
    return any(not (end <= used_start or start >= used_end) for used_start, used_end in used_ranges)


def detect_categories_in_text(text: str) -> list[str]:
    lowered = text.lower()
    patterns: list[tuple[str, str]] = [
        (category.lower(), category) for category in CANONICAL_CATEGORIES
    ]
    patterns.extend(CATEGORY_ALIASES.items())
    patterns.sort(key=lambda item: len(item[0]), reverse=True)

    found: list[tuple[int, str]] = []
    used_ranges: list[tuple[int, int]] = []
    for pattern, category in patterns:
        start = 0
        while True:
            idx = lowered.find(pattern, start)
            if idx == -1:
                break
            end = idx + len(pattern)
            if not _ranges_overlap(idx, end, used_ranges):
                found.append((idx, category))
                used_ranges.append((idx, end))
            start = idx + 1

    ordered: list[str] = []
    seen: set[str] = set()
    for _, category in sorted(found, key=lambda item: item[0]):
        if category in seen:
            continue
        seen.add(category)
        ordered.append(category)
    return ordered


def _resolve_alias(value: str) -> str | None:
    canonical = CANONICAL_BY_LOWER.get(value.lower())
    if canonical is not None:
        return canonical
    return CATEGORY_ALIASES.get(value.lower())


def _append_unique(categories: list[str], category: str) -> None:
    if category not in categories:
        categories.append(category)


def normalize_category_value(value: str) -> CategoryResolveResult:
    """Map one LLM-provided category string to canonical categories."""
    cleaned = _strip_category_prefix(value)
    if not cleaned:
        return CategoryResolveResult()

    if cleaned in CANONICAL_CATEGORY_SET:
        return CategoryResolveResult(categories=[cleaned])

    alias_match = _resolve_alias(cleaned)
    if alias_match is not None:
        return CategoryResolveResult(categories=[alias_match])

    detected_in_value = detect_categories_in_text(cleaned)
    if detected_in_value:
        return CategoryResolveResult(categories=detected_in_value)

    if " и " in cleaned.lower():
        parts = [part.strip() for part in cleaned.split(" и ") if part.strip()]
        resolved_parts: list[str] = []
        for part in parts:
            resolved = normalize_category_value(part)
            for category in resolved.categories:
                _append_unique(resolved_parts, category)
        if resolved_parts:
            return CategoryResolveResult(categories=resolved_parts)

    return CategoryResolveResult(
        needs_clarification=True,
        question=CATEGORY_CLARIFICATION_QUESTION,
    )


def normalize_category_values(values: list[str]) -> CategoryResolveResult:
    merged: list[str] = []
    for value in values:
        resolved = normalize_category_value(value)
        if resolved.needs_clarification and not resolved.categories:
            return resolved
        for category in resolved.categories:
            _append_unique(merged, category)
    if merged:
        return CategoryResolveResult(categories=merged)
    return CategoryResolveResult(
        needs_clarification=True,
        question=CATEGORY_CLARIFICATION_QUESTION,
    )


def _sync_focus_category_fields(focus: dict[str, Any], categories: list[str]) -> None:
    focus["categories"] = categories
    focus["category"] = categories[0] if len(categories) == 1 else None
    focus["direction"] = focus.get("direction") or "expense"


def _collect_raw_category_values(focus: dict[str, Any]) -> list[str]:
    values: list[str] = []
    categories = focus.get("categories")
    if isinstance(categories, list):
        values.extend(item.strip() for item in categories if isinstance(item, str) and item.strip())
    category = focus.get("category")
    if isinstance(category, str) and category.strip():
        values.append(category.strip())
    return values


def normalize_focus_category(payload: dict[str, Any]) -> None:
    """Normalize focus.categories from LLM output only. Does not scan raw_message."""
    focus = payload.get("focus")
    if not isinstance(focus, dict):
        return

    raw_values = _collect_raw_category_values(focus)
    if not raw_values:
        return

    resolved = normalize_category_values(raw_values)
    if resolved.categories:
        _sync_focus_category_fields(focus, resolved.categories)
        return

    if resolved.needs_clarification:
        focus["category"] = None
        focus["categories"] = []
