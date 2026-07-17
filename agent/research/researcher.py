"""Salesforce-only Phase 2A researcher orchestration."""

import json
import os
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from dotenv import load_dotenv

from agent.enums import BuildabilityVerdict, Confidence, McpStatus, VerificationStatus
from agent.research.composio_tools import ComposioDirectAdapter
from agent.research.evidence import (
    SourceRecord,
    classify_source_url,
    deduplicate_urls,
    validate_evidence,
)
from agent.research.extraction import (
    ModelQuotaExhausted,
    empty_result,
    extract_result,
    retry_core_fields,
)
from agent.schemas import FinalAppResult, ResearcherAppResult

QUERY_INTENTS = [
    "{app} official product overview category and description",
    "{app} official API authentication methods OAuth API key",
    "{app} official independent developer signup free account trial or credits API access",
    "{app} official existing customer API credential creation admin permission",
    "{app} official multi-tenant OAuth app registration marketplace review partner",
    "{app} official REST GraphQL API resources and SDK documentation",
    "{app} official write operations and bulk API documentation",
    "{app} official webhooks event API or WebSocket documentation",
    "{app} official MCP Model Context Protocol documentation",
]

# Each high-impact gap has one explicit, low-cost search intent.  These routes
# keep product classification separate from API feature pages.
FIELD_SPECIFIC_ROUTES = {
    "authentication": "official API authentication OAuth API key documentation",
    "credential_path": "official developer API credentials signup admin access documentation",
    "documented_public_api": "official public API reference overview",
    "read_operations": "official API GET list read operations documentation",
    "write_operations": "official API create update delete write operations documentation",
    "api_breadth": "official API resources endpoints overview documentation",
}
TARGETED_SEARCH_LIMIT = 3


class MissingEnvironment(RuntimeError):
    pass


class CoverageError(RuntimeError):
    pass


def _inventory_record(app_id: str) -> dict[str, str]:
    import csv

    with Path("data/apps.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["app_id"] == app_id:
                return row
    raise ValueError(f"unknown app ID: {app_id}")


def _official_domains(app: dict[str, str]) -> tuple[str, ...]:
    hint = app.get("normalized_domain") or app.get("website_hint", "")
    host = urlparse("https://" + hint.split("/", 1)[0]).hostname or hint.split("/", 1)[0]
    return (host.lower().rstrip("."),)


def planned_queries(
    app_id: str = "salesforce", app_name: str = "Salesforce", max_queries: int | None = None
) -> list[dict[str, str]]:
    queries = [
        {
            "query_id": f"{app_id}-{index}",
            "intent": intent.format(app=app_name),
            "query": intent.format(app=app_name),
        }
        for index, intent in enumerate(QUERY_INTENTS, start=1)
    ]
    return queries if max_queries is None else queries[:max_queries]


def _run_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]


