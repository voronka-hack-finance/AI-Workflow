"""Context build endpoint."""
from fastapi import APIRouter

from app.schemas.context_builder_request import ContextBuilderRequest
from app.schemas.context_package import ContextPackage
from shared_contracts.context_package import (
    AppliedFilters,
    ContextBuilderMetadata,
    ContextPackageMetadata,
    ResolvedComparison,
    ResolvedPeriod,
    SourceMessage,
)
from shared_contracts.intent_result import IntentResult

router = APIRouter(prefix="/api/v1/context", tags=["context"])


@router.post("/build", response_model=ContextPackage)
async def build_context(request: ContextBuilderRequest) -> ContextPackage:
    # TODO: call ContextBuilderService
    return ContextPackage(
        request_id="stub-request",
        workflow_run_id="stub-run",
        user_id=request.user_id,
        chat_id="stub-chat",
        source_message=SourceMessage(
            raw_message="",
            current_date="2026-01-01",
            timezone="UTC",
        ),
        intent_result=IntentResult(),
        context_builder=ContextBuilderMetadata(
            resolved_period=ResolvedPeriod(type="unknown"),
            resolved_comparison=ResolvedComparison(enabled=False),
            applied_filters=AppliedFilters(
                period={"start_date": None, "end_date": None},
            ),
        ),
        metadata=ContextPackageMetadata(created_at="2026-01-01T00:00:00Z"),
    )
