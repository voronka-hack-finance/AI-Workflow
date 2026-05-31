"""Human-readable workflow job tracing for docker logs."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("app.queue.workflow_job")


def _rabbitmq_target(rabbitmq_url: str) -> str:
    if "@" in rabbitmq_url:
        return rabbitmq_url.split("@", 1)[1]
    return rabbitmq_url


def log_workflow_job(event: str, **fields: Any) -> None:
    parts = [f"{key}={value}" for key, value in fields.items()]
    suffix = " ".join(parts)
    logger.info("WORKFLOW_JOB_%s %s", event, suffix)


def log_workflow_result(event: str, **fields: Any) -> None:
    parts = [f"{key}={value}" for key, value in fields.items()]
    suffix = " ".join(parts)
    logger.info("WORKFLOW_RESULT_%s %s", event, suffix)


def log_service_rabbitmq_config(
    *,
    service: str,
    consumer_enabled: bool,
    tasks_queue: str,
    results_queue: str,
    rabbitmq_url: str,
) -> None:
    log_workflow_job(
        "SERVICE_CONFIG",
        service=service,
        consumer_enabled=consumer_enabled,
        tasks_queue=tasks_queue,
        results_queue=results_queue,
        broker=_rabbitmq_target(rabbitmq_url),
    )