def _value(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    return value.model_dump(mode="json") if hasattr(value, "model_dump") else value


def _deterministic_verdict(result: ResearcherAppResult) -> BuildabilityVerdict:
    access = result.credential_access
    breadth = result.api_surface.api_breadth.value
    if _api_verdict_blockers(result):
        return BuildabilityVerdict.UNKNOWN
    if breadth == "none":
        return BuildabilityVerdict.NOT_CURRENTLY_BUILDABLE
    if breadth == "limited":
        return BuildabilityVerdict.LIMITED_TOOLKIT
    independent = access.independent_developer_access.value
    existing = access.existing_customer_access.value
    multi = access.multi_tenant_integration_access.value
    if independent in {
        "self_serve_free",
        "self_serve_free_credits",
        "self_serve_trial",
        "self_serve_paid",
    }:
        return BuildabilityVerdict.BUILD_NOW
    if multi in {"app_review_required", "marketplace_review_required"}:
        return BuildabilityVerdict.BUILD_AFTER_APP_REVIEW
    if multi in {"partner_approval_required", "contact_vendor_required"}:
        return BuildabilityVerdict.OUTREACH_REQUIRED
    if existing in {
        "self_serve_user",
        "workspace_admin_required",
        "vendor_enablement_required",
        "paid_plan_required",
    }:
        return BuildabilityVerdict.BUILD_WITH_CUSTOMER_CREDENTIALS
    return BuildabilityVerdict.UNKNOWN


def _field_has_evidence(result: ResearcherAppResult, *fields: str) -> bool:
    return any(item.field in fields for item in result.evidence)


def _api_verdict_blockers(result: ResearcherAppResult) -> list[str]:
    unresolved: list[str] = []
    if not result.authentication.methods or "unknown" in {
        method.value for method in result.authentication.methods
    } or not result.authentication.evidence_ids:
        unresolved.append("authentication")
    api = result.api_surface
    if not (api.documented_public_api or api.rest):
        unresolved.append("documented_public_api")
    if not _field_has_evidence(
        result, "api_surface.documented_public_api", "api_surface.rest"
    ):
        unresolved.append("api_evidence")
    if api.read_operations is not True:
        unresolved.append("read_operations")
    elif not _field_has_evidence(result, "api_surface.read_operations"):
        unresolved.append("read_operations_evidence")
    if api.write_operations is not True:
        unresolved.append("write_operations")
    elif not _field_has_evidence(result, "api_surface.write_operations"):
        unresolved.append("write_operations_evidence")
    if api.api_breadth.value == "unknown":
        unresolved.append("api_breadth")
    elif not _field_has_evidence(result, "api_surface.api_breadth"):
        unresolved.append("api_breadth_evidence")
    return unresolved


def _verdict_blockers(result: ResearcherAppResult) -> list[str]:
    blockers = _api_verdict_blockers(result)
    if blockers:
        return blockers + ["credential_path"]
    verdict = _deterministic_verdict_unchecked(result)
    access = result.credential_access
    required = {
        BuildabilityVerdict.BUILD_NOW: (
            access.independent_developer_access.value,
            "credential_access.independent_developer_access",
        ),
        BuildabilityVerdict.BUILD_WITH_CUSTOMER_CREDENTIALS: (
            access.existing_customer_access.value,
            "credential_access.existing_customer_access",
        ),
    }.get(verdict)
    if required and (
        required[0] == "unknown" or not _field_has_evidence(result, required[1])
    ):
        return ["credential_path"]
    if verdict == BuildabilityVerdict.UNKNOWN:
        return ["credential_path"]
    if verdict == BuildabilityVerdict.BUILD_AFTER_APP_REVIEW and not _field_has_evidence(
        result, "credential_access.multi_tenant_integration_access"
    ):
        return ["app_review_evidence"]
    if verdict == BuildabilityVerdict.OUTREACH_REQUIRED and not _field_has_evidence(
        result, "credential_access.multi_tenant_integration_access"
    ):
        return ["vendor_gate_evidence"]
    return []


def _deterministic_verdict_unchecked(result: ResearcherAppResult) -> BuildabilityVerdict:
    access = result.credential_access
    breadth = result.api_surface.api_breadth.value
    if breadth == "none":
        return BuildabilityVerdict.NOT_CURRENTLY_BUILDABLE
    if breadth == "limited":
        return BuildabilityVerdict.LIMITED_TOOLKIT
    independent = access.independent_developer_access.value
    existing = access.existing_customer_access.value
    multi = access.multi_tenant_integration_access.value
    if independent in {
        "self_serve_free", "self_serve_free_credits", "self_serve_trial", "self_serve_paid",
    }:
        return BuildabilityVerdict.BUILD_NOW
    if multi in {"app_review_required", "marketplace_review_required"}:
        return BuildabilityVerdict.BUILD_AFTER_APP_REVIEW
    if multi in {"partner_approval_required", "contact_vendor_required"}:
        return BuildabilityVerdict.OUTREACH_REQUIRED
    if existing in {
        "self_serve_user", "workspace_admin_required", "vendor_enablement_required",
        "paid_plan_required",
    }:
        return BuildabilityVerdict.BUILD_WITH_CUSTOMER_CREDENTIALS
    return BuildabilityVerdict.UNKNOWN


def _core_unresolved_fields(result: ResearcherAppResult) -> list[str]:
    return _verdict_blockers(result)


def _rescore_confidence(result: ResearcherAppResult) -> ResearcherAppResult:
    payload = result.model_dump(mode="json")
    core_unknown = _core_unresolved_fields(result)
    supplementary = {
        "graphql", "bulk_operations", "webhooks_events", "websocket",
        "sdk_available", "mcp_status",
    }
    if core_unknown:
        confidence = Confidence.LOW.value
    elif any(
        question.split(":", 1)[0] in supplementary
        for question in result.unresolved_questions
    ):
        confidence = Confidence.MEDIUM.value
    else:
        confidence = Confidence.HIGH.value
    payload["verification"]["overall_confidence"] = confidence
    payload["verification"]["researcher_policy_version"] = "tolerant_core_supplementary_v3"
    return ResearcherAppResult.model_validate(payload)


def _apply_evidence_validation(
    result: ResearcherAppResult,
    source_records: dict[str, SourceRecord],
) -> ResearcherAppResult:
    invalid: list[str] = []
    official_required = {
        "authentication",
        "credential_access",
        "credential_access.independent_developer_access",
        "credential_access.existing_customer_access",
        "credential_access.multi_tenant_integration_access",
        "api_surface.api_breadth",
        "api_surface.write_operations",
        "mcp",
        "mcp.status",
        "buildability",
    }
    source_id_by_url = {source.url: source_id for source_id, source in source_records.items()}
    for evidence in result.evidence:
        source_id = source_id_by_url.get(str(evidence.url), evidence.evidence_id)
        check = validate_evidence(
            evidence_id=source_id,
            field=evidence.field,
            url=str(evidence.url),
            excerpt=evidence.excerpt,
            sources=source_records,
            important=evidence.field in official_required,
        )
        if not check.valid:
            invalid.append(evidence.evidence_id)
    covered_fields = {
        evidence.field for evidence in result.evidence if evidence.evidence_id not in invalid
    }
    missing_high_impact = {
        "authentication": "authentication",
        "credential_access.independent_developer_access": (
            "credential_access.independent_developer_access"
        ),
        "credential_access.existing_customer_access": "credential_access.existing_customer_access",
        "credential_access.multi_tenant_integration_access": (
            "credential_access.multi_tenant_integration_access"
        ),
        "api_surface.api_breadth": "api_surface.api_breadth",
        "api_surface.write_operations": "api_surface.write_operations",
        "mcp.status": "mcp.status",
    }
    missing_fields = [
        label for field, label in missing_high_impact.items() if field not in covered_fields
    ]
    if not invalid and not missing_fields:
        return result
    valid_evidence = [item for item in result.evidence if item.evidence_id not in invalid]
    payload = result.model_dump(mode="json")
    payload["evidence"] = [item.model_dump(mode="json") for item in valid_evidence]
    for section_name in (
        "authentication",
        "credential_access",
        "api_surface",
        "mcp",
        "buildability",
    ):
        section = payload[section_name]
        section["evidence_ids"] = [
            evidence_id for evidence_id in section["evidence_ids"] if evidence_id not in invalid
        ]
        if invalid and section_name in {"credential_access", "mcp", "buildability"}:
            section["field_confidence"] = Confidence.LOW.value
    if invalid:
        payload["unresolved_questions"].append(
            f"Evidence validation failed for: {', '.join(invalid)}"
        )
    if missing_fields:
        payload["unresolved_questions"].append(
            "Missing high-impact evidence for: " + ", ".join(missing_fields)
        )
    return ResearcherAppResult.model_validate(payload)


def _coverage_failures(
    result: ResearcherAppResult,
    source_records: dict[str, SourceRecord],
    mcp_search_completed: bool,
) -> list[str]:
    # Evidence IDs are generated independently of source IDs; use URL matching here.
    official_urls = {
        source.url
        for source in source_records.values()
        if source.source_type in {"official", "official_github"}
    }
    official = [item for item in result.evidence if str(item.url) in official_urls]
    failures: list[str] = []
    if not any(item.field == "authentication" for item in official):
        failures.append("authentication")
    credential_fields = {
        "credential_access.independent_developer_access",
        "credential_access.existing_customer_access",
        "credential_access.multi_tenant_integration_access",
    }
    covered_credentials = {item.field for item in official if item.field in credential_fields}
    unresolved_credentials = {
        field
        for field, value in (
            (
                "credential_access.independent_developer_access",
                result.credential_access.independent_developer_access.value,
            ),
            (
                "credential_access.existing_customer_access",
                result.credential_access.existing_customer_access.value,
            ),
            (
                "credential_access.multi_tenant_integration_access",
                result.credential_access.multi_tenant_integration_access.value,
            ),
        )
        if value == "unknown"
    }
    if len(covered_credentials | unresolved_credentials) < 2:
        failures.append(
            "credential_access (fewer than two dimensions covered or explicitly unresolved)"
        )
    if not any(item.field.startswith("api_surface") for item in official):
        failures.append("api_surface")
    if result.mcp.status.value == McpStatus.UNKNOWN.value or not mcp_search_completed:
        failures.append("mcp.status")
    return failures


def _result_with_verdict(result: ResearcherAppResult) -> ResearcherAppResult:
    payload = result.model_dump(mode="json")
    verdict = _deterministic_verdict(result)
    payload["buildability"]["verdict"] = verdict.value
    if verdict == BuildabilityVerdict.UNKNOWN and not any(
        item.startswith("Buildability remains unresolved")
        for item in payload["unresolved_questions"]
    ):
        payload["unresolved_questions"].append(
            "Buildability remains unresolved from available evidence"
        )
    return _rescore_confidence(ResearcherAppResult.model_validate(payload))


def _search_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        for key in ("citations", "organic_results", "results", "items"):
            if isinstance(value.get(key), list):
                return [item for item in value[key] if isinstance(item, dict)]
        for key in ("data", "result", "response"):
            if key in value:
                items = _search_items(value[key])
                if items:
                    return items
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _page_text(value: Any) -> str:
    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"]
        for key in ("data", "results", "result", "response"):
            if key in value:
                text = _page_text(value[key])
                if text:
                    return text
    if isinstance(value, list):
        return "\n\n".join(filter(None, (_page_text(item) for item in value)))
    return ""


def _stored_source_records(run_dir: Path) -> dict[str, SourceRecord] | None:
    source_path = run_dir / "sources.json"
    if not source_path.is_file():
        return None
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, list) or not payload:
        return None
    records: dict[str, SourceRecord] = {}
    for item in payload:
        if not isinstance(item, dict):
            return None
        required = {"source_id", "url", "text", "source_type", "query_intent"}
        if not required.issubset(item) or not isinstance(item["text"], str):
            return None
        text_path = run_dir / f"{item['source_id']}.txt"
        if not text_path.is_file():
            return None
        try:
            text = text_path.read_text(encoding="utf-8")
        except OSError:
            return None
        if text != item["text"] or not text.strip():
            return None
        records[item["source_id"]] = SourceRecord(
            source_id=item["source_id"],
            url=item["url"],
            title=item.get("title"),
            text=text,
            source_type=item["source_type"],
            query_intent=item["query_intent"],
        )
    return records or None


