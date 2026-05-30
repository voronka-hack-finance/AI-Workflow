"""Intent parsing endpoint."""
from fastapi import APIRouter, HTTPException

from app.core.errors import LLMParseError
from app.parser.service import IntentParserService
from app.schemas.intent_request import IntentParseRequest
from app.schemas.intent_result import IntentParseResponse

router = APIRouter(prefix="/api/v1/intent", tags=["intent"])
_parser_service = IntentParserService()


@router.post("/parse", response_model=IntentParseResponse)
async def parse_intent(request: IntentParseRequest) -> IntentParseResponse:
    try:
        return await _parser_service.parse(request)
    except LLMParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
