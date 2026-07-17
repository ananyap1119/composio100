"""Create a presentation-only human verification overlay."""
# ruff: noqa: E501
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERDICTS = {
    "Salesforce": "Build now; customer-admin policy caveat",
    "HubSpot": "Build now; use OAuth or private/static access tokens",
    "Apify": "Build now",
    "Close": "Customer-specific build now; public distribution requires Close approval",
    "Jira": "Build now; customer site-admin authorization required",
    "Otter AI": "Enterprise-customer build; public multi-customer distribution remains unresolved",
    "Linear": "Build now",
    "Front": "Customer-specific build now; public distribution requires Front publishing approval",
    "Shopify": "Build after Shopify App Store review for public distribution",
    "Zoho CRM": "Build now",
}
DISPLAY = {
    "Salesforce": ("OAuth 2.0", "Broad REST read/write", "Build now", "OAuth app; customer policy may require admin approval", "Build now"),
    "HubSpot": ("OAuth 2.0 and private/static access token", "Broad REST read/write", "Build now", "OAuth", "Build now"),
    "Apify": ("API token", "REST read/write", "Build now", "Self-serve token-based integration", "Build now"),
    "Close": ("API key and OAuth 2.0", "Broad REST read/write", "Build now", "Close approval required", "Public distribution requires vendor approval"),
    "Jira": ("OAuth 2.0 3LO and API token", "REST read/write", "Build now", "OAuth sharing available", "Build now with customer-admin authorization"),
    "Otter AI": ("Bearer API key", "Broad read with limited write", "Enterprise customer credentials", "Not publicly established", "Enterprise-customer build; public distribution remains uncertain"),
    "Linear": ("OAuth 2.0 and personal API key", "Public GraphQL with queries and mutations", "Build now", "OAuth app", "Build now"),
    "Front": ("OAuth 2.0 and company API token", "Core API with read/write/send operations", "Build now with admin-created credentials", "Front publishing approval required", "Public distribution requires vendor approval"),
    "Shopify": ("OAuth 2.0", "GraphQL Admin API for new public apps", "Custom-app path", "Shopify App Store review required", "Build after marketplace review"),
    "Zoho CRM": ("OAuth 2.0", "Broad REST CRUD, bulk, metadata and related APIs", "Build now", "OAuth through API Console", "Build now"),
}


def main() -> None:
    dataset = {r["name"]: r for r in json.loads((ROOT / "data/final_dataset.json").read_text(encoding="utf-8"))["apps"]}
    audit = json.loads((ROOT / "evaluation/manual_audit_results.json").read_text(encoding="utf-8"))
    grouped = {}
    for claim in audit["claims"]:
        grouped.setdefault(claim["app"], []).append({"field": claim["field"], "original_agent_value": claim["original_agent_value"], "human_audited_value": claim["corrected_value"], "audit_outcome": claim["outcome"], "official_evidence_url": claim["official_source_url"], "explanation": claim["explanation"]})
    apps = []
    for name, verdict in VERDICTS.items():
        row = dataset[name]
        authentication, api, customer, public, decision = DISPLAY[name]
        apps.append({"app_name": name, "original_agent_value": {"verdict": row["buildability_verdict"], "confidence": row["confidence"]}, "human_audited_value": grouped.get(name, []), "audit_outcome": [c["audit_outcome"] for c in grouped.get(name, [])], "official_evidence_urls": sorted({c["official_evidence_url"] for c in grouped.get(name, [])}), "concise_explanation": "Manual official-documentation audit; see claim-level explanations.", "original_verdict": row["buildability_verdict"], "human_verified_scoped_verdict": verdict, "review_status": row["review_status"], "provenance": "manual_official_documentation_audit", "display_authentication": authentication, "display_api": api, "display_customer_path": customer, "display_public_path": public, "display_decision": decision})
    (ROOT / "evaluation/human_verified_overlay.json").write_text(json.dumps({"provenance": "manual_official_documentation_audit", "apps": apps}, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
