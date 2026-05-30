# LLM Intent Parser Service

Парсит сообщения пользователя в канонический `intent_result` через LangChain и возвращает `IntentParserResponse`.

## Локальный запуск

```bash
cd llm-intent-parser-service
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8011
uv run pytest
```

## Выбор провайдера

Переменная окружения `INTENT_PARSER_LLM_PROVIDER`:

- `mock` — детерминированный парсер для тестов и CI
- `openai_compatible` — внешний OpenAI-compatible сервер через `langchain-openai` (`ChatOpenAI`) (**по умолчанию для локальной разработки**)

Локально по умолчанию — LM Studio на `http://127.0.0.1:1234/v1`, модель `qwen2.5-7b-instruct` (см. `.env.example`).

**Docker Compose** использует `host.docker.internal:1234`, чтобы контейнер достигал LM Studio на хосте. Проверка активного провайдера:

```powershell
Invoke-RestMethod http://127.0.0.1:8011/health
# llm_provider должен быть "openai_compatible", не "mock"
# few_shot_limit: 0 для локальной 7B (рекомендуется), omit — полный few-shot для больших моделей
```

Локальные 7B-модели (например `qwen2.5-7b-instruct` Q4) часто копируют первый few-shot пример и возвращают `expense_breakdown` на любой запрос. Установите `INTENT_PARSER_FEW_SHOT_LIMIT=0`, чтобы модель использовала только system prompt + ваше сообщение.

Пример env для тестов/CI:

```env
INTENT_PARSER_LLM_PROVIDER=mock
INTENT_PARSER_LLM_MODEL=mock-intent-parser
```

Пример env для локального LM Studio:

```env
INTENT_PARSER_LLM_PROVIDER=openai_compatible
INTENT_PARSER_LLM_MODEL=qwen2.5-7b-instruct
OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_COMPATIBLE_API_KEY=local
INTENT_PARSER_LLM_TEMPERATURE=0.1
INTENT_PARSER_MAX_OUTPUT_TOKENS=1200
INTENT_PARSER_LLM_TIMEOUT_SECONDS=60
```

Сервис не загружает веса модели in-process. LM Studio сейчас и vLLM позже используют один и тот же провайдер `openai_compatible`.

## Эндпоинты

- `GET /health` — проверка здоровья
- `POST /api/v1/intent/parse` — парсинг сообщения в `IntentParserResponse`

Пример запроса:

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

## Тесты

```bash
INTENT_PARSER_LLM_PROVIDER=mock uv run pytest llm-intent-parser-service/tests
```

## Статус

Ядро реализовано: LangChain pipeline, провайдеры mock/openai_compatible, валидация, clarification, category normalizer. Real LLM integration-тесты могут требовать настройки модели.
