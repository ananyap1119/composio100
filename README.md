# Toolkit Readiness Research Agent

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
