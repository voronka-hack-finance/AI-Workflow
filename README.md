# AI Financial Assistant — Services Monorepo

Skeleton monorepo for the AI pipeline: workflow orchestration, intent parsing, context building, analytics, and response generation.

Dependencies are managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock` per service). No `requirements.txt`.

## Prerequisites

Install uv: https://docs.astral.sh/uv/getting-started/installation/

**Local-only artifacts (not committed):** `uv sync` may create `.venv/` on your machine for local dev/tests. Docker builds their own venv inside the image and do not use your host `.venv`. `.ruff_cache/` and `.pytest_cache/` are tool caches — also gitignored.

## Services

| Service | Port | Main endpoint |
|---------|------|---------------|
| ai-workflow-service | 8010 | RabbitMQ + `POST /api/v1/workflows` |
| llm-intent-parser-service | 8011 | `POST /api/v1/intent/parse` |
| ai-context-builder-service | 8012 | `POST /api/v1/context/build` |
| analytics-service | 8013 | `POST /api/v1/analytics/run` |
| llm-response-agent-service | 8014 | `POST /api/v1/response/generate` |

## Quick start (local)

```bash
cd ai-workflow-service   # or any service
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
uv run pytest
uv run ruff check .
```

Monorepo helpers:

```bash
make sync    # uv sync in all services
make lock    # uv lock in all services
make test    # uv run pytest in all services
```

## Docker

```bash
cp .env.example .env
make dev-up
```

Each service image runs `uv sync --frozen --no-dev` and starts via `uv run`.

## Documentation

See `docs/` for architecture (existing markdown files must not be overwritten).

## Status

Skeleton only — implement business logic behind `TODO` markers.
