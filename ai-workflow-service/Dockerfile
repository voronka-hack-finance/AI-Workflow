FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY ai-workflow-service/pyproject.toml ai-workflow-service/uv.lock ./
COPY packages/shared_contracts ../packages/shared_contracts
COPY packages/shared_http ../packages/shared_http

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY ai-workflow-service/app ./app

EXPOSE 8010

CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
