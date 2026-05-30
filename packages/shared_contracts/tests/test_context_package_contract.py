"""Context package contract tests."""
import pytest
from pydantic import ValidationError

from shared_contracts.context_package import ContextPackage, ContextPackageData
from conftest import minimal_context_package


def test_context_package_can_be_created() -> None:
    package = minimal_context_package()
    assert package.package_type == "analytics_context_package"
    assert package.context_builder.expanded_functions == [
        "income_analysis",
        "budget_recommendation",
    ]


def test_context_package_category_profiles_is_array() -> None:
    package = minimal_context_package()
    assert isinstance(package.data.category_profiles, list)
    assert len(package.data.category_profiles) == 1


def test_context_package_rejects_missing_data() -> None:
    payload = minimal_context_package().model_dump()
    payload["missing_data"] = {"transactions": True}
    with pytest.raises(ValidationError):
        ContextPackage(**payload)


def test_context_package_rejects_root_expanded_functions() -> None:
    payload = minimal_context_package().model_dump()
    payload["expanded_functions"] = ["income_analysis"]
    with pytest.raises(ValidationError):
        ContextPackage(**payload)


def test_context_package_rejects_category_profiles_object() -> None:
    with pytest.raises(ValidationError):
        ContextPackageData(category_profiles={"Фастфуд": {"category_group": "food_outside"}})  # type: ignore[arg-type]
