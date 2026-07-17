from datetime import timedelta

import pytest
from conftest import result_payload
from pydantic import ValidationError

from agent.schemas import ResearcherAppResult


def test_valid_research_result_round_trips() -> None:
    result = ResearcherAppResult.model_validate(result_payload())
    assert result.authentication.methods[0].value == "api_key"
    assert result.model_dump(mode="json")["mcp"]["status"] == "none_found"


def test_unknown_fields_are_rejected() -> None:
    payload = result_payload()
    payload["fabricated"] = True
    with pytest.raises(ValidationError, match="Extra inputs"):
        ResearcherAppResult.model_validate(payload)


def test_referenced_evidence_must_exist() -> None:
    payload = result_payload()
    payload["authentication"]["evidence_ids"] = ["missing"]  # type: ignore[index]
    with pytest.raises(ValidationError, match="unknown evidence IDs"):
        ResearcherAppResult.model_validate(payload)


def test_timestamp_order_is_validated() -> None:
    payload = result_payload()
    created = payload["timestamps"]["created_at"]  # type: ignore[index]
    payload["timestamps"]["updated_at"] = (  # type: ignore[index]
        __import__("datetime").datetime.fromisoformat(created) - timedelta(days=1)
    ).isoformat()
    with pytest.raises(ValidationError, match="updated_at"):
        ResearcherAppResult.model_validate(payload)
