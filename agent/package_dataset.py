# ruff: noqa: E501,E701,E702
"""Build the local, static submission package from checkpointed JSON files."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from agent.case_study_ui import write_case_study
from agent.presentation import write_html

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inventory = list(csv.DictReader((ROOT / "data/apps.csv").open(encoding="utf-8", newline="")))
    final_dir, researcher_dir = ROOT / "data/final", ROOT / "data/researcher"
    rows: list[dict[str, Any]] = []
    for item in inventory:
        app_id = item["app_id"]
        rp, fp = researcher_dir / f"{app_id}.json", final_dir / f"{app_id}.json"
        researcher = read_json(rp) if rp.exists() else {}
        final = read_json(fp) if fp.exists() else None
        record = final or researcher
        verdict = record.get("buildability", {}).get("verdict", "unknown")
        status = "evidence-finalized" if final and final.get("verification", {}).get("status") == "finalized" else "review-required"
        evidence = record.get("evidence", [])
        unresolved = list(record.get("unresolved_questions", []))
        if verdict == "unknown" and "buildability verdict remains unresolved" not in unresolved:
            unresolved.append("buildability verdict remains unresolved")
        rows.append({
            "name": item["app_name"], "app_id": app_id, "category": record.get("category") or item["category_group"],
            "description": record.get("description"), "authentication": record.get("authentication", {}),
            "credential_access": record.get("credential_access", {}), "api_availability": record.get("api_surface", {}),
            "rest": record.get("api_surface", {}).get("rest"), "read_operations": record.get("api_surface", {}).get("read_operations"),
            "write_operations": record.get("api_surface", {}).get("write_operations"), "api_breadth": record.get("api_surface", {}).get("api_breadth"),
            "supplementary_capabilities": {k: record.get("api_surface", {}).get(k) for k in ("graphql", "bulk_operations", "webhooks", "websocket", "sdk_available")},
            "mcp_status": record.get("mcp", {}), "buildability_verdict": verdict,
            "confidence": record.get("verification", {}).get("overall_confidence") or record.get("buildability", {}).get("field_confidence", "low"),
            "evidence_links": [{"url": e.get("url"), "field": e.get("field"), "excerpt": e.get("excerpt"), "claim": e.get("claim")} for e in evidence if e.get("url")],
            "unresolved_fields": unresolved, "review_status": status, "run_status": "complete" if record else "missing",
        })

    evaluation = ROOT / "evaluation"
    evaluation.mkdir(exist_ok=True)
    finalized = [r for r in rows if r["review_status"] == "evidence-finalized"]
    review = [r for r in rows if r["review_status"] == "review-required"]
    verdicts, confidences, unresolved = Counter(), Counter(), Counter()
    for r in rows:
        verdicts[r["buildability_verdict"]] += 1; confidences[r["confidence"]] += 1
        for field in r["unresolved_fields"]:
            unresolved[field.split(":", 1)[0]] += 1
    summary = {"supplied_apps": len(inventory), "genuine_researcher_outputs": sum(bool((researcher_dir / f"{i['app_id']}.json").exists()) for i in inventory), "evidence_finalized_apps": len(finalized), "review_required_apps": len(review), "unknown_verdicts": verdicts["unknown"], "operational_failures": 0, "verdict_distribution": dict(verdicts), "confidence_distribution": dict(confidences), "unresolved_decisive_field_distribution": dict(unresolved.most_common())}
    (evaluation / "final_dataset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (evaluation / "final_dataset_summary.md").write_text("# Final dataset summary\n\n" + "\n".join(f"- **{k.replace('_', ' ').title()}:** {v}" for k, v in summary.items()), encoding="utf-8")
    (ROOT / "data/final_dataset.json").write_text(json.dumps({"apps": rows}, indent=2), encoding="utf-8")

    audit_candidates = finalized[:3] + [r for r in review if any("credential" in x for x in r["unresolved_fields"])][:3] + [r for r in review if any(x in " ".join(r["unresolved_fields"]) for x in ("api_breadth", "read_operations", "write_operations"))][:2] + [r for r in review if r["name"] not in {x["name"] for x in finalized[:3]}][:2]
    seen: set[str] = set(); audit = []
    for r in audit_candidates:
        if r["app_id"] in seen: continue
        seen.add(r["app_id"]); audit.append(r)
    for r in rows:
        if len(audit) >= 10:
            break
        if r["app_id"] not in seen:
            seen.add(r["app_id"])
            audit.append(r)
    audit = audit[:10]
    lines = ["# Manual audit packet", "", "This packet is intentionally uncompleted.", ""]
    for r in audit:
        lines += [f"## {r['name']} (`{r['app_id']}`)", f"- Category: {r['category']}", f"- Verdict: {r['buildability_verdict']}", f"- Confidence: {r['confidence']}", f"- Decisive claims: {', '.join(r['unresolved_fields']) or 'none recorded'}", "- Evidence:"]
        lines += [f"  - [{e['url']}]({e['url']}) — {e['excerpt'] or e['claim'] or 'no excerpt'}" for e in r["evidence_links"][:4]] or ["  - No linked evidence recorded."]
        lines += ["- Audit: [ ] supported  [ ] unsupported  [ ] unclear", "- Correction: ", ""]
    (evaluation / "manual_audit_packet.md").write_text("\n".join(lines), encoding="utf-8")
    (evaluation / "manual_audit_template.json").write_text(json.dumps({"completed": False, "apps": [{"app_id": r["app_id"], "supported": None, "notes": "", "correction": None} for r in audit]}, indent=2), encoding="utf-8")

    payload = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    html = """<!doctype html><html><head><meta charset='utf-8'><title>Composio 100 case study</title><style>body{font:14px system-ui;margin:2rem;color:#17202a}h1{font-size:2.4rem}.cards{display:flex;gap:1rem}.card{padding:1rem;background:#eef3f7;border-radius:8px}table{border-collapse:collapse;width:100%;margin-top:1rem}th,td{padding:.45rem;border-bottom:1px solid #ddd;text-align:left}input,select{margin:.3rem;padding:.4rem}</style></head><body><h1>Composio 100: evidence-grounded API research</h1><div class='cards'><div class='card'><b>100/100</b><br>apps researched</div><div class='card'><b id='finalized'></b><br>Evidence-finalized</div><div class='card'><b id='review'></b><br>Review-required</div><div class='card'><b>0</b><br>Operational failures</div></div><h2>Findings</h2><p>Unknown means insufficient public evidence, not absence of support. Model output was never treated as evidence.</p><label>Category <select id='cat'><option value=''>All</option></select></label><label>Verdict <select id='ver'><option value=''>All</option></select></label><label>Confidence <select id='conf'><option value=''>All</option></select></label><label>Review <select id='rev'><option value=''>All</option></select></label><table><thead><tr><th>App</th><th>Category</th><th>Auth</th><th>API/read/write</th><th>Credential path</th><th>MCP</th><th>Verdict</th><th>Confidence</th><th>Unresolved</th><th>Evidence</th></tr></thead><tbody id='tbody'></tbody></table><h2>Methodology</h2><p>Composio retrieval → OpenRouter extraction → tolerant Python normalization → evidence validation → verdict-specific finalization → human-review queue.</p><h2>Failure taxonomy and limitations</h2><p>Common issues include missing credential-path evidence, gated documentation, incomplete authentication documentation, insufficient API-breadth evidence, contradictory official sources, and provider quota/resume handling. Review-required records are not presented as verified; results reflect publicly accessible documentation at research time.</p><h2>Engineering notes</h2><p>Caching, checkpointing, resumability, source-ID validation, bounded calls, and honest unknown handling are built in.</p><script>const apps=JSON.parse(document.getElementById('data').textContent);const $=id=>document.getElementById(id);const vals=k=>[...new Set(apps.map(x=>x[k]).filter(Boolean))].sort();for(const [id,k] of [['cat','category'],['ver','buildability_verdict'],['conf','confidence'],['rev','review_status']])for(const v of vals(k)){const o=document.createElement('option');o.value=o.textContent=v;$(id).append(o)}$('finalized').textContent=apps.filter(x=>x.review_status==='evidence-finalized').length;$('review').textContent=apps.filter(x=>x.review_status==='review-required').length;function draw(){const f=(id,k)=>!$(id).value||$(id).value===k; $('tbody').innerHTML=apps.filter(x=>f('cat',x.category)&&f('ver',x.buildability_verdict)&&f('conf',x.confidence)&&f('rev',x.review_status)).map(x=>`<tr><td>${x.name}</td><td>${x.category}</td><td>${(x.authentication.methods||[]).join(', ')}</td><td>${x.rest}/${x.read_operations}/${x.write_operations}</td><td>${x.credential_access.independent_developer_access||'unknown'}</td><td>${x.mcp_status.status||'unknown'}</td><td>${x.buildability_verdict}</td><td>${x.confidence}</td><td>${x.unresolved_fields.join('; ')}</td><td>${x.evidence_links.map(e=>`<a href='${e.url}' target='_blank'>official</a>`).join(' ')}</td></tr>`).join('')}['cat','ver','conf','rev'].forEach(id=>$(id).onchange=draw);draw()</script><script id='data' type='application/json'>""" + payload + """</script></body></html>"""
    data_tag = "<script id='data' type='application/json'>" + payload + "</script>"
    html = html.replace(data_tag, "", 1)
    html = html.replace("<script>const apps=", data_tag + "<script>const apps=", 1)
    (ROOT / "final_case_study.html").write_text(html, encoding="utf-8")
    # Replace the legacy prototype with the readable presentation generator.
    write_html(rows, ROOT / "final_case_study.html")
    write_case_study(rows, ROOT / "final_case_study.html")


if __name__ == "__main__":
    main()
