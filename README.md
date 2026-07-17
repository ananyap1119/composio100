# composio100

The pipeline uses one evidence-grounded researcher with Composio direct tool execution for search and page retrieval. Deterministic validators check citations, source quality, contradictions, confidence, and unsupported claims. High-risk fields enter a human-review queue and are finalized through a manual audit.

A full independent verifier was tested during development but removed after incomplete retrieval produced false negatives. Final accuracy will be measured through a separate manual audit of 10 apps.

`provided_apps.csv` is immutable source data; `data/apps.csv` preserves every supplied value and adds stable IDs, nullable normalized domains, and calibration flags. The first 10 supplied apps are the calibration set.

## Commands

```bash
python -m agent.cli validate-inventory
python -m agent.cli validate-result path/to/result.json
python -m agent.cli research --app-id salesforce --resume-latest
python -m agent.cli apply-human-review --app-id salesforce --decisions data/reviewed/salesforce_human_decisions.json
python -m agent.cli export path/to/final-results.json
pytest
ruff check .
```

The Salesforce final record is `data/final/salesforce.json`; its manual audit is `evaluation/salesforce_manual_audit.json`.

## Case study package

100 applications were researched. Concrete verdicts were finalized only when all verdict-driving claims had validated official evidence. Remaining records were routed to review rather than promoted using unsupported assumptions.

The standalone case study is [`final_case_study.html`](final_case_study.html). The consolidated dataset is `data/final_dataset.json`; its reconciled counts are in `evaluation/final_dataset_summary.md` and the uncompleted 10-app audit packet is `evaluation/manual_audit_packet.md`.

The research pipeline uses Composio retrieval, OpenRouter extraction, tolerant Python normalization, evidence validation, verdict-specific finalization, and a human-review queue. Cached checkpoints, source-ID validation, bounded calls, and resumable runs are used throughout. Unknown means insufficient public evidence, not absence of support; model output is never treated as evidence.
