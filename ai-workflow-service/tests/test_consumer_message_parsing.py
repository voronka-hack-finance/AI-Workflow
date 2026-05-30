"""RabbitMQ message parsing tests."""
from __future__ import annotations

import json

import pytest

from app.core.errors import RabbitMQMessageError
from app.queue.message import parse_workflow_message
from tests.conftest import sample_task


def test_parse_valid_message() -> None:
    task = sample_task()
    body = json.dumps(task.model_dump()).encode("utf-8")

    parsed = parse_workflow_message(body)

    assert parsed.request_id == task.request_id
    assert parsed.workflow_run_id == task.workflow_run_id


def test_invalid_json_raises() -> None:
    with pytest.raises(RabbitMQMessageError):
        parse_workflow_message(b"not-json")


def test_missing_required_field_raises() -> None:
    payload = sample_task().model_dump()
    del payload["request_id"]
    body = json.dumps(payload).encode("utf-8")

    with pytest.raises(RabbitMQMessageError):
        parse_workflow_message(body)


def test_non_object_payload_raises() -> None:
    with pytest.raises(RabbitMQMessageError):
        parse_workflow_message(json.dumps(["bad"]).encode("utf-8"))
