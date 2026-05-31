# LLM Intent Parser Service

Парсит сообщения пользователя в канонический `intent_result` через LangChain и возвращает `IntentParserResponse`.

**Статус: ✅ готово.** LangChain pipeline, mock / openai_compatible провайдеры, валидация intent, category normalizer.

---

## Роль в системе

```text
Workflow → POST /intent/parse → [этот сервис] → IntentParserResponse → Context Builder
```

---

## Локальный запуск

```bash
cd llm-intent-parser-service
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8011
uv run pytest
```

---

## Эндпоинты

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/health` | Проверка здоровья |
| POST | `/api/v1/intent/parse` | Парсинг сообщения в `IntentParserResponse` |

---

## Выбор провайдера

Переменная окружения `INTENT_PARSER_LLM_PROVIDER`:

| Значение | Назначение |
|----------|------------|
| `mock` | Детерминированный парсер для тестов и CI |
| `openai_compatible` | OpenAI-compatible сервер (LM Studio, Ollama, vLLM) — **по умолчанию для dev** |

Локально по умолчанию — LM Studio на `http://127.0.0.1:1234/v1`, модель `qwen2.5-7b-instruct`.

**Docker Compose** использует `host.docker.internal:1234`, чтобы контейнер достигал LM Studio на хосте.

```powershell
Invoke-RestMethod http://127.0.0.1:8011/health
# llm_provider: "openai_compatible"
```

Локальные 7B-модели часто копируют few-shot примеры. Установите `INTENT_PARSER_FEW_SHOT_LIMIT=0` для system prompt + сообщение пользователя.

### Примеры env

Тесты/CI:

```env
INTENT_PARSER_LLM_PROVIDER=mock
INTENT_PARSER_LLM_MODEL=mock-intent-parser
```

Локальный LM Studio:

```env
INTENT_PARSER_LLM_PROVIDER=openai_compatible
INTENT_PARSER_LLM_MODEL=qwen2.5-7b-instruct
OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_COMPATIBLE_API_KEY=local
INTENT_PARSER_FEW_SHOT_LIMIT=0
```

---

## Тесты

```bash
INTENT_PARSER_LLM_PROVIDER=mock uv run pytest llm-intent-parser-service/tests
```

---

## Статус

| Область | Состояние |
|---------|-----------|
| LangChain pipeline | ✅ |
| Провайдеры mock / openai_compatible | ✅ |
| Валидация intent + category normalizer | ✅ |
| Message hints | ✅ |
| Real LLM integration-тесты | Опционально, требуют настройки модели |
