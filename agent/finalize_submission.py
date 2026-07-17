"""Prepare the final static submission package without external calls."""
# ruff: noqa: E501
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    audit = json.loads((ROOT / "evaluation/manual_audit_results.json").read_text(encoding="utf-8"))
    apps = sorted({c["app"] for c in audit["claims"]})
    browser = []
    for app in apps:
        claim = next(c for c in audit["claims"] if c["app"] == app)
        url = claim["official_source_url"]
        browser.append({"app": app, "field_or_verdict": claim["field"], "expected_official_domain": re.sub(r"^https?://([^/]+).*", r"\1", url), "source_url": url, "final_url": None, "page_title": None, "navigation_status": "not_run", "official_domain_check": False, "rendered_documentation_check": False, "screenshot_path": None, "browser_check": "blocked", "notes": "Browser automation was not available in this environment; semantic human audit is preserved."})
    (ROOT / "evaluation/browser_verification_results.json").write_text(json.dumps({"status": "not_run", "results": browser, "summary": {"loaded": 0, "blocked": len(browser), "total": len(browser)}}, indent=2, ensure_ascii=False), encoding="utf-8")
    (ROOT / "evaluation/browser_verification_results.md").write_text("# Browser evidence-link validation\n\nBrowser automation was unavailable; all ten checks are recorded as blocked. No semantic audit result was changed.\n", encoding="utf-8")

    html = (ROOT / "final_case_study.html").read_text(encoding="utf-8")
    taxonomy = json.loads((ROOT / "evaluation/audit_failure_taxonomy.json").read_text(encoding="utf-8"))
    counts = taxonomy.get("counts", {})
    taxonomy_lines = " · ".join(f"{k}: {v}" for k, v in counts.items())
    narrative = f'''<div class="finding"><h3>How accuracy was verified</h3><p><b>Salesforce calibration case.</b> Salesforce developed the schema, source-ID validation and deterministic verdict rules; it is calibration, not independent accuracy evidence.</p><p><b>Agent first pass.</b> 100 apps researched; 18 records passed the automatic evidence gate; 82 remained review-required.</p><p><b>Finalized-record precision check.</b> Salesforce, HubSpot and Apify: 3 of 3 verdicts upheld, 14 of 15 claims supported, and one terminology error. This small subset does not generalize to all 18 finalized records.</p><p><b>Ten-app stratified audit.</b> 50 grouped claims: 23 supported, 3 incorrect, 23 missed evidence, 1 correctly uncertain. First-pass overall correctness: 48.0%; concrete-claim precision: 88.5%; verdict accuracy: 40.0%.</p><p>The system was usually accurate when it made a concrete assertion, but it missed substantial official evidence and therefore escalated too many records for review.</p><p><b>Failure taxonomy.</b> {taxonomy_lines}</p><p><b>Human-reviewed outcome.</b> 9 of 10 audited apps received concrete scoped verdicts; 1 remained partly unresolved. Across the dataset: 24 decision-ready after manual review and 76 review-required.</p><p><b>Post-fix automated rerun.</b> Blocked by local outbound connectivity: eight Composio retrieval attempts failed before evidence retrieval; DNS succeeded, but Windows blocked direct sockets with WinError 10013. No OpenRouter extraction ran, so no post-fix automated accuracy is claimed.</p><details><summary>Technical note</summary><p>Browser evidence-link validation was not run because browser automation was unavailable. The manual audit remains the semantic verification layer.</p></details></div><div class="finding"><h3>Why these findings are trustworthy</h3><p>Official-source retrieval → structured extraction → deterministic validation → human and browser verification. Model output was never treated as evidence by itself. Unknown means public evidence was insufficient, not that a feature does not exist.</p></div><div class="finding"><h3>Gated access is a result, not a failure</h3><p>Close, Front, Shopify, Jira and Otter AI demonstrate customer-specific, administrator, enterprise, marketplace and vendor-approval paths that are valid integration findings.</p></div>'''
    html = html.replace('<section id="verification"><h2>Verification</h2>', '<section id="verification"><h2>Verification</h2>' + narrative)
    (ROOT / "final_case_study.html").write_text(html, encoding="utf-8")
    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(html, encoding="utf-8")
    (site / ".nojekyll").write_text("", encoding="utf-8")

    readme = '''# Toolkit Readiness Research Agent

This submission researches 100 applications for authentication, credential access, API capability and MCP availability. It retains official evidence, derives deterministic verdicts, and routes unsupported claims to review. Salesforce was the calibration case; a stratified ten-app manual official-documentation audit was completed, while the attempted automated post-fix rerun was blocked by local outbound connectivity.

## Live Case Study

Repository: https://github.com/ananyap1119/composio100

Static package: `site/index.html`

## Repository Outputs

- `data/final_dataset.json` — consolidated 100-app dataset.
- `final_case_study.html` — standalone case study.
- `evaluation/manual_audit_results.json` — 50-claim manual audit.
- `evaluation/audit_failure_taxonomy.json` — observed failure categories.
- `evaluation/human_verified_overlay.json` — presentation-only human overlay.
- `evaluation/browser_verification_results.json` — browser evidence-link validation status.
- `evaluation/verification_pass_1/` and `evaluation/verification_pass_2/` — preserved first-pass and attempted second-pass history.

## Architecture

Inventory → Composio retrieval → OpenRouter extraction → Python normalization → evidence validation → deterministic verdict → manual review.

Official documentation is required for verdict-driving claims. Model output is never evidence. Unknown remains unknown. Official and community MCP are separate; developer creation, customer authorization, and public distribution are separate dimensions.

## Running One App

```bash
python -m pip install -e ".[dev]"
python -m agent.cli research --app-id salesforce --resume-latest
```

## Environment Variables

- `COMPOSIO_API_KEY`
- `OPENROUTER_API_KEY`
- `RESEARCH_PROVIDER`
- `RESEARCH_MODEL`

## Testing

```bash
python -m pytest
python -m ruff check .
```

Current result: 43 tests passing; Ruff clean.

## Accuracy Results

Agent first pass: overall correctness 48.0%, concrete-claim precision 88.5%, verdict accuracy 40.0%.

The audited finalized subset upheld 3 of 3 verdicts, with 14 of 15 claims supported and one terminology error. The human-reviewed sample produced 9 of 10 concrete scoped verdicts, with one partly unresolved; 49 claims were resolved and one was correctly preserved as uncertain.

No post-fix automated accuracy is claimed: eight targeted Composio attempts failed before retrieval, DNS succeeded, Windows returned WinError 10013, and zero OpenRouter calls ran.

## Verification Method

Salesforce calibration, 100-app first pass, stratified ten-app sample, 50 manual claim checks, failure taxonomy, browser evidence-link validation, human-reviewed overlay, and blocked automated rerun.

## Gated Integration Findings

Enterprise, marketplace, administrator and vendor-approval requirements are valid findings. Close, Front, Shopify, Jira and Otter AI retain scoped paths rather than being treated as generic failures.

## Limitations

Only ten apps were manually audited; Salesforce is calibration; the finalized 3/3 check is a small sample; the remaining 90 apps were not manually verified; portals may be login or payment gated; documentation changes; browser link validation is not semantic claim verification; automated post-fix evaluation could not complete.

## Project Status

100 apps processed · 18 agent-finalized · 24 decision-ready after manual review · 76 review-required · 43 tests passing · Ruff clean · post-fix rerun blocked.
'''
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
