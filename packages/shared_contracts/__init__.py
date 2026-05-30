"""Shared Pydantic contracts for AI services."""

from shared_contracts.context_package import ContextPackage
from shared_contracts.financial_analysis_result import FinancialAnalysisResult, FunctionResult
from shared_contracts.intent_result import IntentParserResponse, IntentResult
from shared_contracts.normalized_data import (
    CategoryProfile,
    TransactionNormalized,
    UserFinancialContextNormalized,
)
from shared_contracts.response_agent_result import ResponseAgentResult

__all__ = [
    "CategoryProfile",
    "ContextPackage",
    "FinancialAnalysisResult",
    "FunctionResult",
    "IntentParserResponse",
    "IntentResult",
    "ResponseAgentResult",
    "TransactionNormalized",
    "UserFinancialContextNormalized",
]
