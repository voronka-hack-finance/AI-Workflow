"""Map backend category profile DTO to CategoryProfile."""
from __future__ import annotations

from shared_contracts.normalized_data import CategoryGroup, CategoryProfile

from app.data_adapters.warnings import NormalizationWarnings
from app.schemas.backend_dto import BackendCategoryProfile

DEFAULT_CATEGORY_GROUPS: dict[str, str] = {
    "Фастфуд": CategoryGroup.FOOD_OUTSIDE,
    "Рестораны": CategoryGroup.FOOD_OUTSIDE,
    "Продукты": CategoryGroup.ESSENTIAL_VARIABLE,
    "ЖКХ": CategoryGroup.ESSENTIAL_FIXED,
    "Медицина": CategoryGroup.HEALTH,
    "Транспорт": CategoryGroup.TRANSPORT,
}


class CategoryMapper:
    def map_many(
        self,
        items: list[BackendCategoryProfile],
        warnings: NormalizationWarnings | None = None,
    ) -> list[CategoryProfile]:
        collector = warnings or NormalizationWarnings()
        return [self.map_one(item, collector) for item in items]

    def map_one(
        self,
        item: BackendCategoryProfile,
        warnings: NormalizationWarnings | None = None,
    ) -> CategoryProfile:
        collector = warnings or NormalizationWarnings()
        group = item.categoryGroup or DEFAULT_CATEGORY_GROUPS.get(item.category)
        if group is None:
            collector.add_unmapped_category(item.category)
            group = CategoryGroup.UNKNOWN
        return CategoryProfile(
            category=item.category,
            category_group=group,
            can_optimize=item.canOptimize,
            protected_by_default=item.protectedByDefault,
            is_required_expense=item.isRequiredExpense,
        )
