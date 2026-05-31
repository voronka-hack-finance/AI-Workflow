"""Response generation endpoint."""
from fastapi import APIRouter

from app.response_pipeline.response_agent_service import ResponseAgentService
from app.schemas.response_request import ResponseGenerateRequest
from app.schemas.response_result import ResponseGenerateResult

router = APIRouter(prefix="/api/v1/response", tags=["response"])
_response_service = ResponseAgentService()


@router.post("/generate", response_model=ResponseGenerateResult)
async def generate_response(request: ResponseGenerateRequest) -> ResponseGenerateResult:
    return await _response_service.generate(request)
