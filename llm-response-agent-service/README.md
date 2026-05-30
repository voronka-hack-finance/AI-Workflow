# LLM Response Agent Service

Генерирует финальный ответ пользователю через agent pipeline.

## Локальный запуск

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8014
uv run pytest
uv run ruff check .
```

## Эндпоинты

- `GET /health` — проверка здоровья
- `POST /api/v1/response/generate` — основной API (dev-stub)

## Статус

`POST /response/generate` работает через `build_dev_final_answer()` — шаблонный текст на русском без вызова LLM. Контрактная сборка `ResponseGenerateResult` (validation/routing/editor — hardcoded `"passed"` / `"dev_stub"`).

Каркас agents/prompts/validators/pipeline на месте. `ResponseAgentService`, `LLMClient`, полноценный LangChain pipeline — в TODO.
