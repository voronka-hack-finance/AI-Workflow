# Analytics Service

Runs execution plan functions on context package.

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8013
uv run pytest
uv run ruff check .
```

## Endpoints

- `GET /health` — health check
- `POST /api/v1/analytics/run` — main API (skeleton)

## Status

Skeleton only — business logic marked with `TODO`.
