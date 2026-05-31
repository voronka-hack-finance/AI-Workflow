# AI Context Builder Service

Собирает `ContextPackage` и execution plan на основе intent. Backend data — **только через RabbitMQ**, без HTTP к gateway.

**Статус: ✅ готово.** Function Registry, planning, RabbitMQ backend data jobs, mock provider, normalization, data quality, полный `ContextPackage`.

---

## Роль в системе

```text
Workflow → POST /context/build → [этот сервис]
                                      │
                    ai.backend.data.requests → Backend
                    ai.context_builder.backend_data.responses ← Backend
                                      │
                              ContextPackage → Analytics
```

---

## Локальный запуск

```bash
uv sync
copy .env.example .env   # Windows
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8012
uv run pytest
uv run ruff check .
```

---

## Эндпоинты


| Метод | Путь                    | Назначение              |
| ----- | ----------------------- | ----------------------- |
| GET   | `/health`               | Проверка здоровья       |
| POST  | `/api/v1/context/build` | Сборка `ContextPackage` |


---

## Backend data (RabbitMQ)

Context Builder **не** ходит в backend gateway по HTTP. Данные запрашиваются только через RabbitMQ job:

```text
Context Builder → ai.backend.data.requests
Backend (backend-hackathon) → читает job, достаёт данные
Backend → ai.context_builder.backend_data.responses
Context Builder → normalize → ContextPackage
```

Consumer `ai.backend.data.requests` живёт **в backend-репозитории**, не в AI monorepo.

### Локальная связка с backend-hackathon

1. Запустите backend docker-compose (gateway `:8081`, RabbitMQ host port `:5673`).
2. Убедитесь, что backend consumer подписан на `ai.backend.data.requests` и отвечает в `ai.context_builder.backend_data.responses`.
3. Context Builder `.env`:

```env
CONTEXT_BUILDER_DATA_PROVIDER=rabbitmq
RABBITMQ_URL=amqp://guest:guest@localhost:5673/
```

Тесты используют `mock` автоматически (`tests/conftest.py`).

---

## Статус


| Область                       | Состояние |
| ----------------------------- | --------- |
| Function Registry + planning  | ✅         |
| RabbitMQ backend data jobs    | ✅         |
| Mock data provider (тесты/CI) | ✅         |
| Data adapters + normalization | ✅         |
| Data quality checker          | ✅         |
| Полный `ContextPackage`       | ✅         |


