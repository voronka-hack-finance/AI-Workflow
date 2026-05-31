# LLM Response Agent Service

Генерирует финальный ответ пользователю через agent pipeline на основе `FinancialAnalysisResult`.

**Статус: ✅ готово.** Agent router, специализированные agents, final editor, mock / openai_compatible LLM, input/output validation.

---

## Роль в системе

```text
Workflow → POST /response/generate → [этот сервис] → ResponseGenerateResult → ai.workflow.results
```

Response Agent **не пересчитывает** аналитику — только объясняет validated facts.

---

## Локальный запуск

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8014
uv run pytest
uv run ruff check .
```

---

## Эндпоинты

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/health` | Проверка здоровья |
| POST | `/api/v1/response/generate` | Генерация финального ответа |

---

## Pipeline

```text
InputValidator → AgentRouter → Agents (parallel) → FinalEditor → OutputValidator → ResponseGenerateResult
```

### Agents

`budget_planner`, `spending_detective`, `habit_coach`, `growth_agent`, `safety_agent`.

---

## Выбор провайдера

| Значение | Назначение |
|----------|------------|
| `mock` | Детерминированный ответ для тестов и CI |
| `openai_compatible` | OpenAI-compatible сервер — **по умолчанию для dev** |

```env
RESPONSE_AGENT_LLM_PROVIDER=openai_compatible
RESPONSE_AGENT_LLM_MODEL=qwen2.5-7b-instruct
OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_COMPATIBLE_API_KEY=local
```

---

## Статус

| Область | Состояние |
|---------|-----------|
| ResponseAgentService (полный pipeline) | ✅ |
| Agent router + 5 agents | ✅ |
| Final editor + fallback | ✅ |
| Input/output validation | ✅ |
| Провайдеры mock / openai_compatible | ✅ |
| Boundary rules (LLM не считает финансы) | ✅ |
