"""Map backend user context DTO to UserFinancialContextNormalized."""
from __future__ import annotations

from shared_contracts.normalized_data import UserFinancialContextNormalized

from app.schemas.backend_dto import BackendUserContext


class UserContextMapper:
    def map_one(self, item: BackendUserContext | None) -> UserFinancialContextNormalized:
        if item is None:
            return UserFinancialContextNormalized()
        return UserFinancialContextNormalized(
            current_savings=item.currentSavings,
            stable_monthly_income=item.stableMonthlyIncome,
            has_debt=item.hasDebt,
            monthly_debt_payment=item.monthlyDebtPayment,
            debt_amount=item.debtAmount,
            financial_goal=item.financialGoal,
            goal_amount=item.goalAmount,
            goal_deadline_months=item.goalDeadlineMonths,
            salary_day=item.salaryDay,
            current_balance=item.currentBalance,
        )
