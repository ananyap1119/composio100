# Assignment compliance audit

This audit maps each assignment requirement to the final product. “Complete”
means the requirement is visible or runnable. “External dependency” means the
artifact is ready but completion depends on account access outside the product.

| Assignment line | Prior gap found in self-review | Final implementation | Status |
|---|---|---|---|
| Research 100 specified apps across 10 categories | All rows existed | Matrix and `research-set.json` contain exactly 100 apps in the requested 10 categories | Complete |
| Category and one-line explanation of what each app does | Descriptions were category-generic | Every row now has an app-specific one-line description | Complete |
| Authentication method | Present, but not reproducibly consumable | Auth is visible per row and included in the downloadable JSON/agent input | Complete |
| Self-serve versus gated, including nuance | Labels existed; nuance was easy to miss | Rows expose access and blocker; category summaries quantify self-serve availability | Complete |
| API surface breadth and existing MCP/skills | Present, but MCP meaning needed a caveat | Surface and MCP are visible; methodology states that MCP does not imply equal provenance or support quality | Complete |
| Buildability and biggest blocker | Per-row verdicts existed | Ready/Constrained/Blocked rubric is explicit; each row shows the blocker or the public credential path | Complete |
| Evidence for conclusions | Source links existed | All 100 rows expose a first-party documentation/vendor trail; seven high-risk claims have exact verification links | Complete |
| Patterns: dominant authentication | Present | Headline quantifies OAuth prevalence and explains why it dominates | Complete |
| Patterns: self-serve versus gated by category | Under-explained | Every category row shows ready and self-serve counts; matrix filters support inspection | Complete |
| Patterns: most common blocker | Not quantified clearly | Headline calls out recurring approval gates and shows the count | Complete |
| Patterns: easy wins versus outreach | Present but terse | Recommendation explicitly prioritizes developer/productivity apps and routes advertising, enterprise, and access-gated products to outreach | Complete |
| Use an agent/script/pipeline across all 100 apps | Earlier sample script did not default to 100 | `research-agent.mjs` defaults to all 100 rows, with bounded concurrency, timeouts, extraction, comparison, confidence, and review routing | Complete |
| Explain what the agent does | High-level only | On-page pipeline, ownership cards, README, and script source specify each automated step | Complete |
| Explain where a human is required | Browser/human ownership was implicit | On-page Agent/Human/No-paid-accounts cards and README assign explicit decision ownership | Complete |
| Verify a sample against real documentation | Sample result lacked row-level proof | Seven-row table links each exact official source and records five passes plus two corrections | Complete |
| Report what was right and wrong | Misses were summarized only | Google Ads and NotebookLM misses are named, explained, and corrected in the matrix | Complete |
| Use real verification loops, including agent, browser, other means, and human | Loop stages were not concrete enough | On-page loop separates agent challenge, browser replay, and human decision; structured sample is downloadable | Complete |
| Show how accuracy improved | A percentage could be misread | Product shows 5/7 first-pass, 71%, and 7/7 after correction, with an explicit warning that this is not 100% across all apps | Complete |
| One self-explanatory HTML page | Present | Single-page narrative flows from headline findings to matrix, method, verification, and interview defense | Complete |
| Understandable in roughly two minutes | Dense table risked slowing review | Above-the-fold findings, compact rubric, filters, category summaries, and progressive row details create a fast scan path | Complete |
| Findings table | Present | Searchable/filterable 100-row matrix with expandable evidence | Complete |
| Headline patterns | Present | Four quantified pattern cards plus category-level counts | Complete |
| Agent used and what it did | Runnable script was too small | Full default 100-app agent is downloadable beside its canonical dataset | Complete |
| Proof the app/agent can run | Live app existed; data artifact missing | Live deployment, downloadable script/data, source snapshot, README commands, and production tests | Complete |
| Verification hits and misses | Only summary cards | Exact seven-row hit/correction table | Complete |
| Final output and process | Present | Page integrates outcome, method, loop, caveats, and downloadable artifacts | Complete |
| Human- and agent-consumable | Page favored the human reader | JSON datasets and script complement the HTML interface | Complete |
| Be honest when wrong or defeated | Needed stronger scope caveat | Two errors remain visible; sample limitation and unreachable-source behavior are explicit | Complete |
| No need for paid accounts | Already respected | No protected endpoint success is claimed; plan/license/approval gates are findings | Complete |
| Live link | Present | `https://atlas-api-readiness.ananyap1119.chatgpt.site` | Complete |
| Source repo link | GitHub authentication is not currently available in this workspace | A downloadable source snapshot is shipped now; publishing the GitHub repository requires reconnecting GitHub authentication | External dependency |
| README explaining how to run the agent | Earlier README was too short and used an obsolete command | README now documents full setup, default 100-app run, flags, schema, workflow, verification, ownership, and limitations | Complete |

## Honest residual risks

- The verification sample is risk-weighted and small; it is not a confidence
  interval for all 100 rows.
- Vendor documentation and policies can change after the recorded review.
- Some first-party pages are JavaScript-rendered or resist automated fetching;
  the agent routes those to human review rather than treating them as negative
  evidence.
- The boolean MCP field should become a provenance enum in a production data
  model.
