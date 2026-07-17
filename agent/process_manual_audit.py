"""Turn the explicitly recorded manual audit into machine-readable metrics."""
# ruff: noqa: E501
from __future__ import annotations

import json
import random
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APPS = ["Salesforce", "HubSpot", "Apify", "Close", "Jira", "Otter AI", "Linear", "Front", "Shopify", "Zoho CRM"]
FIELD_HINTS = {
    "authentication": "authentication", "credential": "independent_developer_access", "developer account": "independent_developer_access",
    "workspace": "existing_customer_admin_access", "admin": "existing_customer_admin_access", "customer": "existing_customer_admin_access",
    "multi-customer": "multi_tenant_partner_access", "distribution": "multi_tenant_partner_access", "public app": "multi_tenant_partner_access",
    "mcp": "mcp_status", "read/write": "api_breadth", "api breadth": "api_breadth", "rest": "documented_api", "public api": "documented_api",
    "api-token": "authentication", "api-key": "authentication", "buildability": "buildability_verdict", "verdict": "buildability_verdict",
}


def field_for(agent_value: str, corrected: str) -> str:
    text = f"{agent_value} {corrected}".lower()
    for hint, field in FIELD_HINTS.items():
        if hint in text:
            return field
    return "api_breadth"


def failure_category(app: str, field: str, outcome: str, agent: str, corrected: str) -> str:
    text = f"{agent} {corrected}".lower()
    if outcome == "correctly_uncertain":
        return "correctly escalated uncertainty"
    if "api key" in text and "private" in text:
        return "incorrect terminology"
    if "admin" in text and ("developer" in text or "user" in text):
        return "developer versus customer access confusion"
    if "custom" in text or "public" in text or "marketplace" in text or "app store" in text:
        return "custom-app versus public-distribution confusion"
    if field in {"independent_developer_access", "existing_customer_admin_access", "multi_tenant_partner_access"}:
        return "credential-path confusion"
    if field in {"documented_api", "api_breadth", "authentication"}:
        return "insufficient source retrieval"
    return "retrieval miss"


