"""SpendingLeakDetection function."""
from app.functions.base import BaseAnalyticsFunction


class SpendingLeakDetection(BaseAnalyticsFunction):
    name = "spending_leak_detection"

    async def run(self, context: dict) -> dict:
        # TODO: implement
        return {}
