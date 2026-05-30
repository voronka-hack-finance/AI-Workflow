# AI Context Builder Service

Собирает context package и execution plan на основе intent.

## Локальный запуск

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8012
uv run pytest
uv run ruff check .
```

## Эндпоинты

- `GET /health` — проверка здоровья
- `POST /api/v1/context/build` — основной API (заглушка)

## Статус

Каркас: FastAPI, Pydantic-схемы (`ContextPackage`, normalized data, category profile), структура модулей (`builder/`, `planning/`, `data_clients/`, `data_adapters/`).

`POST /context/build` возвращает stub-ответ. Бизнес-логика (`ContextBuilderService`, data clients, mappers) — в TODO.
