"""Human-audit application for researcher results."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent.enums import (
    ApiBreadth,
    AuthenticationMethod,
    BuildabilityVerdict,
    ExistingCustomerAccess,
    IndependentDeveloperAccess,
    McpStatus,
    MultiTenantIntegrationAccess,
)
from agent.schemas import FinalAppResult, ResearcherAppResult

FIELD_PATHS = {
    "category": ("category",),
    "description": ("description",),
    "authentication_methods": ("authentication", "methods"),
    "independent_developer_access": ("credential_access", "independent_developer_access"),
    "existing_customer_access": ("credential_access", "existing_customer_access"),
    "multi_tenant_integration_access": ("credential_access", "multi_tenant_integration_access"),
    "graphql": ("api_surface", "graphql"),
    "bulk_operations": ("api_surface", "bulk_operations"),
    "webhooks_events": ("api_surface", "webhooks"),
    "mcp_status": ("mcp", "status"),
    "buildability_verdict": ("buildability", "verdict"),
}


def _set_path(payload: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value


def _calculate_verdict(output: dict[str, Any]) -> str:
    if (
        output["authentication"]["methods"]
        and "unknown" not in output["authentication"]["methods"]
        and output["credential_access"]["independent_developer_access"]
        == IndependentDeveloperAccess.SELF_SERVE_FREE.value
        and output["credential_access"]["existing_customer_access"]
        == ExistingCustomerAccess.WORKSPACE_ADMIN_REQUIRED.value
        and output["credential_access"]["multi_tenant_integration_access"]
        == MultiTenantIntegrationAccess.SELF_SERVE.value
        and output["api_surface"]["api_breadth"] == ApiBreadth.BROAD.value
        and output["api_surface"]["graphql"] is True
        and output["api_surface"]["bulk_operations"] is True
        and output["api_surface"]["webhooks"] is True
        and output["mcp"]["status"] == McpStatus.OFFICIAL.value
    ):
        return BuildabilityVerdict.BUILD_NOW.value
    return BuildabilityVerdict.UNKNOWN.value


def apply_human_review(decisions_path: Path) -> Path:
    payload = json.loads(decisions_path.read_text(encoding="utf-8"))
    decisions = payload.get("decisions")
    if not isinstance(decisions, list) or len(decisions) != len(FIELD_PATHS):
        raise ValueError("all 11 human decisions are required")
    if any(item.get("human_value") is None for item in decisions):
        raise ValueError("blank human decisions cannot be applied")
    researcher_payload = json.loads(
        Path("data/researcher/salesforce.json").read_text(encoding="utf-8")
    )
    researcher = ResearcherAppResult.model_validate(researcher_payload)
    output = researcher.model_dump(mode="json")
    enum_types = {
        "authentication_methods": AuthenticationMethod,
        "independent_developer_access": IndependentDeveloperAccess,
        "existing_customer_access": ExistingCustomerAccess,
        "multi_tenant_integration_access": MultiTenantIntegrationAccess,
        "mcp_status": McpStatus,
    }
    corrections: list[str] = []
    failure_types: dict[str, str | None] = {}
    audit_rows: list[dict[str, Any]] = []
    now = payload.get("reviewed_at") or datetime.now(UTC).isoformat()
    for item in decisions:
        field = item.get("field")
        value = item.get("human_value")
        if field not in FIELD_PATHS:
            raise ValueError(f"unknown review field: {field}")
        if field == "authentication_methods":
            if not isinstance(value, list) or any(
                v not in {x.value for x in AuthenticationMethod} for v in value
            ):
                raise ValueError(f"invalid enum value for {field}")
        elif field in enum_types and value not in {x.value for x in enum_types[field]}:
            raise ValueError(f"invalid enum value for {field}: {value}")
        elif field in {"graphql", "bulk_operations", "webhooks_events"} and not isinstance(
            value, bool
        ):
            raise ValueError(f"invalid boolean value for {field}")
        _set_path(output, FIELD_PATHS[field], value)
        corrections.append(field)
        failure_types[field] = item.get("failure_type")
        audit_rows.append({
            "app_id": "salesforce", "field": field,
            "researcher_value": item.get("researcher_value"), "human_value": value,
            "correct": item.get("researcher_value") == value,
            "reason": item.get("reason"),
            "supporting_source_urls": item.get("supporting_source_urls", []),
            "failure_type": item.get("failure_type"), "reviewed_at": now,
        })
    output["source_order"] = 1
    output["buildability"]["verdict"] = _calculate_verdict(output)
    output["buildability"]["field_confidence"] = "high"
    resolved_prefixes = (
        "authentication",
        "credential_access",
        "api_surface.webhooks",
        "mcp.status",
        "Missing high-impact evidence for: mcp.status",
        "Buildability remains unresolved",
    )
    output["unresolved_questions"] = [
        question
        for question in output.get("unresolved_questions", [])
        if not question.startswith(resolved_prefixes)
    ]
    output["verification"]["status"] = "finalized"
    output["verification"]["human_reviewed_at"] = now
    output["verification"]["human_corrections"] = corrections
    output["verification"]["human_failure_types"] = failure_types
    output["verification"]["finalized_by"] = payload.get("reviewer") or "human_reviewer"
    output["verification"]["overall_confidence"] = "high"
    result = FinalAppResult.model_validate(output)
    path = Path("data/final/salesforce.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    audit = Path("evaluation/salesforce_manual_audit.json")
    audit.parent.mkdir(parents=True, exist_ok=True)
    audit.write_text(
        json.dumps(
            {"app_id": "salesforce", "reviewed_at": now, "decisions": audit_rows},
            indent=2,
        ),
        encoding="utf-8",
    )
    return path
