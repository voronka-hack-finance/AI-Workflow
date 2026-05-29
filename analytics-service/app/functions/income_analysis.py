"""IncomeAnalysis function."""
from app.functions.base import BaseAnalyticsFunction


class IncomeAnalysis(BaseAnalyticsFunction):
    name = "income_analysis"

    async def run(self, context: dict) -> dict:
        # TODO: implement
        return {}
