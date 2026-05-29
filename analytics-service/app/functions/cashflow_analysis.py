"""CashflowAnalysis function."""
from app.functions.base import BaseAnalyticsFunction


class CashflowAnalysis(BaseAnalyticsFunction):
    name = "cashflow_analysis"

    async def run(self, context: dict) -> dict:
        # TODO: implement
        return {}
