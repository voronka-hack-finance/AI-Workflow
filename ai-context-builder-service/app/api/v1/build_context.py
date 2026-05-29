"""Context build endpoint."""
from fastapi import APIRouter

from app.schemas.context_builder_request import ContextBuilderRequest
from app.schemas.context_package import ContextPackage

router = APIRouter(prefix="/api/v1/context", tags=["context"])


@router.post("/build", response_model=ContextPackage)
async def build_context(request: ContextBuilderRequest) -> ContextPackage:
    # TODO: call ContextBuilderService
    return ContextPackage(user_id=request.user_id)
