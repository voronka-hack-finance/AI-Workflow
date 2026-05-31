"""Context build endpoint."""
from fastapi import APIRouter, Depends, HTTPException

from app.builder.context_builder_service import ContextBuilderService
from app.builder.deps import get_context_builder_service
from app.core.errors import BackendDataTimeoutError, BackendDataValidationError
from app.schemas.context_builder_request import ContextBuilderRequest
from shared_contracts.context_package import ContextPackage

router = APIRouter(prefix="/api/v1/context", tags=["context"])


@router.post("/build", response_model=ContextPackage)
async def build_context(
    request: ContextBuilderRequest,
    service: ContextBuilderService = Depends(get_context_builder_service),
) -> ContextPackage:
    try:
        return await service.build(request)
    except BackendDataTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except BackendDataValidationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
