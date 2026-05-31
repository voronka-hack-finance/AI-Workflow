"""Debug session logging for agent instrumentation."""
from __future__ import annotations

import json
import time
from typing import Any
from urllib import error, request

_SESSION_ID = "c5e41b"
_INGEST_URL = "http://127.0.0.1:7869/ingest/fbe8c4ff-8424-4c9d-9a44-8632f1123f1b"
_FALLBACK_INGEST_URL = (
    "http://host.docker.internal:7869/ingest/fbe8c4ff-8424-4c9d-9a44-8632f1123f1b"
)


def debug_session_log(
    *,
    location: str,
    message: str,
    hypothesis_id: str,
    data: dict[str, Any] | None = None,
    run_id: str = "pre-fix",
) -> None:
    payload = {
        "sessionId": _SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json", "X-Debug-Session-Id": _SESSION_ID}
    for url in (_INGEST_URL, _FALLBACK_INGEST_URL):
        try:
            req = request.Request(url, data=body, headers=headers, method="POST")
            request.urlopen(req, timeout=1)  # noqa: S310
            return
        except (error.URLError, TimeoutError, OSError):
            continue
