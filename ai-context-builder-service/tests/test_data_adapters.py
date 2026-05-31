"""Data adapter tests."""
from app.data_adapters.category_mapper import CategoryMapper
from app.data_adapters.transaction_mapper import TransactionMapper
from app.data_adapters.user_context_mapper import UserContextMapper
from app.data_adapters.warnings import NormalizationWarnings
from app.schemas.backend_dto import BackendCategoryProfile, BackendTransaction, BackendUserContext


def test_transaction_mapper_maps_backend_dto() -> None:
    mapper = TransactionMapper()
    item = BackendTransaction(
        id="tx_1",
        sum=-1294,
        currency="RUB",
        type="OUT",
        merchantName="Вкусно — и точка",
        bankCategory="Фастфуд",
        mccCode="5814",
        date="2026-05-10T18:25:00",
    )
    result = mapper.map_one(item)
    assert result.transaction_id == "tx_1"
    assert result.direction == "expense"
    assert result.category == "Фастфуд"


def test_transaction_mapper_records_unmapped_and_ambiguous() -> None:
    mapper = TransactionMapper()
    warnings = NormalizationWarnings()
    item = BackendTransaction(
        id="tx_amb",
        sum=-500,
        currency="RUB",
        type="OUT",
        bankCategory="Неизвестная категория",
        date="2026-05-11T12:00:00",
        ambiguous=True,
    )
    mapper.map_one(item, warnings)
    assert "tx_amb" in warnings.ambiguous_transactions
    assert "Неизвестная категория" in warnings.unmapped_categories


def test_user_context_mapper() -> None:
    mapper = UserContextMapper()
    result = mapper.map_one(
        BackendUserContext(currentSavings=45000, stableMonthlyIncome=85000)
    )
    assert result.current_savings == 45000
    assert result.stable_monthly_income == 85000


def test_category_mapper_unknown_group() -> None:
    mapper = CategoryMapper()
    warnings = NormalizationWarnings()
    result = mapper.map_one(
        BackendCategoryProfile(category="Неизвестная категория"),
        warnings,
    )
    assert result.category_group == "unknown"
    assert "Неизвестная категория" in warnings.unmapped_categories
