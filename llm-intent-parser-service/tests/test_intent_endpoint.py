"""Intent endpoint tests."""
from shared_contracts.intent_result import IntentParserResponse

from tests.conftest import minimal_parse_payload


def test_parse_intent_returns_valid_response(client) -> None:
    response = client.post("/api/v1/intent/parse", json=minimal_parse_payload())
    assert response.status_code == 200
    parsed = IntentParserResponse.model_validate(response.json())
    assert parsed.schema_version == "1.0"
    assert parsed.request_id == "req_001"
    assert parsed.intent_result.requested_functions == ["budget_recommendation"]


def test_parse_intent_invalid_payload_returns_422(client) -> None:
    response = client.post("/api/v1/intent/parse", json={"raw_message": "hello"})
    assert response.status_code == 422
