"""Validated final-result JSON and flattened CSV exporters."""

import csv
import json
from collections.abc import Iterable
from pathlib import Path

from agent.schemas import FinalAppResult

CSV_FIELDS = [
    "source_order",
    "app_id",
    "app_name",
    "domain",
    "category",
    "authentication_methods",
    "independent_developer_access",
    "existing_customer_access",
    "multi_tenant_integration_access",
    "documented_public_api",
    "api_breadth",
    "mcp_status",
    "buildability_verdict",
    "overall_confidence",
    "evidence_urls",
]


def _csv_row(result: FinalAppResult) -> dict[str, object]:
    return {
        "source_order": result.source_order,
        "app_id": result.app_id,
        "app_name": result.app_name,
        "domain": result.domain,
        "category": result.category or "",
        "authentication_methods": "|".join(
            method.value for method in result.authentication.methods
        ),
        "independent_developer_access": result.credential_access.independent_developer_access.value,
        "existing_customer_access": result.credential_access.existing_customer_access.value,
        "multi_tenant_integration_access": (
            result.credential_access.multi_tenant_integration_access.value
        ),
        "documented_public_api": result.api_surface.documented_public_api,
        "api_breadth": result.api_surface.api_breadth.value,
        "mcp_status": result.mcp.status.value,
        "buildability_verdict": result.buildability.verdict.value,
        "overall_confidence": result.verification.overall_confidence.value,
        "evidence_urls": "|".join(dict.fromkeys(str(item.url) for item in result.evidence)),
    }


def export_final_results(
    records: Iterable[FinalAppResult], output_dir: Path = Path("data/final")
) -> tuple[Path, Path]:
    """Validate, sort, and export records. Empty input yields valid empty outputs."""
    validated = [FinalAppResult.model_validate(record) for record in records]
    orders = [record.source_order for record in validated]
    if len(orders) != len(set(orders)):
        raise ValueError("source_order values must be unique")
    validated.sort(key=lambda record: record.source_order)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "apps.json"
    csv_path = output_dir / "apps.csv"
    json_path.write_text(
        json.dumps(
            [record.model_dump(mode="json") for record in validated],
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(_csv_row(record) for record in validated)
    return json_path, csv_path