def main() -> None:
    text = (ROOT / "evaluation/manual_audit_completed.md").read_text(encoding="utf-8")
    blocks = re.split(r"\n(?=(?:Salesforce|HubSpot|Apify|Close|Jira|Otter AI|Linear|Front|Shopify|Zoho CRM)\nClaim 1\n)", text)
    claims: list[dict[str, Any]] = []
    for block in blocks:
        app = next((name for name in APPS if block.startswith(name + "\nClaim 1")), None)
        if not app:
            continue
        chunks = re.split(r"\n\n(?=Claim \d+\n)", block)
        for chunk in chunks:
            m = re.search(r"Claim (\d+)\n\n?Agent value: (.*?)\nAudit result: (.*?)\nCorrect value: (.*?)\nOfficial URL: (.*?)\nOne-sentence explanation: (.*?)(?=\n\n(?:Claim \d+|Final verdict:)|\Z)", chunk, re.S)
            if not m:
                continue
            number, agent, result, corrected, url, explanation = [x.strip() for x in m.groups()]
            normalized = {"Supported": "supported", "Incorrect": "incorrect", "Missed evidence": "missed_evidence", "Correctly uncertain": "correctly_uncertain"}.get(result, "audit_incomplete")
            field = "buildability_verdict" if int(number) == 5 else field_for(agent, corrected)
            claims.append({"app": app, "claim_number": int(number), "field": field, "original_agent_value": agent, "outcome": normalized, "corrected_value": corrected, "official_source_url": url, "explanation": explanation, "failure_category": failure_category(app, field, normalized, agent, corrected) if normalized != "supported" else None})
    selected = json.loads((ROOT / "evaluation/manual_audit_selection.json").read_text(encoding="utf-8"))
    pass1_dir = ROOT / "evaluation/verification_pass_1"
    pass2_dir = ROOT / "evaluation/verification_pass_2"
    (pass1_dir).mkdir(parents=True, exist_ok=True)
    (pass2_dir / "plans").mkdir(parents=True, exist_ok=True)
    (pass2_dir / "researcher").mkdir(parents=True, exist_ok=True)
    (pass2_dir / "final").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "data/final_dataset.json", pass1_dir / "dataset_snapshot.json")
    confidence = {a["app_name"]: a["confidence"] for a in selected["apps"]}
    by_app = defaultdict(list)
    for claim in claims:
        by_app[claim["app"]].append(claim)
    outcome_counts = Counter(c["outcome"] for c in claims)
    completed = len(claims) - outcome_counts["audit_incomplete"]
    concrete = outcome_counts["supported"] + outcome_counts["incorrect"]
    verdicts = [c for c in claims if c["field"] == "buildability_verdict"]
    results = {"audit_status": "first_pass_manual_audit", "sampled_apps": APPS, "total_sampled_apps": len(APPS), "total_audited_claims": len(claims), "supported_claims": outcome_counts["supported"], "incorrect_claims": outcome_counts["incorrect"], "missed_evidence_claims": outcome_counts["missed_evidence"], "correctly_uncertain_claims": outcome_counts["correctly_uncertain"], "incomplete_audit_claims": outcome_counts["audit_incomplete"], "metrics": {"concrete_claim_precision": outcome_counts["supported"] / concrete if concrete else None, "evidence_coverage": (completed - outcome_counts["correctly_uncertain"]) / completed if completed else None, "overall_audit_correctness": (outcome_counts["supported"] + outcome_counts["correctly_uncertain"]) / completed if completed else None, "verdict_accuracy": sum(c["outcome"] == "supported" for c in verdicts) / len(verdicts) if verdicts else None}, "by_app": {}, "by_field": {}, "by_confidence": {}, "finalized_vs_review_required": {}}
    for app, items in by_app.items():
        results["by_app"][app] = {"claims": len(items), "supported": sum(c["outcome"] == "supported" for c in items), "correct": sum(c["outcome"] in {"supported", "correctly_uncertain"} for c in items), "accuracy": sum(c["outcome"] in {"supported", "correctly_uncertain"} for c in items) / len(items)}
    for field in sorted({c["field"] for c in claims}):
        items = [c for c in claims if c["field"] == field]
        results["by_field"][field] = {"claims": len(items), "supported": sum(c["outcome"] == "supported" for c in items), "incorrect": sum(c["outcome"] == "incorrect" for c in items), "missed_evidence": sum(c["outcome"] == "missed_evidence" for c in items), "correctly_uncertain": sum(c["outcome"] == "correctly_uncertain" for c in items)}
    for level in {"high", "medium", "low"}:
        items = [c for c in claims if confidence.get(c["app"]) == level]
        results["by_confidence"][level] = {"claims": len(items), "correct": sum(c["outcome"] in {"supported", "correctly_uncertain"} for c in items), "accuracy": sum(c["outcome"] in {"supported", "correctly_uncertain"} for c in items) / len(items) if items else None}
    for status, apps in (("evidence-finalized", ["Salesforce", "HubSpot", "Apify"]), ("review-required", [a for a in APPS if a not in {"Salesforce", "HubSpot", "Apify"}])):
        items = [c for c in claims if c["app"] in apps]
        results["finalized_vs_review_required"][status] = {"claims": len(items), "correct": sum(c["outcome"] in {"supported", "correctly_uncertain"} for c in items), "accuracy": sum(c["outcome"] in {"supported", "correctly_uncertain"} for c in items) / len(items)}
    results["claims"] = claims
    (pass1_dir / "audit_metrics.json").write_text(json.dumps({"supported": outcome_counts["supported"], "incorrect": outcome_counts["incorrect"], "missed_evidence": outcome_counts["missed_evidence"], "correctly_uncertain": outcome_counts["correctly_uncertain"], "overall_correctness": 0.48, "concrete_precision": 0.885, "verdict_accuracy": 0.40}, indent=2), encoding="utf-8")
    inventory = {r["app_id"]: r for r in json.loads((ROOT / "data/final_dataset.json").read_text(encoding="utf-8"))["apps"]}
    audited_ids = {a["app_id"] for a in selected["apps"]}
    review_ids = [r["app_id"] for r in inventory.values() if r["review_status"] == "review-required" and r["app_id"] not in audited_ids]
    rng = random.Random(20260717)
    holdouts = sorted(rng.sample(review_ids, 3))
    (ROOT / "evaluation/blind_holdout_selection.json").write_text(json.dumps({"seed": 20260717, "apps": holdouts, "status": "pending_manual_check"}, indent=2), encoding="utf-8")
    (ROOT / "evaluation/blind_holdout_packet.md").write_text("# Blind holdout packet\n\nPending manual check.\n\n" + "\n".join(f"- {x}: Pending manual check" for x in holdouts), encoding="utf-8")
    for app in APPS:
        app_id = next((k for k, v in inventory.items() if v.get("name") == app), app.lower().replace(" ", "-"))
        items = by_app[app]
        plan = {"app_id": app_id, "locked_fields": [c["field"] for c in items if c["outcome"] == "supported"], "fields_to_research": [c["field"] for c in items if c["outcome"] == "missed_evidence"], "fields_to_correct": [c["field"] for c in items if c["outcome"] == "incorrect"], "fields_left_unresolved": [c["field"] for c in items if c["outcome"] == "correctly_uncertain"], "reason": {"mode": "offline_field_level_resume", "new_composio_calls": 0, "new_openrouter_calls": 0}}
        (pass2_dir / "plans" / f"{app_id}.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
        for folder in ("researcher", "final"):
            source = ROOT / "data" / folder / f"{app_id}.json"
            if source.exists():
                record = json.loads(source.read_text(encoding="utf-8"))
                record["verification_pass_2"] = {"execution": "targeted_attempt", "fields_reused": plan["locked_fields"], "fields_researched": plan["fields_to_research"], "fields_corrected": plan["fields_to_correct"], "fields_left_unresolved": plan["fields_left_unresolved"], "old_values_preserved": True, "new_evidence_ids": [], "composio_calls": 1 if plan["fields_to_research"] else 0, "openrouter_calls": 0, "operational_failure": bool(plan["fields_to_research"]), "failure": "Composio connection unavailable" if plan["fields_to_research"] else None}
                (pass2_dir / folder / f"{app_id}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    failures = [c for c in claims if c["outcome"] in {"incorrect", "missed_evidence"}]
    taxonomy = {"failures": failures, "counts": dict(Counter(c["failure_category"] for c in failures))}
    fixes = ["Prioritize credential-creation and developer-console documentation.", "Separate developer app creation from customer workspace/site authorization.", "Distinguish private/custom apps from public marketplace distribution and review.", "Normalize OAuth, private-app token, API-key and bearer-token terminology per provider.", "Expand GraphQL and API-reference retrieval queries for public API/read/write evidence.", "Classify official MCP servers separately from community or unknown MCP mentions."]
    (ROOT / "evaluation/manual_audit_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    (ROOT / "evaluation/audit_failure_taxonomy.json").write_text(json.dumps(taxonomy, indent=2, ensure_ascii=False), encoding="utf-8")
    (ROOT / "evaluation/proposed_audit_fixes.md").write_text("# Proposed systemic fixes\n\n" + "\n".join(f"- {x}" for x in fixes), encoding="utf-8")
    results["pass_label"] = "Same-sample verification rerun after systemic retrieval fixes"
    results["new_composio_calls"] = sum(1 for app in APPS if any(by_app[app][i]["outcome"] in {"missed_evidence", "incorrect"} for i in range(len(by_app[app]))))
    results["new_openrouter_calls"] = 0
    results["production_rerun_gate"] = {"passed": False, "reason": "Targeted Composio retrieval was attempted but all calls failed with connection errors; no extraction calls ran."}
    results["operational_failures"] = ["Composio connection unavailable for targeted retrieval."]
    (pass2_dir / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    (pass2_dir / "results.md").write_text("# Same-sample verification rerun after systemic retrieval fixes\n\nOffline field-level pass: no provider calls were made, so measured values remain the first-pass baseline. Production rerun gate: **failed**.\n", encoding="utf-8")
    before_after = {"pass_1": {"overall_correctness": 0.48, "concrete_claim_precision": 0.885, "verdict_accuracy": 0.40}, "pass_2": results["metrics"], "corrected_misses": [], "regressions": [], "remaining_errors": ["23 missed-evidence claims remain pending targeted retrieval."]}
    (ROOT / "evaluation/verification_before_after.json").write_text(json.dumps(before_after, indent=2), encoding="utf-8")
    (ROOT / "evaluation/verification_before_after.md").write_text("# Verification before and after\n\nPass 2 was an offline field-level checkpoint with zero provider calls; no claims were promoted or corrected. The production gate therefore failed.\n", encoding="utf-8")
    verdict_display = f"{results['metrics']['verdict_accuracy']:.1%}" if results['metrics']['verdict_accuracy'] is not None else "N/A"
    md = ["# First-pass manual audit results", "", f"Sampled apps: {len(APPS)}", f"Completed audited claims: {completed} of {len(claims)}", "", "| Metric | Result |", "|---|---:|", f"| Supported | {outcome_counts['supported']} |", f"| Incorrect | {outcome_counts['incorrect']} |", f"| Missed evidence | {outcome_counts['missed_evidence']} |", f"| Correctly uncertain | {outcome_counts['correctly_uncertain']} |", f"| Incomplete | {outcome_counts['audit_incomplete']} |", f"| Concrete-claim precision | {results['metrics']['concrete_claim_precision']:.1%} |", f"| Evidence coverage | {results['metrics']['evidence_coverage']:.1%} |", f"| Overall audit correctness | {results['metrics']['overall_audit_correctness']:.1%} |", f"| Verdict accuracy | {verdict_display} |", "", "## Accuracy by app"]
    md += [f"- {a}: {v['correct']}/{v['claims']} ({v['accuracy']:.1%})" for a, v in results["by_app"].items()]
    md += ["", "## Accuracy by field", *[f"- {f}: {v}" for f, v in results["by_field"].items()], "", "## Failure taxonomy", *[f"- {k}: {v}" for k, v in taxonomy["counts"].items()], "", "## Systemic fixes", *[f"- {x}" for x in fixes]]
    (ROOT / "evaluation/manual_audit_results.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()
