# shared_contracts

Общие Pydantic-контракты для AI-сервисов и RabbitMQ-сообщений.

**Статус: ✅ готово.**

Имя пакета: `shared-contracts`  
Импорт: `shared_contracts`

---

## Структура

```text
packages/shared_contracts/
├── __init__.py
├── common.py
├── intent_result.py
├── normalized_data.py
├── context_package.py
├── financial_analysis_result.py
├── response_agent_result.py
├── tests/
├── pyproject.toml
└── README.md
```

---

## Использование

Запуск тестов из сервиса:

```bash
cd ai-workflow-service
uv run pytest ../packages/shared_contracts/tests -q
```

---

## Проверка импорта

```python
from shared_contracts.intent_result import IntentResult, IntentParserResponse
from shared_contracts.normalized_data import TransactionNormalized, UserFinancialContextNormalized, CategoryProfile
from shared_contracts.context_package import ContextPackage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult, FunctionResult
from shared_contracts.response_agent_result import ResponseAgentResult
```
