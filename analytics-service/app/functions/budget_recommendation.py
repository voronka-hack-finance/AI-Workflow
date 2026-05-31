"""BudgetRecommendation function."""
from __future__ import annotations

from shared_contracts.common import RiskLevel

from app.builders.function_result_builder import FunctionResultBuilder
from app.functions.base import BaseAnalyticsFunction
from app.rules import problem_tags, priority_score, recommendation_type, risk_score
from app.runner.function_context import FunctionContext


class BudgetRecommendation(BaseAnalyticsFunction):
    name = "budget_recommendation"

    def __init__(self) -> None:
        self._builder = FunctionResultBuilder()

    def run(self, ctx: FunctionContext):
        cashflow = ctx.prior_result_data("cashflow_analysis")
        expense = ctx.prior_result_data("expense_breakdown")
        emergency = ctx.prior_result_data("emergency_fund_analysis")
        debt = ctx.prior_result_data("debt_analysis")
        leaks = ctx.prior_result_data("spending_leak_detection")
        profiles = {
            p.category: p
            for p in ctx.package.data.category_profiles
        }

        if not cashflow and not expense:
            return self._builder.needs_clarification(
                self.name,
                warnings=["Insufficient prior results for budget recommendation."],
            )

        expenses_ratio = cashflow.get("expenses_to_income_ratio")
        emergency_months = emergency.get("months_covered")
        has_debt = bool(debt.get("has_debt", False))
        leak_count = int(leaks.get("leaks_detected", 0))

        score = risk_score.calculate_risk_score(
            expenses_to_income_ratio=expenses_ratio,
            emergency_months=emergency_months,
            has_debt=has_debt,
            spending_leak_count=leak_count,
        )
        tags = problem_tags.derive_problem_tags(
            expenses_to_income_ratio=expenses_ratio,
            emergency_months=emergency_months,
            has_debt=has_debt,
            spending_leak_count=leak_count,
        )

        expected_savings, categories = self._estimate_savings(expense, leaks, profiles)
        main_problem = tags[0] if tags else "balanced_spending"
        risk_level = _score_to_risk_level(score)

        return self._builder.success(
            self.name,
            {
                "risk_score": round(score, 2),
                "risk_level": risk_level,
                "main_problem": main_problem,
                "problem_tags": tags,
                "recommendation_type": recommendation_type.select_recommendation_type(tags),
                "category_to_optimize": categories,
                "expected_savings": round(expected_savings, 2),
                "priority": priority_score.risk_to_priority(score),
            },
            warnings=None if expected_savings > 0 else ["No optimizable savings identified."],
        )

    def _estimate_savings(self, expense: dict, leaks: dict, profiles: dict) -> tuple[float, list[str]]:
        leak_items = leaks.get("leaks", [])
        if leak_items:
            total = 0.0
            cats: list[str] = []
            for leak in leak_items:
                if not isinstance(leak, dict):
                    continue
                cat = leak.get("category")
                if cat and profiles.get(cat) and profiles[cat].protected_by_default:
                    continue
                amount = float(leak.get("amount", 0))
                savings = amount * 0.2
                total += savings
                if cat:
                    cats.append(cat)
            return total, cats[:3]

        breakdown = expense.get("category_breakdown", [])
        total = 0.0
        cats: list[str] = []
        for item in breakdown[:3]:
            if not isinstance(item, dict):
                continue
            cat = item.get("category")
            if cat and profiles.get(cat) and profiles[cat].protected_by_default:
                continue
            amount = float(item.get("amount", 0))
            if amount > 0 and (not profiles.get(cat) or profiles[cat].can_optimize):
                total += amount * 0.1
                if cat:
                    cats.append(cat)
        return total, cats


def _score_to_risk_level(score: float) -> str:
    if score >= 70:
        return RiskLevel.CRITICAL
    if score >= 50:
        return RiskLevel.HIGH
    if score >= 30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW
