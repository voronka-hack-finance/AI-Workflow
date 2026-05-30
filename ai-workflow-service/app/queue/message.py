"""RabbitMQ message parsing."""
from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from app.core.errors import RabbitMQMessageError
from app.schemas.workflow_task import WorkflowTask


def parse_workflow_message(body: bytes) -> WorkflowTask:
    try:
        payload: Any = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RabbitMQMessageError("Invalid JSON payload") from exc

    if not isinstance(payload, dict):
        raise RabbitMQMessageError("Message payload must be a JSON object")

    try:
        return WorkflowTask.model_validate(payload)
    except ValidationError as exc:
        raise RabbitMQMessageError(str(exc)) from exc