def _latest_usable_run(app_id: str = "salesforce") -> tuple[Path, dict[str, SourceRecord]]:
    root = Path("data/raw") / app_id
    for run_dir in sorted(root.glob("*"), reverse=True):
        if run_dir.is_dir():
            records = _stored_source_records(run_dir)
            if records:
                return run_dir, records
    raise ValueError("no usable stored Salesforce source run found")


def _latest_run_dir(app_id: str) -> Path:
    root = Path("data/raw") / app_id
    runs = [p for p in root.glob("*") if p.is_dir() and (p / "queries.json").is_file()]
    if not runs:
        raise ValueError("no stored source run found")
    return max(runs, key=lambda p: p.stat().st_mtime)


def _mcp_search_completed(run_dir: Path, app_id: str) -> bool:
    path = run_dir / "search_results.json"
    if not path.is_file():
        return False
    try:
        results = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return any(
        isinstance(item, dict) and item.get("query_id") == f"{app_id}-9" for item in results
    )


def _extract_and_persist(
    *,
    app: dict[str, str],
    source_records: dict[str, SourceRecord],
    run_dir: Path,
    primary_model: str,
    fallback_model: str,
    google_api_key: str,
    mcp_search_completed: bool,
    official_domains: tuple[str, ...],
    provider: str,
    composio_api_key: str | None = None,
    targeted_limit: int = TARGETED_SEARCH_LIMIT,
) -> ResearcherAppResult:
    model_log = run_dir / "model_attempts.jsonl"
    model_log.write_text("", encoding="utf-8")
    try:
        result = extract_result(
            model=primary_model,
            fallback_model=fallback_model,
            log_path=model_log,
            app=app,
            sources=[_value(record) for record in source_records.values()],
            google_api_key=google_api_key,
            mcp_search_completed=mcp_search_completed,
            provider=provider,
        )
    except ModelQuotaExhausted as error:
        checkpoint = {
            "app_id": app["app_id"],
            "status": "operationally_blocked",
            "reason": str(error),
            "cached_sources_preserved": True,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        (run_dir / "extraction_checkpoint.json").write_text(
            json.dumps(checkpoint, indent=2), encoding="utf-8"
        )
        raise
    output = Path("data/researcher") / f"{app['app_id']}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = _result_with_verdict(result)
    output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    unresolved = [
        field for field in _core_unresolved_fields(result)
        if field in FIELD_SPECIFIC_ROUTES
    ][:targeted_limit]
    targeted_searches = 0
    fetched_sources = 0
    if unresolved and composio_api_key:
        existing_urls = {record.url for record in source_records.values()}
        with ComposioDirectAdapter(
            composio_api_key, run_dir / "tool_calls.jsonl"
        ) as tools:
            for field in unresolved:
                targeted_searches += 1
                try:
                    raw = tools.search(
                        f"{app['app_name']} {FIELD_SPECIFIC_ROUTES[field]}"
                    )
                except Exception:  # noqa: BLE001 - retain first-pass checkpoint
                    continue
                candidates = deduplicate_urls(
                    item.get("url", "") for item in _search_items(raw)
                )
                url = next((
                    candidate for candidate in candidates
                    if candidate not in existing_urls
                    and classify_source_url(candidate, official_domains) == "official"
                ), None)
                if not url:
                    continue
                try:
                    text = _page_text(tools.fetch(url))
                except Exception:  # noqa: BLE001 - field remains unknown
                    continue
                if not text:
                    continue
                fetched_sources += 1
                source_id = f"{app['app_id']}-targeted-{fetched_sources:02d}"
                record = SourceRecord(
                    source_id=source_id, url=url, title=None, text=text,
                    source_type=classify_source_url(url, official_domains),
                    query_intent=FIELD_SPECIFIC_ROUTES[field],
                )
                source_records[source_id] = record
                existing_urls.add(url)
                (run_dir / f"{source_id}.txt").write_text(text, encoding="utf-8")
        (run_dir / "sources.json").write_text(
            json.dumps([_value(record) for record in source_records.values()], indent=2),
            encoding="utf-8",
        )
        requested = tuple(dict.fromkeys(
            extraction_field
            for field in unresolved
            for extraction_field in (
                ("authentication_methods",) if field == "authentication" else
                (
                    "independent_developer_access", "existing_customer_access",
                    "multi_tenant_integration_access",
                ) if field == "credential_path" else
                ("documented_api",) if field == "documented_public_api" else (field,)
            )
        ))
        try:
            result = retry_core_fields(
                result=result, requested_fields=requested, model=primary_model, app=app,
                sources=[_value(record) for record in source_records.values()],
                google_api_key=google_api_key, log_path=model_log,
                mcp_search_completed=mcp_search_completed, provider=provider,
            )
            result = _result_with_verdict(result)
            output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        except Exception:  # noqa: BLE001 - targeted retry never invalidates first pass
            # The complete first-pass result is already checkpointed above.
            pass
    (run_dir / "targeted_retry.json").write_text(json.dumps({
        "targeted_searches": targeted_searches,
        "fetched_sources": fetched_sources,
        "retried_fields": unresolved if targeted_searches else [],
    }, indent=2), encoding="utf-8")
    return result


def run_research(
    app_id: str,
    *,
    dry_run: bool = False,
    resume_latest: bool = False,
    optimized: bool = False,
) -> dict[str, Any] | ResearcherAppResult:
    app = _inventory_record(app_id)
    queries = planned_queries(
        app_id, app["app_name"], max_queries=5 if optimized else None
    )
    if dry_run:
        return {
            "app_id": app_id,
            "source_order": app["source_order"],
            "query_count": len(queries),
            "queries": queries,
            "network_calls": False,
            "model_calls": False,
        }
    load_dotenv()
    provider = os.getenv("RESEARCH_PROVIDER", "openrouter").lower()
    key_name = {
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }.get(provider, "GOOGLE_API_KEY")
    missing = [key_name] if not os.getenv(key_name) else []
    if not resume_latest and not os.getenv("COMPOSIO_API_KEY"):
        missing.append("COMPOSIO_API_KEY")
    if missing:
        raise MissingEnvironment("missing environment variables: " + ", ".join(missing))
    primary_model = os.getenv(
        "RESEARCH_MODEL",
        "deepseek/deepseek-chat-v3.1"
        if provider == "openrouter"
        else "openai/gpt-oss-120b" if provider == "groq" else "gemini-3.1-flash-lite",
    )
    fallback_model = os.getenv("RESEARCH_FALLBACK_MODEL", "")
    if resume_latest:
        try:
            run_dir, source_records = _latest_usable_run(app_id)
        except ValueError:
            if not optimized:
                raise
            run_dir, source_records = _latest_run_dir(app_id), {}
        if not source_records:
            result = empty_result(
                app=app,
                mcp_search_completed=_mcp_search_completed(run_dir, app_id),
            )
            output = Path("data/researcher") / f"{app_id}.json"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(result.model_dump_json(indent=2), encoding="utf-8")
            return result
        return _extract_and_persist(
            app=app,
            source_records=source_records,
            run_dir=run_dir,
            primary_model=primary_model,
            fallback_model=fallback_model,
            google_api_key=os.environ[key_name],
            mcp_search_completed=_mcp_search_completed(run_dir, app_id),
            official_domains=_official_domains(app),
            provider=provider,
            composio_api_key=os.getenv("COMPOSIO_API_KEY"),
            targeted_limit=1 if optimized else TARGETED_SEARCH_LIMIT,
        )
    run_id = _run_id()
    run_dir = Path("data/raw") / app_id / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "queries.json").write_text(json.dumps(queries, indent=2), encoding="utf-8")
    search_results: list[dict[str, Any]] = []
    source_records: dict[str, SourceRecord] = {}
    discarded_urls: list[dict[str, str]] = []
    official_domains = _official_domains(app)
    with ComposioDirectAdapter(
        os.environ["COMPOSIO_API_KEY"], run_dir / "tool_calls.jsonl"
    ) as tools:
        for query in queries:
            raw = tools.search(query["query"])
            items = [
                {**item, "_query_id": query["query_id"], "_query_intent": query["intent"]}
                for item in _search_items(raw)
            ]
            search_results.append({"query_id": query["query_id"], "results": items})
        all_candidate_urls = deduplicate_urls(
            item.get("url", "") for result in search_results for item in result["results"]
        )
        candidate_urls = [
            url for url in all_candidate_urls
            if classify_source_url(url, official_domains) == "official"
        ]
        # Reserve at least one official page for every field-specific intent
        # before filling the remaining page budget.
        prioritized: list[str] = []
        for query in queries:
            for item in next(
                (result["results"] for result in search_results
                 if result["query_id"] == query["query_id"]), []
            ):
                url = item.get("url", "")
                if url in candidate_urls and url not in prioritized:
                    prioritized.append(url)
                    break
        candidate_urls = prioritized + [url for url in candidate_urls if url not in prioritized]
        for url in all_candidate_urls:
            if url not in candidate_urls:
                discarded_urls.append(
                    {"url": url, "reason": "not an official Salesforce-controlled host"}
                )
        retained_limit = 8 if optimized else 15
        for url in candidate_urls[retained_limit:]:
            discarded_urls.append({
                "url": url, "reason": f"retained-page limit of {retained_limit} reached"
            })
        for index, url in enumerate(candidate_urls[:retained_limit], start=1):
            matching = next(
                (
                    item
                    for result in search_results
                    for item in result["results"]
                    if item.get("url") == url
                ),
                {},
            )
            try:
                page = tools.fetch(url)
            except Exception:  # noqa: BLE001 - bounded fallback is recorded by adapter
                discarded_urls.append({"url": url, "reason": "page retrieval failed"})
                continue
            text = _page_text(page)
            if not text:
                discarded_urls.append({"url": url, "reason": "page retrieval returned no text"})
                continue
            source_id = f"{app_id}-{index:02d}"
            source_records[source_id] = SourceRecord(
                source_id=source_id,
                url=url,
                title=matching.get("title"),
                text=text,
                source_type=classify_source_url(url, official_domains),
                query_intent=matching.get("_query_intent", matching.get("_query_id", "unknown")),
            )
            (run_dir / f"{source_id}.txt").write_text(text, encoding="utf-8")
        (run_dir / "search_results.json").write_text(
            json.dumps(search_results, indent=2), encoding="utf-8"
        )
        (run_dir / "sources.json").write_text(
            json.dumps([_value(record) for record in source_records.values()], indent=2),
            encoding="utf-8",
        )
        (run_dir / "discarded_urls.json").write_text(
            json.dumps(discarded_urls, indent=2), encoding="utf-8"
        )
    return _extract_and_persist(
        app=app,
        source_records=source_records,
        run_dir=run_dir,
        primary_model=primary_model,
        fallback_model=fallback_model,
        google_api_key=os.environ[key_name],
        mcp_search_completed=True,
        official_domains=_official_domains(app),
        provider=provider,
        composio_api_key=os.getenv("COMPOSIO_API_KEY"),
        targeted_limit=1 if optimized else TARGETED_SEARCH_LIMIT,
    )


