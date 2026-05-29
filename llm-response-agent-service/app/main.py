"""FastAPI application entrypoint."""
from fastapi import FastAPI

from app.core.logging import setup_logging
from app.api.v1.health import router as health_router
from app.api.v1.generate_response import router as generate_response_router

setup_logging()

app = FastAPI(
    title="AI Service",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(generate_response_router)
