# LLM Intent Parser Service

Parses user messages into structured intent JSON via LLM.

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8011
uv run pytest
uv run ruff check .
```

## Endpoints

- `GET /health` — health check
- `POST /api/v1/intent/parse` — main API (skeleton)

## Status

Skeleton only — business logic marked with `TODO`.