def _batch_summary_entry(app: dict[str, str], result: ResearcherAppResult) -> dict[str, Any]:
    high_impact = {
        "authentication": "authentication",
        "credential_access.independent_developer_access": "independent_developer_access",
        "credential_access.existing_customer_access": "existing_customer_access",
        "credential_access.multi_tenant_integration_access": "multi_tenant_integration_access",
        "api_surface.api_breadth": "api_breadth",
        "api_surface.write_operations": "write_operations",
        "api_surface.graphql": "graphql",
        "api_surface.bulk_operations": "bulk_operations",
        "api_surface.webhooks": "webhooks_events",
        "mcp.status": "mcp_status",
        "buildability": "buildability_verdict",
    }
    covered = {item.field for item in result.evidence}
    coverage = {
        label: any(field in covered for field in (key, key.split(".")[-1]))
        for key, label in high_impact.items()
    }
    unresolved = list(result.unresolved_questions)
    supplementary_fields = {
        "graphql", "bulk_operations", "webhooks", "websocket", "sdk_available", "mcp"
    }
    core_unresolved = list(dict.fromkeys(_verdict_blockers(result)))
    supplementary_unresolved = [
        item for item in unresolved
        if item not in core_unresolved
        and item.split(":", 1)[0].split(".")[-1] in supplementary_fields
    ]
    risks = []
    for section in ("authentication", "credential_access", "api_surface", "buildability"):
        if section == "buildability":
            continue
        if getattr(result, section).field_confidence.value == "low":
            risks.append(f"low_confidence:{section}")
    if result.buildability.verdict.value == BuildabilityVerdict.UNKNOWN.value:
        risks.append("buildability_unknown")
    risks.extend(f"unresolved:{item.split(':', 1)[0]}" for item in core_unresolved)
    machine_final = (
        result.buildability.verdict.value != BuildabilityVerdict.UNKNOWN.value
        and not core_unresolved
        and result.verification.overall_confidence.value in {"medium", "high"}
    )
    human_review_required = bool(core_unresolved)
    model_counts = {"core": 0, "supplementary": 0, "targeted_core": 0}
    targeted_searches = 0
    try:
        latest_run, _ = _latest_usable_run(app["app_id"])
        attempts_path = latest_run / "model_attempts.jsonl"
        if attempts_path.is_file():
            for line in attempts_path.read_text(encoding="utf-8").splitlines():
                attempt = json.loads(line)
                group = attempt.get("group")
                if group in model_counts:
                    model_counts[group] += 1
        targeted_path = latest_run / "targeted_retry.json"
        if targeted_path.is_file():
            targeted_searches = int(
                json.loads(targeted_path.read_text(encoding="utf-8")).get(
                    "targeted_searches", 0
                )
            )
    except (OSError, ValueError, json.JSONDecodeError, TypeError):
        pass
    return {
        "app_id": app["app_id"],
        "app_name": app["app_name"],
        "status": "successful",
        "searches_performed": 9,
        "official_sources_retained": sum(
            item.source_type in {"official", "official_github"}
            for item in result.evidence
        ),
        "valid_evidence_count": len(result.evidence),
        "evidence_coverage": coverage,
        "core_model_calls": model_counts["core"],
        "supplementary_model_calls": model_counts["supplementary"],
        "targeted_retries_performed": model_counts["targeted_core"],
        "targeted_searches_made": targeted_searches,
        "cached_sources_reused": True,
        "provider": os.getenv("RESEARCH_PROVIDER", "openrouter").lower(),
        "groq_primary_requests": 0,
        "groq_fallback_requests": 0,
        "core_unresolved_fields": core_unresolved,
        "supplementary_unresolved_fields": supplementary_unresolved,
        "unresolved_fields": unresolved,
        "risk_flags": sorted(set(risks)),
        "human_review_required": human_review_required,
        "human_review_reason": "; ".join(risks) if human_review_required else None,
        "researcher_verdict": result.buildability.verdict.value,
        "confidence": result.verification.overall_confidence.value,
        "machine_final": machine_final,
        "result_state": (
            "machine_final" if machine_final else
            "human_review_required" if human_review_required else
            "completed_with_unknown_fields"
        ),
        "output_path": f"data/final/{app['app_id']}.json" if machine_final else (
            f"data/researcher/{app['app_id']}.json"
        ),
        "failure_message": None,
    }


