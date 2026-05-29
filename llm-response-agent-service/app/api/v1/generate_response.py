"""Response generation endpoint."""
from fastapi import APIRouter

from app.schemas.response_request import ResponseGenerateRequest
from app.schemas.response_result import ResponseGenerateResult

router = APIRouter(prefix="/api/v1/response", tags=["response"])


@router.post("/generate", response_model=ResponseGenerateResult)
async def generate_response(request: ResponseGenerateRequest) -> ResponseGenerateResult:
    # TODO: run ResponseAgentService pipeline
    return ResponseGenerateResult(answer="")
