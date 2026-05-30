# LLM Intent Parser Service

Parses user messages into canonical `intent_result` via LangChain and returns `IntentParserResponse`.

## Run locally

```bash
cd llm-intent-parser-service
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8011
uv run pytest
```

## Provider selection

Use environment variable `INTENT_PARSER_LLM_PROVIDER`:

- `mock` — deterministic parser for tests and CI only
- `openai_compatible` — external OpenAI-compatible server via `langchain-openai` (`ChatOpenAI`) (**default for local dev**)

Default local dev uses LM Studio at `http://127.0.0.1:1234/v1` with model `qwen2.5-7b-instruct` (see `.env.example`).

**Docker Compose** uses `host.docker.internal:1234` so the container can reach LM Studio on the host. Check active provider:

```powershell
Invoke-RestMethod http://127.0.0.1:8011/health
# llm_provider should be "openai_compatible", not "mock"
# few_shot_limit: 0 for local 7B (recommended), omit for full few-shot on larger models
```

Local 7B models (e.g. `qwen2.5-7b-instruct` Q4) often copy the first few-shot example and return `expense_breakdown` for every query. Set `INTENT_PARSER_FEW_SHOT_LIMIT=0` so the model uses only the system prompt + your message.

Example test/CI env:

```env
INTENT_PARSER_LLM_PROVIDER=mock
INTENT_PARSER_LLM_MODEL=mock-intent-parser
```

Example local LM Studio env:

```env
INTENT_PARSER_LLM_PROVIDER=openai_compatible
INTENT_PARSER_LLM_MODEL=qwen2.5-7b-instruct
OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_COMPATIBLE_API_KEY=local
INTENT_PARSER_LLM_TEMPERATURE=0.1
INTENT_PARSER_MAX_OUTPUT_TOKENS=1200
INTENT_PARSER_LLM_TIMEOUT_SECONDS=60
```

The service does not load model weights in-process. LM Studio now and vLLM later both use the same `openai_compatible` provider.

## Endpoints

- `GET /health` — health check
- `POST /api/v1/intent/parse` — parse user message into `IntentParserResponse`

Request example:

```json
{
  "request_id": "req_001",
  "user_id": "user_123",
  "chat_id": "chat_001",
  "raw_message": "Дай рекомендацию по бюджету на месяц.",
  "current_date": "2026-05-29",
  "timezone": "Europe/Moscow",
  "chat_context": {
    "last_6_messages": [],
    "chat_summary": null,
    "active_workflow": null
  }
}
```

## Tests

```bash
INTENT_PARSER_LLM_PROVIDER=mock uv run pytest llm-intent-parser-service/tests
```