def _finalize_if_eligible(app: dict[str, str], result: ResearcherAppResult) -> Path | None:
    """Write a final record only when verdict-specific evidence is sufficient."""
    result = _result_with_verdict(_rescore_confidence(result))
    entry = _batch_summary_entry(app, result)
    if not entry["machine_final"]:
        return None
    payload = result.model_dump(mode="json")
    payload["source_order"] = int(app["source_order"])
    verification = payload["verification"]
    verification.update({
        "status": VerificationStatus.FINALIZED.value,
        "human_reviewed": False,
        "audit_status": "not_sampled",
        "finalized_by": "deterministic_finalization_gate",
    })
    final = FinalAppResult.model_validate(payload)
    path = Path("data/final") / f"{app['app_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(final.model_dump_json(indent=2), encoding="utf-8")
    return path


def run_research_batch(
    *,
    calibration: bool,
    skip_finalized: bool,
    resume: bool = False,
    production: bool = False,
    start_order: int = 1,
    end_order: int = 100,
) -> dict[str, Any]:
    import csv

    load_dotenv()
    with Path("data/apps.csv").open(encoding="utf-8", newline="") as handle:
        apps = list(csv.DictReader(handle))
    if production and (start_order < 1 or end_order > 100 or start_order > end_order):
        raise ValueError("invalid production source-order range")
    selected = select_batch_apps(
        apps, calibration=calibration, production=production,
        start_order=start_order, end_order=end_order,
    )
    summary_path = Path(
        "evaluation/production_batch_summary.json"
        if production else "evaluation/calibration_batch_summary.json"
    )
    md_path = Path(
        "evaluation/production_batch_summary.md"
        if production else "evaluation/calibration_batch_summary.md"
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for app in selected:
        final_path = Path("data/final") / f"{app['app_id']}.json"
        output_path = Path("data/researcher") / f"{app['app_id']}.json"
        if (skip_finalized or production) and final_path.is_file():
            entries.append({
                "app_id": app["app_id"], "app_name": app["app_name"],
                "status": "skipped", "reason": "valid final record exists",
                "output_path": str(final_path),
            })
            continue
        if resume and output_path.is_file():
            try:
                existing = ResearcherAppResult.model_validate_json(
                    output_path.read_text(encoding="utf-8")
                )
                provider_name = os.getenv("RESEARCH_PROVIDER", "openrouter").lower()
                provider_key = {
                    "groq": "GROQ_API_KEY",
                    "openrouter": "OPENROUTER_API_KEY",
                }.get(provider_name, "GOOGLE_API_KEY")
                if not os.getenv(provider_key):
                    rescored = _result_with_verdict(_rescore_confidence(existing))
                    _finalize_if_eligible(app, rescored)
                    entry = _batch_summary_entry(app, rescored)
                    entry.update({
                        "status": "successful",
                        "reason": "rescored cached result; provider key missing",
                    })
                    entries.append(entry)
                    summary = _make_batch_summary(entries)
                    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
                    continue
                if (
                    existing.verification.researcher_policy_version
                    != "tolerant_core_supplementary_v3"
                ) or any(
                    question.startswith("Missing high-impact evidence")
                    for question in existing.unresolved_questions
                ):
                    raise ValueError("prior run failed the quality gate")
                rescored = _result_with_verdict(_rescore_confidence(existing))
                output_path.write_text(rescored.model_dump_json(indent=2), encoding="utf-8")
                _finalize_if_eligible(app, rescored)
                entry = _batch_summary_entry(app, rescored)
                entry.update({"status": "skipped", "reason": "rescored existing researcher result"})
                entries.append(entry)
                continue
            except Exception:  # noqa: BLE001
                pass
        try:
            use_stored = False
            if resume:
                try:
                    _latest_usable_run(app["app_id"])
                    use_stored = True
                except ValueError:
                    try:
                        _latest_run_dir(app["app_id"])
                        use_stored = True
                    except ValueError:
                        use_stored = False
            result = run_research(
                app["app_id"], resume_latest=use_stored, optimized=production
            )
            if not isinstance(result, ResearcherAppResult):
                raise RuntimeError("research did not return a researcher result")
            _finalize_if_eligible(app, result)
            entry = _batch_summary_entry(app, result)
            queue_path = Path("data/reviewed") / f"{app['app_id']}_review_queue.json"
            queue_path.parent.mkdir(parents=True, exist_ok=True)
            if entry["human_review_required"]:
                queue_path.write_text(json.dumps([entry], indent=2), encoding="utf-8")
            entries.append(entry)
        except Exception as error:  # noqa: BLE001 - continue batch and persist failure
            operational = isinstance(error, ModelQuotaExhausted)
            entries.append({
                "app_id": app["app_id"], "app_name": app["app_name"],
                "status": "operational_failure" if operational else "failed",
                "searches_performed": 0,
                "official_sources_retained": 0, "valid_evidence_count": 0,
                "evidence_coverage": {}, "targeted_retries_performed": 0,
                "unresolved_fields": [], "risk_flags": [],
                "human_review_required": False, "researcher_verdict": None,
                "confidence": None, "output_path": str(output_path),
                "failure_message": str(error)[:300],
            })
            if output_path.is_file():
                queue_path = Path("data/reviewed") / f"{app['app_id']}_review_queue.json"
                queue_path.parent.mkdir(parents=True, exist_ok=True)
                queue_path.write_text(
                    json.dumps([entries[-1]], indent=2), encoding="utf-8"
                )
        summary = _make_batch_summary(entries)
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary = _make_batch_summary(entries)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = ["# Calibration batch summary", "", f"Apps: {len(entries)}", ""]
    for item in entries:
        lines.append(
            f"- {item['app_id']}: {item['status']} "
            f"({item.get('researcher_verdict')}, {item.get('confidence')})"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if summary["totals"]["failed_apps"]:
        raise CoverageError(
            f"calibration batch failed for {summary['totals']['failed_apps']} app(s)"
        )
    return summary


def select_batch_apps(
    apps: list[dict[str, str]], *, calibration: bool, production: bool,
    start_order: int = 1, end_order: int = 100,
) -> list[dict[str, str]]:
    if production:
        return [
            row for row in apps
            if start_order <= int(row["source_order"]) <= end_order
        ]
    if calibration:
        return [row for row in apps if row["calibration_set"].lower() == "true"]
    return list(apps)


def _make_batch_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    from collections import Counter

    confidence_counts = Counter(
        item.get("confidence") for item in entries if item.get("confidence")
    )
    unresolved_counts = Counter(
        field.split(":", 1)[0]
        for item in entries
        for field in item.get("unresolved_fields", [])
    )
    risk_counts = Counter(
        flag for item in entries for flag in item.get("risk_flags", [])
    )
    return {
        "apps": entries,
        "totals": {
            "apps_finalized_before_batch": sum(
                item["status"] == "skipped" and "final" in item.get("output_path", "")
                for item in entries
            ),
            "apps_newly_researched": sum(item["status"] == "successful" for item in entries),
            "successful_apps": sum(item["status"] == "successful" for item in entries),
            "failed_apps": sum(item["status"] == "failed" for item in entries),
            "operational_failures": sum(
                item["status"] == "operational_failure" for item in entries
            ),
            "machine_final_apps": sum(item.get("machine_final", False) for item in entries),
            "unknown_verdict_apps": sum(
                item.get("researcher_verdict") == BuildabilityVerdict.UNKNOWN.value
                for item in entries
            ),
            "verdict_counts": dict(Counter(
                item.get("researcher_verdict") for item in entries
                if item.get("researcher_verdict")
            )),
            "human_review_queue_count": sum(
                item.get("human_review_required", False) for item in entries
            ),
            "apps_requiring_human_review": sum(
                item.get("human_review_required", False) for item in entries
            ),
            "confidence_counts": dict(confidence_counts),
            "most_common_unresolved_fields": unresolved_counts.most_common(10),
            "most_common_risk_flags": risk_counts.most_common(10),
        },
    }
