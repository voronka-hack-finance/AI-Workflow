# AI Workflow Service

Orchestrates AI pipeline steps via RabbitMQ, HTTP clients, and LangGraph.

## Run locally

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
uv run pytest
uv run ruff check .
```

## Endpoints

- `GET /health` — health check
- `POST /api/v1/workflow/run` — run workflow synchronously (dev/test)
- `POST /api/v1/workflow/run/debug` — dev debug run with per-step service results
- `POST /api/v1/workflow/run/batch` — run up to 10 workflows synchronously
- `POST /api/v1/workflow/enqueue` — publish task to RabbitMQ (production-like)

## Workflow entry points

1. **RabbitMQ** — queue `ai.workflow.tasks` (consumer inside the service)
2. **HTTP `/run`** — synchronous dev/test path, returns `WorkflowResult`
3. **HTTP `/enqueue`** — validates task and publishes to RabbitMQ, returns `queued`
4. **HTTP `/run/debug`** — dev debug path with per-step results (`intent_parser`, etc.)

## Debug workflow run

Use `POST /api/v1/workflow/run/debug` to inspect intermediate service results.

### Intent parser only (fastest)

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/run/debug?stop_after=parse_intent" `
  -ContentType "application/json" -Body $body
```

Response includes:

- `intent_parser` — full `IntentParserResponse` as JSON
- `steps[]` — per-step `status`, `duration_ms`, `request_summary`, `response_valid`, `result`
- downstream steps (`build_context`, `run_analytics`, `generate_response`) stay `not_run`

### Full pipeline debug

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/run/debug" `
  -ContentType "application/json" -Body $body
```

Returns debug metadata for every HTTP step that completed before clarification/failure/completion.

## HTTP trigger examples

Request body (shared by `/run` and `/enqueue`):

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

If `workflow_run_id`, `message_id`, or `created_at` are omitted, the service generates them automatically.

### Sync run (dev, no RabbitMQ required)

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

### Batch sync run

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

### Enqueue to RabbitMQ (production-like)

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8010/api/v1/workflow/enqueue" `
  -ContentType "application/json" -Body $body
```

Response example:

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

Watch logs:

```bash
make logs-ai-workflow-service
make logs-llm-intent-parser-service
```

Docker rebuild after code changes:

```bash
docker compose -f docker-compose.dev.yml up -d --build ai-workflow-service
```

## Configuration

```env
AI_WORKFLOW_ENABLE_HTTP_TRIGGER=true
AI_WORKFLOW_ENABLE_RABBITMQ_CONSUMER=true
INTENT_PARSER_SERVICE_URL=http://llm-intent-parser-service:8011
```

Set `AI_WORKFLOW_ENABLE_HTTP_TRIGGER=false` to disable HTTP trigger endpoints.

## Backend Chat

Backend / Chat integration uses `BackendChatClient` port with `MockBackendChatClient` in Phase 03.
HTTP implementation is deferred to Phase 08.
