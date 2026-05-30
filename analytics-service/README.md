# Analytics Service

Выполняет функции execution plan над context package.

## Локальный запуск

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8013
uv run pytest
uv run ruff check .
```

## Эндпоинты

- `GET /health` — проверка здоровья
- `POST /api/v1/analytics/run` — основной API (заглушка)

## Статус

Каркас: FastAPI, 14 analytics functions как классы-заглушки, `AnalyticsEngine`, `ExecutionPlanRunner`, scoring/helpers — в TODO.

`POST /analytics/run` возвращает stub-ответ. Реализована утилита `safe_divide()` в `helpers/safe_math.py`.
