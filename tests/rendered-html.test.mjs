import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the complete API readiness case study", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>Atlas — API Readiness Index<\/title>/i);
  assert.match(html, /100 \/ 100 APPS/);
  assert.match(html, /Every app\. Every decision\./);
  assert.match(html, /Research that checks itself\./);
  assert.match(html, /Trust is a measured output\./);
  assert.doesNotMatch(html, /INTERVIEW PREP|Questions this work should survive\./);
  assert.match(html, /manually sampled seven risk-weighted rows/);
  assert.match(html, /Google Ads/);
  assert.match(html, /Corrected/);
  assert.match(html, /Salesforce/);
  assert.match(html, /NotebookLM/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape/);
});

test("ships the research agent and consistent 100-row source data", async () => {
  const [page, agent, packageJson, researchJson, verificationJson, questionnaire, audit] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../public/research-agent.mjs", import.meta.url), "utf8"),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(new URL("../public/research-set.json", import.meta.url), "utf8"),
    readFile(new URL("../public/verification-sample.json", import.meta.url), "utf8"),
    readFile(new URL("../public/interview-questionnaire.md", import.meta.url), "utf8"),
    readFile(new URL("../public/assignment-compliance-audit.md", import.meta.url), "utf8"),
  ]);
  const rows = page.match(/^\s*\["[^"]+"/gm) ?? [];
  const researchSet = JSON.parse(researchJson);
  const verificationSet = JSON.parse(verificationJson);
  assert.equal(rows.length, 100);
  assert.equal(researchSet.length, 100);
  assert.equal(new Set(researchSet.map((row) => row.name)).size, 100);
  assert.equal(new Set(researchSet.map((row) => row.category)).size, 10);
  assert.ok(researchSet.every((row) => row.description && row.evidence));
  assert.equal(verificationSet.length, 7);
  assert.equal(verificationSet.filter((row) => row.result === "Corrected").length, 2);
  assert.match(agent, /function classify/);
  assert.match(agent, /human_review/);
  assert.match(questionnaire, /### 35\./);
  assert.match(audit, /Source repo link/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
});
