# Analytics Service

Выполняет analytics functions над `ContextPackage` и возвращает `FinancialAnalysisResult`.

**Статус: ✅ готово.** 14 analytics functions, ExecutionPlanRunner, data quality gate, полный `FinancialAnalysisResult`.

---

## Роль в системе

```text
Workflow → POST /analytics/run → [этот сервис] → FinancialAnalysisResult → Response Agent
```

Сервис не вызывает LLM и не обращается к backend.

---

## Локальный запуск

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8013
uv run pytest
uv run ruff check .
```

---

## Эндпоинты


| Метод | Путь                    | Назначение                                                       |
| ----- | ----------------------- | ---------------------------------------------------------------- |
| GET   | `/health`               | Проверка здоровья                                                |
| POST  | `/api/v1/analytics/run` | Принимает `ContextPackage`, возвращает `FinancialAnalysisResult` |


---

## Архитектура

```text
ContextPackage → AnalyticsRunner → ExecutionPlanRunner → functions → FinancialAnalysisResult
```

### Analytics functions

`expense_breakdown`, `income_analysis`, `cashflow_analysis`, `category_analysis`, `period_analysis`, `budget_plan`, `budget_recommendation`, `goal_analysis`, `debt_analysis`, `emergency_fund_analysis`, `spending_leak_detection`, `transfer_analysis`, `action_plan`.

---

## Конфигурация

```env
ANALYTICS_SERVICE_NAME=analytics-service
ANALYTICS_SERVICE_PORT=8013
ANALYTICS_RULES_VERSION=v1.0
ANALYTICS_DEFAULT_CURRENCY=RUB
```

---

## Статус


| Область                               | Состояние |
| ------------------------------------- | --------- |
| AnalyticsRunner + ExecutionPlanRunner | ✅         |
| 14 analytics functions                | ✅         |
| FinancialAnalysisResult builder       | ✅         |
| Data quality gate                     | ✅         |
| Boundary rules (priority, risk, tags) | ✅         |


