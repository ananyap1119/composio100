# Atlas interview questionnaire

Use these answers as a compact defense of the work. Keep the distinction between
the automated first pass and human verification explicit.

## Product and approach

### 1. Give me the one-minute walkthrough.

Atlas turns a 100-app integration brief into a decision surface. The matrix shows
what each app does, authentication, whether credentials are truly self-serve,
API breadth, MCP availability, a buildability verdict, the blocker, and a
first-party source. Above it, I summarize portfolio patterns. Below it, I show
the agent workflow and a verification sample that records both hits and misses.

### 2. What problem does this solve for Composio?

It separates apps that an integration team can begin building now from apps that
need plan access, administrator setup, app review, a partnership, or further
research. That prevents engineering time from being spent before the credential
and policy path is understood.

### 3. Why did you build a product rather than submit a spreadsheet?

The brief asks for a self-explanatory HTML artifact that an agent and a human can
consume. The page keeps the scan path fast for a reviewer while the JSON,
downloadable agent, evidence links, and source snapshot preserve machine
readability and reproducibility.

### 4. How did you keep the scope controlled?

I used one normalized schema, one matrix, four aggregate findings, one
verification table, and one runnable script. I did not build authentication,
paid-account tests, or a backend because those would not improve the requested
decision.

### 5. What is the data model?

Each row contains `id`, `name`, `category`, `description`, `auth`, `access`,
`surface`, `mcp`, `verdict`, `blocker`, and `evidence`. The same 100-row dataset
is downloadable and is the default input to the research agent.

## Classification decisions

### 6. What does “Ready” mean?

There is a documented callable surface and a developer can obtain the required
credentials without a commercial or policy approval blocking initial work.
Production review can still exist; the decisive question is whether meaningful
integration work can start.

### 7. What does “Constrained” mean?

The surface exists, but a paid plan, app review, tenant administrator, license,
partnership, narrow interface, or deployment-specific setup limits access or
scope. It is buildable conditionally, not a dead end.

### 8. What does “Blocked” mean?

I found no usable general public callable surface for the requested integration,
or the only path is effectively unavailable without a private program. “Blocked”
is evidence about current access, not a permanent claim about the company.

### 9. How did you define self-serve versus gated?

Self-serve means a developer can create an app or credential through public
onboarding. Gated means a human approval, partnership, enterprise license,
customer/admin action, or invite-only documentation is required. A public docs
page alone does not make access self-serve.

### 10. What counts as a broad API surface?

A surface is broad when it covers several core product objects and workflows,
such as records plus search, events, administration, or mutations. “Narrow”
means a limited operation set, export-only path, or CLI-only interface.

### 11. How did you classify MCP?

I marked MCP when a documented MCP server or meaningful MCP-compatible surface
was found. I would add an `mcp_provenance` field in production to distinguish
first-party, community, and aggregator-hosted servers; the current boolean does
not imply equal support quality.

### 12. Which authentication pattern dominates?

OAuth 2.0 dominates because most multi-user SaaS integrations need delegated,
scoped authorization. API keys and tokens remain common in developer tools,
data providers, and single-workspace services.

### 13. What is the most common blocker?

Approval is the recurring blocker: developer-token reviews, partner programs,
business verification, OAuth approval, tenant administrators, and enterprise
licenses. The engineering surface often exists before the organization is
permitted to use it.

### 14. Which categories are easiest?

Developer infrastructure and productivity are the clearest near-term wins
because their APIs and credential flows are usually public and designed for
third-party builders. Advertising, enterprise finance/data, and some AI products
need more outreach or commercial access.

## Agent and pipeline

### 15. What exactly does the agent do?

It reads all 100 normalized rows, fetches each first-party evidence page with
bounded concurrency and a timeout, removes markup, extracts explicit auth,
access, and surface signals, stores short evidence excerpts, compares observed
signals with the curated claim, scores confidence, and routes conflicts or
failed fetches to human review.

### 16. Why use a script instead of manually researching 100 rows?

A script makes coverage, timeouts, output shape, and challenge rules repeatable.
Manual reading is still necessary for policy nuance, but it is focused on the
uncertain rows instead of being the only control across the whole set.

### 17. Why is the classifier transparent and regex-based?

