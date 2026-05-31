"""Registry mapping function names to implementations."""
from __future__ import annotations

from shared_contracts.common import MVP_ANALYTICS_FUNCTIONS

from app.functions.action_plan import ActionPlan
from app.functions.base import BaseAnalyticsFunction
from app.functions.budget_plan import BudgetPlan
from app.functions.budget_recommendation import BudgetRecommendation
from app.functions.cashflow_analysis import CashflowAnalysis
from app.functions.category_analysis import CategoryAnalysis
from app.functions.debt_analysis import DebtAnalysis
from app.functions.emergency_fund_analysis import EmergencyFundAnalysis
from app.functions.expense_breakdown import ExpenseBreakdown
from app.functions.goal_analysis import GoalAnalysis
from app.functions.income_analysis import IncomeAnalysis
from app.functions.period_analysis import PeriodAnalysis
from app.functions.spending_leak_detection import SpendingLeakDetection
from app.functions.transfer_analysis import TransferAnalysis


class FunctionRegistry:
    def __init__(self) -> None:
        self._functions: dict[str, BaseAnalyticsFunction] = {}
        for cls in (
            PeriodAnalysis,
            ExpenseBreakdown,
            IncomeAnalysis,
            CashflowAnalysis,
            CategoryAnalysis,
            TransferAnalysis,
            SpendingLeakDetection,
            EmergencyFundAnalysis,
            DebtAnalysis,
            BudgetRecommendation,
            GoalAnalysis,
            BudgetPlan,
            ActionPlan,
        ):
            instance = cls()
            self._functions[instance.name] = instance

    def is_known(self, function_name: str) -> bool:
        return function_name in MVP_ANALYTICS_FUNCTIONS

    def get(self, function_name: str) -> BaseAnalyticsFunction | None:
        if not self.is_known(function_name):
            return None
        return self._functions.get(function_name)
