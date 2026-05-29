"""ExpenseBreakdown function."""
from app.functions.base import BaseAnalyticsFunction


class ExpenseBreakdown(BaseAnalyticsFunction):
    name = "expense_breakdown"

    async def run(self, context: dict) -> dict:
        # TODO: implement
        return {}
