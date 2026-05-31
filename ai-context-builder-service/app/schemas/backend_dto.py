"""Internal backend DTO schemas (not shared contracts)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class BackendTransaction(BaseModel):
    id: str
    sum: float
    currency: str
    type: str
    merchantName: str | None = None
    bankCategory: str | None = None
    mccCode: str | None = None
    date: str
    ambiguous: bool = False


class BackendUserContext(BaseModel):
    currentSavings: float | None = None
    stableMonthlyIncome: float | None = None
    hasDebt: bool | None = None
    monthlyDebtPayment: float | None = None
    debtAmount: float | None = None
    financialGoal: str | None = None
    goalAmount: float | None = None
    goalDeadlineMonths: int | None = None
    salaryDay: int | None = None
    currentBalance: float | None = None


class BackendCategoryProfile(BaseModel):
    category: str
    categoryGroup: str | None = None
    canOptimize: bool = True
    protectedByDefault: bool = False
    isRequiredExpense: bool = False


class BackendTransactionsResponse(BaseModel):
    items: list[BackendTransaction] = Field(default_factory=list)
