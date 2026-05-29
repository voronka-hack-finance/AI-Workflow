"""BudgetRecommendation function."""
from app.functions.base import BaseAnalyticsFunction


class BudgetRecommendation(BaseAnalyticsFunction):
    name = "budget_recommendation"

    async def run(self, context: dict) -> dict:
        # TODO: implement
        return {}
