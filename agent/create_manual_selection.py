# ruff: noqa: E501
"""Create the requested stratified manual-audit selection from local records."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SELECTED = [
    ("salesforce", "Evidence-finalized CRM baseline with OAuth and official MCP."),
    ("hubspot", "Evidence-finalized self-serve CRM-platform case with OAuth and API-key paths."),
    ("apify", "Evidence-finalized API-key data-platform case, contrasting with SaaS CRMs."),
    ("close", "Credential-path uncertainty with several authentication options and otherwise broad API evidence."),
    ("jira", "Workspace-admin credential requirement tests existing-customer access and admin gating."),
    ("otter-ai", "Contact-vendor and workspace-admin path tests a gated, unusual integration."),
    ("linear", "API evidence is fundamentally incomplete: authentication, API, read and write are all unresolved."),
    ("front", "API evidence is partial: read is present but write and breadth remain unverified."),
    ("shopify", "Marketplace-review path tests multi-tenant distribution and ecommerce access."),
    ("zoho-crm", "Official MCP edge case with OAuth and API evidence but unresolved breadth/access dimensions."),
]


def source_details(app_id: str) -> list[dict[str, Any]]:
    for folder in (ROOT / "data/final", ROOT / "data/researcher"):
        path = folder / f"{app_id}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("evidence", [])
    return []


def main() -> None:
    rows = {r["app_id"]: r for r in json.loads((ROOT / "data/final_dataset.json").read_text(encoding="utf-8"))["apps"]}
    selected: list[dict[str, Any]] = []
    for app_id, reason in SELECTED:
        row = rows[app_id]
        evidence = source_details(app_id)
        selected.append({
            "app_id": app_id,
            "app_name": row["name"],
            "category": row["category"],
            "current_verdict": row["buildability_verdict"],
            "confidence": row["confidence"],
            "review_status": row["review_status"],
            "authentication_methods": row["authentication"].get("methods", []),
            "credential_access": row["credential_access"],
            "documented_api": row["api_availability"].get("documented_public_api"),
            "read_operations": row["read_operations"],
            "write_operations": row["write_operations"],
            "api_breadth": row["api_breadth"],
            "mcp_status": row["mcp_status"].get("status"),
            "decisive_unresolved_fields": [x for x in row["unresolved_fields"] if any(k in x.lower() for k in ("credential", "authentication", "documented", "read", "write", "api_breadth", "buildability"))],
            "selection_reason": reason,
            "official_evidence": [{"title": e.get("page_title") or e.get("url", "").split("/")[2], "url": e.get("url")} for e in evidence if e.get("url")],
        })
    (ROOT / "evaluation/manual_audit_selection.json").write_text(json.dumps({"completed": False, "apps": selected}, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Manual audit selection", "", "| App | Category | Verdict | Confidence | Main audit focus | Why selected |", "|---|---|---|---|---|---|"]
    for r in selected:
        focus = ", ".join(r["decisive_unresolved_fields"]) or "validated decisive claims"
        lines.append(f"| {r['app_name']} | {r['category']} | {r['current_verdict']} | {r['confidence']} | {focus} | {r['selection_reason']} |")
    for r in selected:
        lines += ["", f"## {r['app_name']}", "", f"Current verdict: {r['current_verdict']}", f"Confidence: {r['confidence']}", f"Selection reason: {r['selection_reason']}", f"Primary audit focus: {', '.join(r['decisive_unresolved_fields']) or 'validated decisive claims'}", "", "### Claims to verify", "", "- [ ] Category and one-line description", "- [ ] Documented public API", "- [ ] Authentication methods", "- [ ] Read operations", "- [ ] Write operations", "- [ ] API breadth", "- [ ] Independent developer credential access", "- [ ] Existing-customer/admin access", "- [ ] Multi-tenant or partner access", "- [ ] MCP status", "- [ ] Final buildability verdict", "", "### Existing evidence", ""]
        if r["official_evidence"]:
            lines.extend(f"- {e['title']} — {e['url']}" for e in r["official_evidence"])
        else:
            lines.append("- No official evidence URL retained.")
        lines += ["", "### Manual findings", "", "Correct:", "Incorrect:", "Unclear:", "Missing evidence:", "", "### Corrections required", "", "### Notes", ""]
    (ROOT / "evaluation/manual_audit_selection.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
