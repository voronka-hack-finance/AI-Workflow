# AI Context Builder Service

Builds context package and execution plan from intent.

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8012
uv run pytest
uv run ruff check .
```

## Endpoints

- `GET /health` — health check
- `POST /api/v1/context/build` — main API (skeleton)

## Status

Skeleton only — business logic marked with `TODO`.
