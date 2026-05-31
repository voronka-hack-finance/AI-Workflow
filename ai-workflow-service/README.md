# AI Workflow Service

Оркестратор AI-конвейера: RabbitMQ consumer/publisher, HTTP-клиенты к downstream-сервисам, LangGraph.

**Статус: ✅ готово.** Consumer слушает `ai.workflow.tasks` и запускает pipeline при получении job. Результат публикуется в `ai.workflow.results` для backend.

---

## Роль в системе

```text
Backend → ai.workflow.tasks → [этот сервис] → ai.workflow.results → Backend
                                    │
                    Intent Parser → Context Builder → Analytics → Response Agent
```

Workflow запускается **автоматически** при получении сообщения из очереди — HTTP-триггер не нужен в production.

---

## Локальный запуск

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
uv run pytest
uv run ruff check .
```

---

## Эндпоинты

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/health` | Проверка здоровья |
| POST | `/api/v1/workflow/run` | Синхронный запуск (dev/test) |
| POST | `/api/v1/workflow/run/debug` | Debug-запуск с результатами каждого шага |
| POST | `/api/v1/workflow/run/batch` | До 10 синхронных запусков |
| POST | `/api/v1/workflow/enqueue` | Публикация задачи в RabbitMQ (production-like) |

---

## Точки входа workflow

1. **RabbitMQ** (production) — очередь `ai.workflow.tasks`, consumer внутри сервиса
2. **HTTP `/run`** — синхронный dev/test путь, возвращает `WorkflowResult`
3. **HTTP `/enqueue`** — валидация задачи и публикация в RabbitMQ, статус `queued`
4. **HTTP `/run/debug`** — debug-путь с результатами шагов

---

## RabbitMQ

| Очередь | Направление | Контракт |
|---------|-------------|----------|
| `ai.workflow.tasks` | consume | `WorkflowTask` — входная job от backend |
| `ai.workflow.results` | publish | `WorkflowResultMessage` — финальный ответ для backend |

После завершения pipeline orchestrator публикует `WorkflowResultMessage` с полями `status`, `content`, `errors`. Backend consumer забирает результат и доставляет сообщение пользователю.

---

## Debug-запуск

```powershell
$body = @{
  request_id = "req_001"
  workflow_run_id = "run_001"
  user_id = "user_123"
  chat_id = "chat_001"
  raw_message = "Куда уходят деньги?"
  current_date = "2026-05-30"
  timezone = "Europe/Moscow"
} | ConvertTo-Json

# Только intent parser
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/run/debug?stop_after=parse_intent" `
  -ContentType "application/json" -Body $body

# Полный pipeline
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/run/debug" `
  -ContentType "application/json" -Body $body
```

---

## Конфигурация

```env
AI_WORKFLOW_ENABLE_HTTP_TRIGGER=true
AI_WORKFLOW_ENABLE_RABBITMQ_CONSUMER=true
RABBITMQ_URL=amqp://finance_ai:finance_ai@rabbitmq:5672/
RABBITMQ_WORKFLOW_QUEUE=ai.workflow.tasks
RABBITMQ_WORKFLOW_RESULT_QUEUE=ai.workflow.results
INTENT_PARSER_SERVICE_URL=http://llm-intent-parser-service:8011
CONTEXT_BUILDER_SERVICE_URL=http://ai-context-builder-service:8012
ANALYTICS_SERVICE_URL=http://analytics-service:8013
RESPONSE_AGENT_SERVICE_URL=http://llm-response-agent-service:8014
```

`AI_WORKFLOW_ENABLE_HTTP_TRIGGER=false` отключает HTTP trigger-эндпоинты.

---

## Статус

| Область | Состояние |
|---------|-----------|
| LangGraph-граф (intent → context → analytics → response) | ✅ |
| RabbitMQ consumer (`ai.workflow.tasks`) | ✅ |
| RabbitMQ publisher результатов (`ai.workflow.results`) | ✅ |
| HTTP API (run, debug, batch, enqueue) | ✅ |
| HTTP-клиенты downstream | ✅ |
| Pipeline без clarification stops | ✅ |
| Backend Chat client | Mock (реальный HTTP — в backend boundary) |
