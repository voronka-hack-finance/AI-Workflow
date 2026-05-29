# LLM Response Agent Service

Generates final user-facing response via agent pipeline.

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8014
uv run pytest
uv run ruff check .
```

## Endpoints

- `GET /health` — health check
- `POST /api/v1/response/generate` — main API (skeleton)

## Status

Skeleton only — business logic marked with `TODO`.
