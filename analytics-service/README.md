# Analytics Service

Выполняет analytics functions над Context Package и возвращает `FinancialAnalysisResult`.

## Локальный запуск

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8013
uv run pytest
uv run ruff check .
```

## Эндпоинты

- `GET /health` — проверка здоровья
- `POST /api/v1/analytics/run` — принимает `ContextPackage`, возвращает `FinancialAnalysisResult`

## Env

```env
ANALYTICS_SERVICE_NAME=analytics-service
ANALYTICS_SERVICE_PORT=8013
ANALYTICS_RULES_VERSION=v1.0
ANALYTICS_DEFAULT_CURRENCY=RUB
```

## Архитектура

```text
ContextPackage → AnalyticsRunner → ExecutionPlanRunner → functions → FinancialAnalysisResult
```

Сервис не вызывает LLM и не обращается к backend.
