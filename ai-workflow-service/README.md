# AI Workflow Service

Оркестратор AI-конвейера: RabbitMQ, HTTP-клиенты к downstream-сервисам, LangGraph.

## Локальный запуск

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
uv run pytest
uv run ruff check .
```

## Эндпоинты

- `GET /health` — проверка здоровья
- `POST /api/v1/workflow/run` — синхронный запуск workflow (dev/test)
- `POST /api/v1/workflow/run/debug` — debug-запуск с результатами каждого шага
- `POST /api/v1/workflow/run/batch` — до 10 синхронных запусков
- `POST /api/v1/workflow/enqueue` — публикация задачи в RabbitMQ (production-like)

## Точки входа workflow

1. **RabbitMQ** — очередь `ai.workflow.tasks` (consumer внутри сервиса)
2. **HTTP `/run`** — синхронный dev/test путь, возвращает `WorkflowResult`
3. **HTTP `/enqueue`** — валидация задачи и публикация в RabbitMQ, статус `queued`
4. **HTTP `/run/debug`** — debug-путь с результатами шагов (`intent_parser` и др.)

## Debug-запуск

Используйте `POST /api/v1/workflow/run/debug` для просмотра промежуточных результатов сервисов.

### Только intent parser (быстрее всего)

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/run/debug?stop_after=parse_intent" `
  -ContentType "application/json" -Body $body
```

Ответ содержит:

- `intent_parser` — полный `IntentParserResponse` в JSON
- `steps[]` — `status`, `duration_ms`, `request_summary`, `response_valid`, `result` по шагам
- downstream-шаги (`build_context`, `run_analytics`, `generate_response`) остаются `not_run`

### Полный pipeline debug

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/run/debug" `
  -ContentType "application/json" -Body $body
```

Возвращает debug-метаданные для каждого HTTP-шага до clarification/ошибки/завершения.

## Примеры HTTP-запросов

Тело запроса (общее для `/run` и `/enqueue`):

```json
{
  "request_id": "req_001",
  "workflow_run_id": "run_001",
  "user_id": "user_123",
  "chat_id": "chat_001",
  "raw_message": "Куда уходят деньги?",
  "current_date": "2026-05-30",
  "timezone": "Europe/Moscow"
}
```

Если `workflow_run_id`, `message_id` или `created_at` не указаны — сервис генерирует их автоматически.

### Синхронный запуск (dev, RabbitMQ не нужен)

PowerShell:

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

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/run" `
  -ContentType "application/json" -Body $body
```

curl:

```bash
curl -X POST http://127.0.0.1:8010/api/v1/workflow/run \
  -H "Content-Type: application/json" \
  -d '{"request_id":"req_001","workflow_run_id":"run_001","user_id":"user_123","chat_id":"chat_001","raw_message":"Куда уходят деньги?","current_date":"2026-05-30","timezone":"Europe/Moscow"}'
```

### Batch-синхронный запуск

```powershell
$body = @{
  items = @(
    @{
      request_id = "req_001"
      workflow_run_id = "run_001"
      user_id = "user_123"
      chat_id = "chat_001"
      raw_message = "Куда уходят деньги?"
      current_date = "2026-05-30"
      timezone = "Europe/Moscow"
    },
    @{
      request_id = "req_002"
      workflow_run_id = "run_002"
      user_id = "user_123"
      chat_id = "chat_001"
      raw_message = "Дай рекомендацию по бюджету на месяц"
      current_date = "2026-05-30"
      timezone = "Europe/Moscow"
    }
  )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/run/batch" `
  -ContentType "application/json" -Body $body
```

### Постановка в очередь RabbitMQ (production-like)

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/enqueue" `
  -ContentType "application/json" -Body $body
```

Пример ответа:

```json
{
  "request_id": "req_001",
  "workflow_run_id": "run_001",
  "user_id": "user_123",
  "chat_id": "chat_001",
  "status": "queued",
  "queue": "ai.workflow.tasks"
}
```

Логи:

```bash
make logs-ai-workflow-service
make logs-llm-intent-parser-service
```

Пересборка Docker после изменений кода:

```bash
docker compose -f docker-compose.dev.yml up -d --build ai-workflow-service
```

## Конфигурация

```env
AI_WORKFLOW_ENABLE_HTTP_TRIGGER=true
AI_WORKFLOW_ENABLE_RABBITMQ_CONSUMER=true
INTENT_PARSER_SERVICE_URL=http://llm-intent-parser-service:8011
```

`AI_WORKFLOW_ENABLE_HTTP_TRIGGER=false` отключает HTTP trigger-эндпоинты.

## Backend Chat

Интеграция с Backend / Chat через порт `BackendChatClient`. Сейчас используется `MockBackendChatClient` (in-memory). HTTP-реализация — в планах.

## Статус

Ядро реализовано: LangGraph-граф, RabbitMQ, HTTP API, клиенты downstream, clarification, debug runner. Backend Chat — mock.