For this take-home, inspectability matters more than an opaque model call. A
reviewer can see every signal and rerun it without credentials. In production I
would combine deterministic extraction with structured model output, page
snapshots, and an evaluation set.

### 18. What happens when a page cannot be fetched?

The agent records the failure, assigns zero confidence, and sends the row to
human review. It does not convert network failure into “no API” and does not
invent an endpoint result.

### 19. Where is a human required?

The human defines the rubric, resolves contradictory language, checks
JavaScript-rendered or inaccessible docs in a browser, distinguishes production
approval from initial self-service, judges community MCP provenance, and approves
every correction.

### 20. Did you call protected APIs?

No. That would require accounts, credentials, and possibly paid plans that the
brief explicitly says are unnecessary. I verified public credential paths,
surface documentation, and access policy. Any commercial or approval gate is
reported as a result.

### 21. How would you use Composio’s SDK in a production version?

I would use Composio for authenticated tool execution and connection lifecycle
tests after a source is classified as buildable. The current artifact deliberately
keeps public-source discovery credential-free; a production loop would add a
Composio-backed smoke test for allowed accounts and compare real tool schemas
against the documented surface.

### 22. What does the agent output?

It outputs schema version, timestamp, rubric, run summary, and a result per app:
source status, HTTP status, observed signals, excerpts, conflicts, confidence,
and the human-review flag. This makes failures auditable rather than hiding them
inside a score.

## Verification and accuracy

### 23. How did you choose the seven-app verification sample?

It is risk-weighted: familiar self-serve platforms establish the baseline, while
advertising and emerging AI products stress the gated/blocked boundary. It tests
the claims most likely to change or be misclassified.

### 24. Why only seven?

The assignment is time-bounded. Seven deep checks allowed a real correction loop
within scope. It is not statistically representative, so I say that plainly and
would expand verification to every gated and blocked row first.

### 25. How did you calculate 71%?

Five of seven sampled claims survived the first source replay unchanged:
`5 / 7 = 71.4%`, displayed as 71%. Two failed and were corrected.

### 26. Can you claim 100% accuracy?

Only for the same seven-row sample after correction: seven of seven then matched
the reviewed official sources. I do not claim 100% accuracy for the complete
100-app matrix.

### 27. What was wrong about Google Ads?

The first pass treated visible docs and an OAuth path as self-serve. Official
policy shows that usable API access depends on a developer token and access-level
review, so I changed it to gated and constrained.

### 28. What was wrong about NotebookLM?

The first pass said there was no callable API. Current Google Cloud documentation
shows preview NotebookLM Enterprise notebook-management APIs. The correct result
is constrained because an Enterprise license and IAM setup gate the surface.

### 29. What is the verification loop?

The agent challenges claims against page text. A browser replay checks the exact
official page and dynamic context. A human then decides whether the rubric or row
should change and records the miss rather than overwriting the history.

### 30. What are likely false positives?

OAuth mentioned only for login, a docs site with no credential-creation path, an
unofficial MCP server, or a marketing page that says “API” without exposing
general endpoints. These are why signal detection is not the final verdict.

### 31. What are likely false negatives?

JavaScript-rendered docs, tenant-only references, regional documentation,
recently launched preview APIs, and surfaces described as CLI or webhooks rather
than “REST.” NotebookLM demonstrated this risk.

### 32. How do you handle changing documentation?

Each run records a timestamp and source URL. Production should also archive
content hashes or permitted snapshots, diff new runs, and automatically reopen
rows when access language or endpoints change.

## Tradeoffs and next steps

### 33. What is the largest limitation?

Evidence coverage is broad, but deep human verification is a seven-row sample.
The next quality investment is not more UI; it is verified snapshots for all
gated and blocked rows, followed by a stratified sample of ready rows.

### 34. What would you do with another eight hours?

I would browser-replay every constrained and blocked row, add evidence timestamps
and quoted snippets per row, separate official from community MCP provenance,
create regression fixtures for the classifier, and run credentialed smoke tests
only for accounts legitimately available.

### 35. Why should the reviewer trust this result?

Because the artifact exposes its rubric, all 100 source trails, the runnable
agent, the exact verification set, the misses, the corrections, and the
limitations. Trust comes from reproducibility and visible uncertainty, not from
claiming the first pass was perfect.
