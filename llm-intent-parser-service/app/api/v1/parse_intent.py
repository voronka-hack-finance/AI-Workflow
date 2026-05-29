"""Intent parsing endpoint."""
from fastapi import APIRouter

from app.schemas.intent_request import IntentParseRequest
from app.schemas.intent_result import IntentParseResponse

router = APIRouter(prefix="/api/v1/intent", tags=["intent"])


@router.post("/parse", response_model=IntentParseResponse)
async def parse_intent(request: IntentParseRequest) -> IntentParseResponse:
    # TODO: call IntentParserService and LLM client
    return IntentParseResponse(intent="unknown", confidence=0.0)
