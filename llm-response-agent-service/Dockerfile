FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY llm-response-agent-service/pyproject.toml llm-response-agent-service/uv.lock ./
COPY packages/shared_contracts ../packages/shared_contracts

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY llm-response-agent-service/app ./app

EXPOSE 8014

CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8014"]
