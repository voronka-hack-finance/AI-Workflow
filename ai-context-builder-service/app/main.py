"""FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.build_context import router as build_context_router
from app.api.v1.health import router as health_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.data_clients.factory import close_rabbitmq_client, get_rabbitmq_client

setup_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    if settings.context_builder_data_provider.strip().lower() == "rabbitmq":
        await get_rabbitmq_client(settings).connect()
    yield
    await close_rabbitmq_client()


app = FastAPI(
    title="AI Context Builder Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(build_context_router)
