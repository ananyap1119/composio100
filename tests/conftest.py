from datetime import UTC, datetime

import pytest

from agent.schemas import ResearcherAppResult


def result_payload() -> dict[str, object]:
    now = datetime(2026, 1, 1, tzinfo=UTC).isoformat()
    evidence = [
        {
            "evidence_id": f"ev-{section}",
            "field": section,
            "claim": f"Official {section} documentation describes this field",
            "url": f"https://example.com/{section}",
            "page_title": f"{section} docs",
            "source_type": "official",
            "excerpt": "Official documentation statement.",
            "retrieved_at": now,
            "published_or_updated_at": None,
            "supports_claim": True,
            "notes": None,
        }
        for section in ("authentication", "credential_access", "api_surface", "mcp", "buildability")
    ]
    return {
        "app_id": "example-app",
        "app_name": "Example App",
        "domain": "example.com",
        "category": "Example",
        "description": None,
        "authentication": {
            "methods": ["api_key"],
            "notes": None,
            "field_confidence": "high",
            "evidence_ids": ["ev-authentication"],
        },
        "credential_access": {
            "independent_developer_access": "unknown",
            "existing_customer_access": "unknown",
            "multi_tenant_integration_access": "unknown",
            "free_or_trial_notes": None,
            "paid_plan_notes": None,
            "admin_or_approval_notes": None,
            "field_confidence": "high",
            "evidence_ids": ["ev-credential_access"],
        },
        "api_surface": {
            "documented_public_api": None,
            "rest": None,
            "graphql": None,
            "webhooks": None,
            "websocket": None,
            "sdk_available": None,
            "read_operations": None,
            "write_operations": None,
            "bulk_operations": None,
            "api_breadth": "unknown",
            "important_resources": [],
            "limitations": [],
            "field_confidence": "high",
            "evidence_ids": ["ev-api_surface"],
        },
        "mcp": {
            "status": "none_found",
            "official_url": None,
            "transport_or_hosting_notes": None,
            "capabilities": [],
            "limitations": [],
            "field_confidence": "high",
            "evidence_ids": ["ev-mcp"],
        },
        "buildability": {
            "verdict": "unknown",
            "main_blocker": None,
            "secondary_blockers": [],
            "single_workspace_buildable": None,
            "public_multi_tenant_buildable": None,
            "reasoning_summary": None,
            "field_confidence": "high",
            "evidence_ids": ["ev-buildability"],
        },
        "evidence": evidence,
        "unresolved_questions": [],
        "verification": {
            "status": "not_started",
            "researcher_completed_at": None,
            "verifier_completed_at": None,
            "human_reviewed_at": None,
            "researcher_model": None,
            "verifier_model": None,
            "researcher_verifier_disagreements": [],
            "human_corrections": [],
            "finalized_by": None,
            "overall_confidence": "high",
        },
        "timestamps": {"created_at": now, "updated_at": now},
    }


@pytest.fixture
def researcher() -> ResearcherAppResult:
    return ResearcherAppResult.model_validate(result_payload())


