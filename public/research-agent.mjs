/**
 * Atlas research agent
 *
 * Default run (all 100):
 *   node public/research-agent.mjs > research-output.json
 *
 * Custom input:
 *   node public/research-agent.mjs --input my-apps.json --limit 10
 *
 * The agent fetches first-party source pages, extracts transparent auth/access/
 * surface signals, compares them with the curated row, assigns confidence, and
 * routes conflicts to human review. It never invents a successful API call.
 */
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(
  process.argv.slice(2).reduce((pairs, arg, index, all) => {
    if (arg.startsWith("--")) pairs.push([arg.slice(2), all[index + 1]?.startsWith("--") ? true : all[index + 1] ?? true]);
    return pairs;
  }, []),
);
const inputPath = path.resolve(args.input || path.join(here, "research-set.json"));
const limit = Number(args.limit || 100);
const concurrency = Math.max(1, Math.min(12, Number(args.concurrency || 6)));
const timeoutMs = Math.max(3000, Number(args.timeout || 12000));
const apps = JSON.parse(await fs.readFile(inputPath, "utf8")).slice(0, limit);

const patterns = {
  auth: [
    ["OAuth 2.0", /oauth\s*2|authorization code/i],
    ["API key", /api[- ]?key|secret key/i],
    ["token", /bearer token|access token|personal access token/i],
    ["Basic", /basic authentication|basic auth/i],
    ["JWT", /\bjwt\b|json web token/i],
  ],
  surface: [
    ["REST", /\brest\b|api reference|endpoint/i],
    ["GraphQL", /graphql/i],
    ["MCP", /model context protocol|\bmcp server\b/i],
    ["CLI", /command.line|\bcli\b/i],
  ],
  gated: /apply for access|approval|partner program|contact sales|enterprise.only|administrator approval|paid plan|license required/i,
  selfServe: /create (an )?app|developer account|sign up|free trial|api key(s)? (page|tab)|creator dashboard/i,
};

function cleanHtml(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;|&#160;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/\s+/g, " ")
    .trim();
}

function excerpt(text, pattern) {
  const match = pattern.exec(text);
  if (!match) return null;
  const start = Math.max(0, match.index - 90);
  const end = Math.min(text.length, match.index + match[0].length + 140);
  return text.slice(start, end).trim();
}

function classify(text) {
  const auth = patterns.auth.filter(([, pattern]) => pattern.test(text)).map(([name]) => name);
  const surface = patterns.surface.filter(([, pattern]) => pattern.test(text)).map(([name]) => name);
  const gated = patterns.gated.test(text);
  const selfServe = patterns.selfServe.test(text);
  const evidence = {
    auth: patterns.auth.map(([name, pattern]) => ({ name, excerpt: excerpt(text, pattern) })).filter((x) => x.excerpt),
    surface: patterns.surface.map(([name, pattern]) => ({ name, excerpt: excerpt(text, pattern) })).filter((x) => x.excerpt),
    access: excerpt(text, gated ? patterns.gated : patterns.selfServe),
  };
  return {
    observed_auth: auth,
    observed_surface: surface,
    observed_access: gated ? "gated_signal" : selfServe ? "self_serve_signal" : "unclear",
    observed_mcp: surface.includes("MCP"),
    evidence,
  };
}

function compare(expected, observed) {
  const conflicts = [];
  if (expected.access === "Self-serve" && observed.observed_access === "gated_signal") {
    conflicts.push("expected self-serve but source contains gate language");
  }
  if (expected.access === "Gated" && observed.observed_access === "self_serve_signal") {
    conflicts.push("expected gated but source contains self-serve language");
  }
  if (!observed.observed_auth.length) conflicts.push("no auth signal extracted");
  if (!observed.observed_surface.length) conflicts.push("no callable-surface signal extracted");
  return conflicts;
}

async function inspect(app) {
  const started = Date.now();
  const result = {
    id: app.id,
    app: app.name,
    source: app.evidence,
    source_status: "unreachable",
    fetched_at: new Date().toISOString(),
    expected: {
      category: app.category,
      auth: app.auth,
      access: app.access,
      surface: app.surface,
      mcp: app.mcp,
      verdict: app.verdict,
      blocker: app.blocker,
    },
    observed: null,
    confidence: 0,
    conflicts: [],
    human_review: true,
    duration_ms: 0,
  };
  try {
    const response = await fetch(app.evidence, {
      redirect: "follow",
      headers: { "user-agent": "AtlasResearchAgent/1.0 (+evidence audit)" },
      signal: AbortSignal.timeout(timeoutMs),
    });
    result.source_status = response.ok ? "reachable" : `http_${response.status}`;
    const text = cleanHtml(await response.text());
    result.observed = classify(text);
    result.conflicts = compare(app, result.observed);
    const complete = result.observed.observed_auth.length > 0 && result.observed.observed_surface.length > 0;
    result.confidence = response.ok ? (complete && !result.conflicts.length ? 0.86 : complete ? 0.72 : 0.42) : 0.18;
    result.human_review = result.confidence < 0.82 || result.conflicts.length > 0 || app.access === "Gated";
  } catch (error) {
    result.conflicts = [`fetch failed: ${error.name || "Error"}`];
  }
  result.duration_ms = Date.now() - started;
  return result;
}

async function mapLimit(items, worker, size) {
  const results = new Array(items.length);
  let cursor = 0;
  async function run() {
    while (cursor < items.length) {
      const index = cursor++;
      results[index] = await worker(items[index]);
      process.stderr.write(`\rresearched ${index + 1}/${items.length}`);
    }
  }
  await Promise.all(Array.from({ length: Math.min(size, items.length) }, run));
  process.stderr.write("\n");
  return results;
}

const results = await mapLimit(apps, inspect, concurrency);
const summary = {
  total: results.length,
  reachable: results.filter((r) => r.source_status === "reachable").length,
  human_review: results.filter((r) => r.human_review).length,
  conflicts: results.reduce((sum, r) => sum + r.conflicts.length, 0),
  average_confidence: Number((results.reduce((sum, r) => sum + r.confidence, 0) / Math.max(1, results.length)).toFixed(3)),
};
process.stdout.write(
  JSON.stringify(
    {
      schema_version: "1.0",
      generated_at: new Date().toISOString(),
      input: path.basename(inputPath),
      rubric: {
        ready: "Documented callable surface and developer-obtainable credentials.",
        constrained: "Callable surface exists; plan, review, tenant admin, license, or partnership is required.",
        blocked: "No usable public callable surface found.",
      },
      summary,
      results,
    },
    null,
    2,
  ),
);
