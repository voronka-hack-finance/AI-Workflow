# AI Workflow Service

Orchestrates AI pipeline steps via RabbitMQ and HTTP clients.

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
uv run pytest
uv run ruff check .
```

## Endpoints

- `GET /health` — health check
- `POST /api/v1/workflows` — main API (skeleton)

## Status

Skeleton only — business logic marked with `TODO`.
