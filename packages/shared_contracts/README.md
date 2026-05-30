# shared_contracts

Shared Pydantic contracts for AI services.

Distribution name: `shared-contracts`  
Import path: `shared_contracts`

## Layout

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

Package modules live directly in `packages/shared_contracts/` — no nested duplicate folder.

## Usage

Run tests from a service venv (packages do not keep their own `.venv`):

```bash
cd ai-workflow-service
uv run pytest ../packages/shared_contracts/tests -q
```

## Import check

```python
from shared_contracts.intent_result import IntentResult, IntentParserResponse
from shared_contracts.normalized_data import TransactionNormalized, UserFinancialContextNormalized, CategoryProfile
from shared_contracts.context_package import ContextPackage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult, FunctionResult
from shared_contracts.response_agent_result import ResponseAgentResult
```
