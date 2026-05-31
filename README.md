# AI Financial Assistant — Monorepo

Monorepo AI-конвейера финансового ассистента: оркестрация workflow, парсинг намерений, сбор контекста, аналитика и генерация ответа.

**Статус проекта: готов к интеграции с backend.** Все сервисы реализованы, связаны между собой и с backend через RabbitMQ. Workflow запускается автоматически при получении job из очереди; результат публикуется обратно в RabbitMQ, backend доставляет сообщение пользователю.

Зависимости управляются через [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock` в каждом сервисе).

---

## Назначение

Система принимает сообщение пользователя из Backend / Chat Service, проходит через цепочку специализированных AI-сервисов и возвращает финансовый ответ. Каждый сервис отвечает за одну зону ответственности.

---

## Поток данных (production)

```mermaid
sequenceDiagram
  participant User as Пользователь
  participant Backend as Backend / Chat
  participant RMQ as RabbitMQ
  participant WF as AI Workflow Service
  participant IP as LLM Intent Parser
  participant CB as AI Context Builder
  participant AN as Analytics Service
  participant RA as LLM Response Agent

  User->>Backend: сообщение в чат
  Backend->>RMQ: publish ai.workflow.tasks
  RMQ->>WF: consumer забирает job
  WF->>IP: POST /intent/parse
  WF->>CB: POST /context/build
  CB->>RMQ: publish ai.backend.data.requests
  RMQ->>Backend: backend-data-worker
  Backend->>RMQ: publish ai.context_builder.backend_data.responses
  RMQ->>CB: ответ с данными
  WF->>AN: POST /analytics/run
  WF->>RA: POST /response/generate
  WF->>RMQ: publish ai.workflow.results
  RMQ->>Backend: consumer забирает результат
  Backend->>User: финальное сообщение в чат
```



### Очереди RabbitMQ


| Очередь                                     | Направление               | Назначение                                 |
| ------------------------------------------- | ------------------------- | ------------------------------------------ |
| `ai.workflow.tasks`                         | Backend → AI Workflow     | Задача на обработку сообщения пользователя |
| `ai.workflow.results`                       | AI Workflow → Backend     | Финальный ответ (`WorkflowResultMessage`)  |
| `ai.backend.data.requests`                  | Context Builder → Backend | Запрос финансовых данных пользователя      |
| `ai.context_builder.backend_data.responses` | Backend → Context Builder | Ответ с raw-данными для нормализации       |


Workflow **не ждёт HTTP-триггера** — consumer в `ai-workflow-service` слушает `ai.workflow.tasks` и запускает pipeline сразу после получения job. По завершении orchestrator публикует результат в `ai.workflow.results`; backend consumer забирает его и отправляет сообщение пользователю.

---

## Архитектура сервисов

```mermaid
flowchart TB
  Backend["Backend / Chat Service"]
  RMQ["RabbitMQ"]

  Backend -->|"ai.workflow.tasks"| RMQ
  RMQ -->|"consumer"| WF["AI Workflow Service"]
  WF -->|"HTTP"| IP["LLM Intent Parser"]
  WF -->|"HTTP"| CB["AI Context Builder"]
  WF -->|"HTTP"| AN["Analytics Service"]
  WF -->|"HTTP"| RA["LLM Response Agent"]
  CB -->|"ai.backend.data.requests"| RMQ
  RMQ -->|"backend-data-worker"| Backend
  WF -->|"ai.workflow.results"| RMQ
  RMQ --> Backend
```



---

## Границы сервисов


| Сервис                  | Ответственность                                                                         |
| ----------------------- | --------------------------------------------------------------------------------------- |
| **AI Workflow Service** | Только оркестрация (LangGraph): consumer/publisher RabbitMQ, HTTP-вызовы downstream     |
| **LLM Intent Parser**   | Понимает запрос пользователя, возвращает структурированный intent                       |
| **AI Context Builder**  | Готовит нормализованные данные и `ContextPackage`; backend data — только через RabbitMQ |
| **Analytics Service**   | Считает финансовые факты по execution plan                                              |
| **LLM Response Agent**  | Формирует финальный ответ пользователю на основе аналитики                              |
| **Backend / Chat**      | Принимает сообщения, публикует workflow jobs, отдаёт данные и доставляет ответ          |


**Инварианты:** LLM не выполняет финансовые расчёты; Response Agent не пересчитывает аналитику.

---

## Стек


| Компонент      | Использование                                            |
| -------------- | -------------------------------------------------------- |
| Python 3.12    | Все сервисы                                              |
| FastAPI        | HTTP API                                                 |
| uv             | Управление зависимостями и запуск                        |
| Pydantic       | Контракты и валидация                                    |
| RabbitMQ       | Асинхронные workflow jobs, backend data jobs, результаты |
| LangGraph      | Оркестрация workflow (только `ai-workflow-service`)      |
| LangChain      | Intent Parser, Response Agent                            |
| Docker Compose | Dev и production стенды                                  |
| nginx          | Dev gateway на порту 8080                                |


---

## Структура monorepo

```text
ai-workflow/
├── ai-workflow-service/          # оркестратор, RabbitMQ consumer/publisher
├── llm-intent-parser-service/    # парсинг намерений
├── ai-context-builder-service/   # сбор контекста, backend data via RabbitMQ
├── analytics-service/            # финансовая аналитика
├── llm-response-agent-service/   # генерация ответа
├── packages/
│   ├── shared_contracts/         # общие Pydantic-модели
│   ├── shared_http/              # HTTP-клиент с retry
│   ├── shared_logging/           # общий логгер
│   └── shared_config/            # базовые настройки
├── infra/                        # RabbitMQ, nginx
├── docker-compose.dev.yml
├── docker-compose.prod.yml
└── Makefile
```

---

## Сервисы и порты


| Сервис                     | Порт | Основной API                                         |
| -------------------------- | ---- | ---------------------------------------------------- |
| ai-workflow-service        | 8010 | RabbitMQ consumer; `POST /api/v1/workflow/run` (dev) |
| llm-intent-parser-service  | 8011 | `POST /api/v1/intent/parse`                          |
| ai-context-builder-service | 8012 | `POST /api/v1/context/build`                         |
| analytics-service          | 8013 | `POST /api/v1/analytics/run`                         |
| llm-response-agent-service | 8014 | `POST /api/v1/response/generate`                     |


Дополнительно: RabbitMQ (5672, management UI 15672), nginx (8080).

---

## Статус реализации


| Компонент                      | Статус   | Что реализовано                                                                                                                |
| ------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **ai-workflow-service**        | ✅ Готово | LangGraph-граф, RabbitMQ consumer (`ai.workflow.tasks`), publisher результатов (`ai.workflow.results`), HTTP API, debug runner |
| **llm-intent-parser-service**  | ✅ Готово | LangChain pipeline, mock / openai_compatible провайдеры, валидация intent, category normalizer                                 |
| **ai-context-builder-service** | ✅ Готово | Function Registry, planning, RabbitMQ backend data jobs, mock provider, normalization, data quality, полный `ContextPackage`   |
| **analytics-service**          | ✅ Готово | 14 analytics functions, ExecutionPlanRunner, `FinancialAnalysisResult`, data quality gate                                      |
| **llm-response-agent-service** | ✅ Готово | Agent pipeline (router, agents, final editor), mock / openai_compatible LLM, input/output validation                           |
| **packages/shared_contracts**  | ✅ Готово | Общие Pydantic-контракты + тесты                                                                                               |
| **packages/shared_http**       | ✅ Готово | HTTP-клиент с retry (используется workflow)                                                                                    |


**E2E-поток:** Backend публикует job → Workflow consumer запускает pipeline → Context Builder получает данные от backend через RabbitMQ → Analytics считает факты → Response Agent генерирует ответ → результат в `ai.workflow.results` → Backend доставляет пользователю.

Подробнее по каждому сервису — в его `README.md`.

---

## Требования

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker и Docker Compose (для стенда)
- Backend-hackathon (для backend data jobs через RabbitMQ)

---

## Быстрый старт (локально)

```bash
cd ai-workflow-service   # или любой другой сервис
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
uv run pytest
uv run ruff check .
```

Команды monorepo:

```bash
make sync    # uv sync во всех сервисах
make lock    # uv lock во всех сервисах
make test    # pytest во всех сервисах + shared_contracts
```

---

## Docker (dev)

```bash
cp .env.example .env
make dev-up
```

Каждый образ собирается через `uv sync --frozen --no-dev` и запускается через `uv run`.

Логи:

```bash
make logs
make logs-ai-workflow-service
```

### Связка с backend-hackathon

1. Запустите backend docker-compose (gateway `:8081`, RabbitMQ host port `:5673`).
2. Убедитесь, что backend consumer слушает `ai.backend.data.requests` и отвечает в `ai.context_builder.backend_data.responses`.
3. В `.env` monorepo: `CONTEXT_BUILDER_DATA_PROVIDER=rabbitmq`, `BACKEND_RABBITMQ_URL=amqp://guest:guest@host.docker.internal:5673/`.
4. Backend публикует workflow job в `ai.workflow.tasks` и слушает `ai.workflow.results`.

---

## Docker (production)

```bash
cp .env.production.example .env.production
# заполните секреты и LLM-провайдер
docker compose -f docker-compose.prod.yml up -d
```

CI/CD: `.github/workflows/deploy.yml`.

---

## Документация

```text
docs/
├── 00-overview/     # архитектура, границы, data flow
├── 01-contracts/    # Pydantic-контракты между сервисами
└── 02-phases/       # фазы реализации по сервисам
```

Точка входа: `[docs/index.md](docs/index.md)`.