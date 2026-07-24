# Atlas — API Readiness Index

Atlas is a single-page product-ops case study that evaluates the authentication,
access model, API surface, MCP availability, and agent buildability of 100 apps
across 10 categories.

Live product: https://atlas-api-readiness.ananyap1119.chatgpt.site

## What is included

- A searchable and filterable 100-app findings matrix.
- App-specific descriptions, authentication, access nuance, API breadth, MCP
  signal, buildability verdict, blocker, and a first-party evidence trail.
- Quantified category and portfolio-level patterns.
- A transparent research agent that replays the first-party sources for all 100
  rows and routes conflicts or low-confidence pages to a human.
- A seven-app, risk-weighted verification sample with five first-pass hits and
  two documented corrections.
- Downloadable research data, verification data, interview Q&A, and a
  line-by-line assignment audit.

## Run the product

Prerequisites: Node.js 22.13 or newer.

```bash
npm install
npm run dev
```

Then open the local URL printed by the development server.

Production validation:

```bash
npm run lint
npm test
```

`npm test` creates the production build before checking its server-rendered HTML
and all required research artifacts.

## Run the research agent

The default command checks all 100 rows in `public/research-set.json`:

```bash
node public/research-agent.mjs > research-output.json
```

Useful controls:

```bash
node public/research-agent.mjs --limit 10 --concurrency 4 --timeout 15000
node public/research-agent.mjs --input another-set.json > results.json
```

The input is an array of objects with these fields:

```json
{
  "id": 61,
  "name": "GitHub",
  "category": "Developer & Infra",
  "description": "Code collaboration platform for repositories, issues, pull requests, Actions, and security.",
  "auth": "OAuth 2.0 / token",
  "access": "Self-serve",
  "surface": "Broad REST + GraphQL",
  "mcp": true,
  "verdict": "Ready",
  "blocker": "—",
  "evidence": "https://docs.github.com/en/rest"
}
```

The output records source reachability, observed auth/access/surface signals,
short source excerpts, conflicts with the curated claim, confidence, and whether
human review is required. The agent does not claim to execute protected
endpoints and does not invent evidence when a page cannot be read.

## Research workflow

1. **Define the rubric.** Ready means a documented callable surface plus
   developer-obtainable credentials. Constrained means the surface exists but a
   plan, review, tenant admin, license, or partnership is required. Blocked means
   no usable public callable surface was found.
2. **Discover first-party evidence.** Each row has a first-party documentation or
   vendor source.
3. **Extract and normalize.** The script searches the source text for explicit
   authentication, access, and interface signals.
4. **Challenge the claim.** Observed signals are compared with the curated row;
   contradictions and weak evidence are queued for review.
5. **Verify high-risk rows.** A browser replay and human reading check gated,
   ambiguous, and time-sensitive claims.
6. **Record corrections.** Google Ads moved from self-serve to gated because a
   developer token is reviewed. NotebookLM moved from blocked to constrained
   because an Enterprise API now exists in preview behind license and IAM gates.

The first pass got five of seven sampled rows correct (71%). After the two
corrections, that same sample was seven of seven. This is not a claim that all
100 rows have 100% accuracy.

## Agent versus human

The agent fetches pages, extracts transparent signals, compares claims, scores
confidence, and queues uncertain rows. The human owns the rubric, interprets
commercial and policy nuance, checks dynamic or inaccessible documentation, and
approves corrections. Paid accounts are intentionally unnecessary: a
payment/approval gate is itself a finding.

## Files

- `app/page.tsx` — the complete interactive case study.
- `app/globals.css` — minimal Composio-inspired visual system.
- `public/research-set.json` — normalized 100-app input.
- `public/research-agent.mjs` — reproducible source-check agent.
- `public/verification-sample.json` — seven verified claims and outcomes.
- `public/interview-questionnaire.md` — interview preparation with precise answers.
- `public/assignment-compliance-audit.md` — requirement-by-requirement audit.
- `tests/rendered-html.test.mjs` — production-render and artifact checks.

## Known limitations

- The seven-row verification sample is risk-weighted, not statistically
  representative of the whole set.
- Documentation and access policies change; evidence should be date-stamped and
  periodically replayed.
- Regex-based extraction can miss JavaScript-rendered, vague, regional, or
  context-dependent documentation.
- MCP means that a documented MCP surface was found; the matrix does not imply
  that every server is first-party or equally production-ready.
- Public documentation can prove the credential path and surface, but not a
  protected call without an account. The site reports this distinction.
