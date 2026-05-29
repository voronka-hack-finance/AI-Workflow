"""HTTP client wrapper."""
import httpx


class ServiceHttpClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def post(self, path: str, json: dict) -> dict:
        # TODO: retries, error mapping
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(f"{self._base_url}{path}", json=json)
            response.raise_for_status()
            return response.json()
