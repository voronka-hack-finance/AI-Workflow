"""HTTP client for downstream service."""
from app.core.config import get_settings


class IntentParserClient:
    def __init__(self) -> None:
        self._settings = get_settings()

    async def call(self, payload: dict) -> dict:
        # TODO: implement HTTP call with shared_http
        return {}
