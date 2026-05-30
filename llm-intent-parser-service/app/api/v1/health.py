"""Health check endpoint."""
from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "llm-intent-parser-service",
        "llm_provider": settings.intent_parser_llm_provider,
        "llm_model": settings.intent_parser_llm_model,
        "few_shot_limit": (
            "all" if settings.intent_parser_few_shot_limit is None else str(settings.intent_parser_few_shot_limit)
        ),
    }
