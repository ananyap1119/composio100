"""Low-cost, provider-neutral, tolerant research extraction."""

import json
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from agent.enums import (
    ApiBreadth,
    AuthenticationMethod,
    BuildabilityVerdict,
    Confidence,
    ExistingCustomerAccess,
    IndependentDeveloperAccess,
    McpStatus,
    MultiTenantIntegrationAccess,
    VerificationStatus,
)
from agent.research.evidence import excerpt_in_text
from agent.schemas import ResearcherAppResult
from agent.ssl_config import configure_ssl

MAX_CONTEXT_CHARS = 18_000
MAX_PASSAGE_CHARS = 1_500
MAX_SOURCES_PER_CALL = 10
TRI_STATE = {"supported", "not_supported", "unknown"}

CORE_FIELDS = (
    "category",
    "description",
    "authentication_methods",
    "independent_developer_access",
    "existing_customer_access",
    "multi_tenant_integration_access",
    "documented_api",
    "rest",
    "read_operations",
    "write_operations",
    "api_breadth",
)
SUPPLEMENTARY_FIELDS = (
    "graphql",
    "bulk_operations",
    "webhooks_events",
    "websocket",
    "sdk_available",
    "mcp_status",
)

FIELD_ENUMS: dict[str, set[str]] = {
    "authentication_methods": {item.value for item in AuthenticationMethod},
    "independent_developer_access": {item.value for item in IndependentDeveloperAccess},
    "existing_customer_access": {item.value for item in ExistingCustomerAccess},
    "multi_tenant_integration_access": {
        item.value for item in MultiTenantIntegrationAccess
    },
    "documented_api": TRI_STATE,
    "rest": TRI_STATE,
    "read_operations": TRI_STATE,
    "write_operations": TRI_STATE,
    "api_breadth": {item.value for item in ApiBreadth},
    "graphql": TRI_STATE,
    "bulk_operations": TRI_STATE,
    "webhooks_events": TRI_STATE,
    "websocket": TRI_STATE,
    "sdk_available": TRI_STATE,
    "mcp_status": {item.value for item in McpStatus},
}

FIELD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "category": ("product", "platform", "overview", "about"),
    "description": ("product", "platform", "overview", "about"),
    "authentication_methods": ("authentication", "oauth", "api key", "token"),
    "independent_developer_access": ("developer", "signup", "free", "trial"),
    "existing_customer_access": ("admin", "credential", "client", "workspace"),
    "multi_tenant_integration_access": (
        "multi-tenant", "distribution", "marketplace", "review", "partner"
    ),
    "documented_api": ("api", "developer", "reference"),
    "rest": ("rest", "endpoint", "api"),
    "read_operations": ("get", "list", "read", "retrieve", "query"),
    "write_operations": ("post", "create", "update", "delete", "write"),
    "api_breadth": ("resource", "endpoint", "object", "api overview"),
    "graphql": ("graphql",),
    "bulk_operations": ("bulk", "batch", "import", "export"),
    "webhooks_events": ("webhook", "event", "subscription", "callback"),
    "websocket": ("websocket", "real-time", "realtime"),
    "sdk_available": ("sdk", "client library", "libraries"),
    "mcp_status": ("mcp", "model context protocol"),
}

SYSTEM_INSTRUCTIONS = """Extract only facts in the supplied official passages.
Return one JSON object and no prose. Each requested field must be an object with exactly:
{"value": ..., "source_ids": [], "excerpts": []}.
Use only listed SOURCE_ID values. Excerpts must be short exact contiguous text from that source.
Use "unknown" (or [] for authentication_methods) when evidence is absent. Never output null.
Do not return confidence, evidence IDs, notes, verdicts, review status, or timestamps.
Negative values require explicit negative evidence. Do not use outside knowledge."""


class ModelQuotaExhausted(RuntimeError):
    """The configured provider has exhausted a non-immediate quota."""


class CoreExtractionError(RuntimeError):
    """No usable core extraction could be produced."""


def _status_code(error: Exception) -> int | None:
    for name in ("status_code", "code"):
        value = getattr(error, name, None)
        if isinstance(value, int):
            return value
    return None


def _is_quota_error(error: Exception) -> bool:
    return _status_code(error) == 429


def _log_attempt(
    log_path: Path | None,
    *,
    group: str,
    model: str,
    error: Exception | None,
) -> None:
    if log_path is None:
        return
    record = {
        "event": "model_attempt",
        "group": group,
        "model": model,
        "attempt": 1,
        "error_class": type(error).__name__ if error else None,
        "status": _status_code(error) if error else None,
        "retry_delay": 0,
        "fallback_activated": False,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _first_json_object(text: str) -> tuple[dict[str, Any], list[str]]:
    """Decode the first complete JSON object without accepting non-object output."""
    decoder = json.JSONDecoder()
    normalizations: list[str] = []
    for match in re.finditer(r"\{", text):
        try:
            value, end = decoder.raw_decode(text[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            if text[:match.start()].strip() or text[match.start() + end:].strip():
                normalizations.append("discarded surrounding non-JSON text")
            return value, normalizations
    raise CoreExtractionError("provider response contained no valid JSON object")


def _deduplicate_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip() and item.strip() not in result:
            result.append(item.strip())
    return result


def _normalise_authentication(value: Any) -> str:
    candidate = str(value or "").strip().lower()
    if "oauth" in candidate:
        return AuthenticationMethod.OAUTH2.value
    if "jwt" in candidate:
        return AuthenticationMethod.JWT.value
    if "bearer" in candidate:
        return AuthenticationMethod.BEARER_TOKEN.value
    if "api key" in candidate or candidate == "apikey":
        return AuthenticationMethod.API_KEY.value
    if "http basic" in candidate or "basic authentication" in candidate:
        return AuthenticationMethod.BASIC_AUTH.value
    return candidate if candidate in FIELD_ENUMS["authentication_methods"] else "unknown"


def _default_field(field: str) -> dict[str, Any]:
    return {
        "value": [] if field == "authentication_methods" else "unknown",
        "source_ids": [],
        "excerpts": [],
    }


def _normalise_field(
    field: str, raw: Any, normalizations: list[str]
) -> dict[str, Any]:
    default = _default_field(field)
    if not isinstance(raw, dict):
        normalizations.append(f"{field}: malformed or missing wrapper defaulted")
        return default
    source_ids = _deduplicate_strings(raw.get("source_ids"))
    excerpts = _deduplicate_strings(raw.get("excerpts"))
    if raw.get("source_ids") != source_ids:
        normalizations.append(f"{field}: source_ids normalized")
    if raw.get("excerpts") != excerpts:
        normalizations.append(f"{field}: excerpts normalized")
    value = raw.get("value")
    if field == "authentication_methods":
        if not isinstance(value, list):
            normalizations.append(f"{field}: malformed value defaulted")
            methods: list[str] = []
        else:
            methods = list(dict.fromkeys(_normalise_authentication(item) for item in value))
            if len(methods) > 1 and "unknown" in methods:
                methods.remove("unknown")
                normalizations.append(f"{field}: unknown removed beside concrete values")
            if methods != value:
                normalizations.append(f"{field}: values normalized and deduplicated")
        value = methods
    elif field in {"category", "description"}:
        if not isinstance(value, str) or not value.strip() or value.strip().lower() == "null":
            value = "unknown"
            normalizations.append(f"{field}: malformed value defaulted")
        else:
            value = value.strip()
    else:
        candidate = str(value or "").strip().lower()
        if candidate not in FIELD_ENUMS[field]:
            candidate = "unknown"
            normalizations.append(f"{field}: invalid enum defaulted")
        value = candidate
    return {"value": value, "source_ids": source_ids, "excerpts": excerpts}


def normalise_extraction(
    raw: dict[str, Any], requested_fields: tuple[str, ...]
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    normalizations: list[str] = []
    result = {
        field: _normalise_field(field, raw.get(field), normalizations)
        for field in requested_fields
    }
    return result, normalizations


def _relevant_passage(text: str, keywords: tuple[str, ...]) -> str:
    compact = re.sub(r"\r\n?", "\n", text)
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n|(?<=[.!?])\s+", compact)]
    selected: list[str] = []
    for chunk in chunks:
        lowered = chunk.lower()
        if any(keyword in lowered for keyword in keywords):
            selected.append(chunk)
        if sum(len(item) for item in selected) >= MAX_PASSAGE_CHARS:
            break
    return "\n".join(selected)[:MAX_PASSAGE_CHARS]


def curate_source_context(
    sources: list[dict[str, Any]], requested_fields: tuple[str, ...]
) -> tuple[str, dict[str, dict[str, Any]]]:
    keywords = tuple(
        dict.fromkeys(
            keyword for field in requested_fields for keyword in FIELD_KEYWORDS[field]
        )
    )
    blocks: list[str] = []
    source_map: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources, start=1):
        source_id = str(source.get("_prompt_id") or f"source_{index:03d}")
        intent = str(source.get("query_intent", "unknown"))
        passage = _relevant_passage(str(source.get("text", "")), keywords)
        if not passage:
            continue
        block = (
            f"SOURCE_ID: {source_id}\nSOURCE_INTENT: {intent}\n"
            f"TITLE: {source.get('title') or ''}\nURL: {source.get('url', '')}\n"
            f"TEXT:\n{passage}"
        )
        if len("\n\n---\n\n".join(blocks + [block])) > MAX_CONTEXT_CHARS:
            break
        blocks.append(block)
        source_map[source_id] = source
        if len(blocks) >= MAX_SOURCES_PER_CALL:
            break
    return "\n\n---\n\n".join(blocks), source_map


def _request_template(fields: tuple[str, ...]) -> str:
    template = {field: _default_field(field) for field in fields}
    return json.dumps(template, indent=2)


def _allowed_values(fields: tuple[str, ...]) -> str:
    lines: list[str] = []
    for field in fields:
        if field in {"category", "description"}:
            allowed = "a JSON string, or the string unknown"
        elif field == "authentication_methods":
            allowed = "a JSON array containing only: " + ", ".join(
                sorted(FIELD_ENUMS[field])
            )
        else:
            allowed = "exactly one of: " + ", ".join(sorted(FIELD_ENUMS[field]))
        lines.append(f"- {field}.value: {allowed}")
    return "\n".join(lines)


def _provider_raw_call(
    *, client: Any, provider: str, model: str, contents: str
) -> str:
    if provider in {"groq", "openrouter"}:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": contents},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""
    from google.genai import types

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    return response.text or ""


def _extract_call(
    *,
    client: Any,
    provider: str,
    model: str,
    app: dict[str, str],
    sources: list[dict[str, Any]],
    requested_fields: tuple[str, ...],
    group: str,
    log_path: Path | None,
    raw_call: Callable[..., str] = _provider_raw_call,
) -> tuple[dict[str, dict[str, Any]], list[str], dict[str, dict[str, Any]]]:
    context, source_map = curate_source_context(sources, requested_fields)
    if not context.strip():
        raise CoreExtractionError(f"no usable source text for {group}")
    prompt = (
        f"APP: {app['app_name']} ({app['app_id']})\n"
        f"REQUESTED_FIELDS: {', '.join(requested_fields)}\n"
        f"ALLOWED_VALUES (use these exact strings; never booleans or null):\n"
        f"{_allowed_values(requested_fields)}\n"
        f"RETURN_SHAPE:\n{_request_template(requested_fields)}\n\n{context}"
    )
    try:
        text = raw_call(
            client=client, provider=provider, model=model, contents=prompt
        )
    except Exception as error:
        _log_attempt(log_path, group=group, model=model, error=error)
        if _is_quota_error(error):
            raise ModelQuotaExhausted(f"{provider} daily model quota exhausted") from error
        raise
    _log_attempt(log_path, group=group, model=model, error=None)
    parsed, parsing_notes = _first_json_object(text)
    fields, normalization_notes = normalise_extraction(parsed, requested_fields)
    return fields, parsing_notes + normalization_notes, source_map


def _intent_suitable(field: str, source: dict[str, Any]) -> bool:
    intent = str(source.get("query_intent", "")).lower()
    if not intent or intent == "unknown":
        return True
    broad = {
        "category": ("product", "overview", "about"),
        "description": ("product", "overview", "about"),
        "authentication_methods": ("auth", "oauth", "api"),
        "independent_developer_access": ("developer", "signup", "free", "trial"),
        "existing_customer_access": ("customer", "credential", "admin"),
        "multi_tenant_integration_access": ("multi-tenant", "marketplace", "partner"),
    }
    expected = broad.get(field, FIELD_KEYWORDS[field])
    if field in broad:
        return any(token in intent for token in expected)
    return any(token in intent for token in expected) or "api" in intent


def _validate_field_evidence(
    field: str,
    field_output: dict[str, Any],
    source_map: dict[str, dict[str, Any]],
    normalizations: list[str],
    *,
    mcp_search_completed: bool,
) -> tuple[Any, list[tuple[dict[str, Any], str]]]:
    value = field_output["value"]
    concrete = bool(value) if field == "authentication_methods" else value != "unknown"
    if not concrete:
        return value, []
    if field == "mcp_status" and value == McpStatus.NONE_FOUND.value:
        if mcp_search_completed:
            return value, []
        normalizations.append("mcp_status: none_found invalidated because search was incomplete")
        return "unknown", []
    evidence: list[tuple[dict[str, Any], str]] = []
    for source_id, excerpt in zip(
        field_output["source_ids"], field_output["excerpts"], strict=False
    ):
        source = source_map.get(source_id)
        if (
            source
            and _intent_suitable(field, source)
            and excerpt_in_text(excerpt, str(source.get("text", "")))
            and source.get("source_type") in {"official", "official_github"}
        ):
            evidence.append((source, excerpt))
    if evidence:
        return value, evidence
    normalizations.append(f"{field}: concrete value invalidated because evidence was missing")
    return ([] if field == "authentication_methods" else "unknown"), []


def _build_result(
    *,
    app: dict[str, str],
    fields: dict[str, dict[str, Any]],
    sources: list[dict[str, Any]],
    normalizations: list[str],
    mcp_search_completed: bool,
) -> ResearcherAppResult:
    now = datetime.now(UTC)
    source_map = {str(source["_prompt_id"]): source for source in sources}
    validated: dict[str, Any] = {}
    field_evidence: dict[str, list[str]] = {}
    evidence: list[dict[str, Any]] = []
    for field in CORE_FIELDS + SUPPLEMENTARY_FIELDS:
        value, items = _validate_field_evidence(
            field,
            fields.get(field, _default_field(field)),
            source_map,
            normalizations,
            mcp_search_completed=mcp_search_completed,
        )
        validated[field] = value
        ids: list[str] = []
        for source, excerpt in items:
            evidence_id = f"evidence-{len(evidence) + 1:03d}"
            evidence.append({
                "evidence_id": evidence_id,
                "field": {
                    "authentication_methods": "authentication",
                    "independent_developer_access": (
                        "credential_access.independent_developer_access"
                    ),
                    "existing_customer_access": "credential_access.existing_customer_access",
                    "multi_tenant_integration_access": (
                        "credential_access.multi_tenant_integration_access"
                    ),
                    "documented_api": "api_surface.documented_public_api",
                    "webhooks_events": "api_surface.webhooks",
                    "mcp_status": "mcp.status",
                }.get(field, f"api_surface.{field}" if field in SUPPLEMENTARY_FIELDS or field in {
                    "rest", "read_operations", "write_operations", "api_breadth"
                } else field),
                "claim": f"{field} is {value}.",
                "url": source["url"],
                "page_title": source.get("title"),
                "source_type": source["source_type"],
                "excerpt": excerpt,
                "retrieved_at": now.isoformat(),
                "supports_claim": True,
            })
            ids.append(evidence_id)
        field_evidence[field] = ids

    def tri(field: str) -> bool | None:
        return {"supported": True, "not_supported": False}.get(validated[field])

    auth_ids = field_evidence["authentication_methods"]
    credential_ids = list(dict.fromkeys(
        field_evidence["independent_developer_access"]
        + field_evidence["existing_customer_access"]
        + field_evidence["multi_tenant_integration_access"]
    ))
    api_fields = (
        "documented_api", "rest", "read_operations", "write_operations", "api_breadth",
        "graphql", "bulk_operations", "webhooks_events", "websocket", "sdk_available",
    )
    api_ids = list(dict.fromkeys(
        evidence_id for field in api_fields for evidence_id in field_evidence[field]
    ))
    unresolved = list(dict.fromkeys(f"Normalization: {note}" for note in normalizations))
    for field in CORE_FIELDS:
        value = validated[field]
        if (field == "authentication_methods" and not value) or value == "unknown":
            unresolved.append(f"{field}: unresolved")
    for field in SUPPLEMENTARY_FIELDS:
        if validated[field] == "unknown":
            unresolved.append(f"{field}: unresolved")
    payload = {
        "app_id": app["app_id"],
        "app_name": app["app_name"],
        "domain": app["normalized_domain"] or app["website_hint"],
        "category": None if validated["category"] == "unknown" else validated["category"],
        "description": (
            None if validated["description"] == "unknown" else validated["description"]
        ),
        "authentication": {
            "methods": validated["authentication_methods"],
            "notes": None,
            "field_confidence": "high" if auth_ids else "low",
            "evidence_ids": auth_ids,
        },
        "credential_access": {
            "independent_developer_access": validated["independent_developer_access"],
            "existing_customer_access": validated["existing_customer_access"],
            "multi_tenant_integration_access": validated["multi_tenant_integration_access"],
            "field_confidence": "high" if len(credential_ids) >= 3 else (
                "medium" if credential_ids else "low"
            ),
            "evidence_ids": credential_ids,
        },
        "api_surface": {
            "documented_public_api": tri("documented_api"),
            "rest": tri("rest"),
            "graphql": tri("graphql"),
            "webhooks": tri("webhooks_events"),
            "websocket": tri("websocket"),
            "sdk_available": tri("sdk_available"),
            "read_operations": tri("read_operations"),
            "write_operations": tri("write_operations"),
            "bulk_operations": tri("bulk_operations"),
            "api_breadth": validated["api_breadth"],
            "important_resources": [],
            "limitations": [],
            "field_confidence": "high" if all(field_evidence[field] for field in (
                "documented_api", "read_operations", "write_operations", "api_breadth"
            )) else ("medium" if api_ids else "low"),
            "evidence_ids": api_ids,
        },
        "mcp": {
            "status": validated["mcp_status"],
            "official_url": next((
                str(item["url"]) for item in evidence if item["field"] == "mcp.status"
            ), None),
            "transport_or_hosting_notes": None,
            "capabilities": [],
            "limitations": [],
            "field_confidence": "high" if field_evidence["mcp_status"] else "low",
            "evidence_ids": field_evidence["mcp_status"],
        },
        "buildability": {
            "verdict": BuildabilityVerdict.UNKNOWN.value,
            "main_blocker": None,
            "secondary_blockers": [],
            "single_workspace_buildable": None,
            "public_multi_tenant_buildable": None,
            "reasoning_summary": None,
            "field_confidence": Confidence.LOW.value,
            "evidence_ids": [],
        },
        "evidence": evidence,
        "unresolved_questions": list(dict.fromkeys(unresolved)),
        "verification": {
            "status": VerificationStatus.RESEARCHER_COMPLETE.value,
            "overall_confidence": Confidence.LOW.value,
            "researcher_policy_version": "tolerant_core_supplementary_v3",
        },
        "timestamps": {"created_at": now.isoformat(), "updated_at": now.isoformat()},
    }
    return ResearcherAppResult.model_validate(payload)


def _fields_from_result(
    result: ResearcherAppResult, sources: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    source_id_by_url = {
        str(source.get("url")): str(source["_prompt_id"]) for source in sources
    }
    evidence_by_field: dict[str, list[Any]] = {}
    for item in result.evidence:
        evidence_by_field.setdefault(item.field, []).append(item)
    field_names = {
        "category": "category",
        "description": "description",
        "authentication_methods": "authentication",
        "independent_developer_access": "credential_access.independent_developer_access",
        "existing_customer_access": "credential_access.existing_customer_access",
        "multi_tenant_integration_access": "credential_access.multi_tenant_integration_access",
        "documented_api": "api_surface.documented_public_api",
        "rest": "api_surface.rest",
        "read_operations": "api_surface.read_operations",
        "write_operations": "api_surface.write_operations",
        "api_breadth": "api_surface.api_breadth",
        "graphql": "api_surface.graphql",
        "bulk_operations": "api_surface.bulk_operations",
        "webhooks_events": "api_surface.webhooks",
        "websocket": "api_surface.websocket",
        "sdk_available": "api_surface.sdk_available",
        "mcp_status": "mcp.status",
    }
    values: dict[str, Any] = {
        "category": result.category or "unknown",
        "description": result.description or "unknown",
        "authentication_methods": [item.value for item in result.authentication.methods],
        "independent_developer_access": (
            result.credential_access.independent_developer_access.value
        ),
        "existing_customer_access": result.credential_access.existing_customer_access.value,
        "multi_tenant_integration_access": (
            result.credential_access.multi_tenant_integration_access.value
        ),
        "documented_api": (
            "supported" if result.api_surface.documented_public_api is True else
            "not_supported" if result.api_surface.documented_public_api is False else "unknown"
        ),
        "api_breadth": result.api_surface.api_breadth.value,
        "mcp_status": result.mcp.status.value,
    }
    for field, attribute in (
        ("rest", "rest"), ("read_operations", "read_operations"),
        ("write_operations", "write_operations"), ("graphql", "graphql"),
        ("bulk_operations", "bulk_operations"), ("webhooks_events", "webhooks"),
        ("websocket", "websocket"), ("sdk_available", "sdk_available"),
    ):
        value = getattr(result.api_surface, attribute)
        values[field] = "supported" if value is True else (
            "not_supported" if value is False else "unknown"
        )
    fields: dict[str, dict[str, Any]] = {}
    for field, evidence_field in field_names.items():
        items = evidence_by_field.get(evidence_field, [])
        fields[field] = {
            "value": values[field],
            "source_ids": [
                source_id_by_url[str(item.url)] for item in items
                if str(item.url) in source_id_by_url
            ],
            "excerpts": [item.excerpt for item in items if item.excerpt],
        }
    return fields


def retry_core_fields(
    *,
    result: ResearcherAppResult,
    requested_fields: tuple[str, ...],
    model: str,
    app: dict[str, str],
    sources: list[dict[str, Any]],
    google_api_key: str,
    log_path: Path | None,
    mcp_search_completed: bool,
    provider: str,
    raw_call: Callable[..., str] = _provider_raw_call,
) -> ResearcherAppResult:
    """Re-extract only unresolved core fields once and preserve completed fields."""
    configure_ssl()
    if provider == "groq":
        from groq import Groq

        client: Any = Groq(api_key=google_api_key)
    elif provider == "openrouter":
        from openai import OpenAI

        client = OpenAI(api_key=google_api_key, base_url="https://openrouter.ai/api/v1")
    else:
        from google import genai

        client = genai.Client(api_key=google_api_key)
    prepared = [
        {**source, "_prompt_id": f"source_{index:03d}"}
        for index, source in enumerate(sources, start=1)
    ]
    completed = _fields_from_result(result, prepared)
    retried, notes, _ = _extract_call(
        client=client, provider=provider, model=model, app=app, sources=prepared,
        requested_fields=requested_fields, group="targeted_core", log_path=log_path,
        raw_call=raw_call,
    )
    completed.update(retried)
    return _build_result(
        app=app, fields=completed, sources=prepared, normalizations=notes,
        mcp_search_completed=mcp_search_completed,
    )


def extract_result(
    *,
    model: str,
    app: dict[str, str],
    sources: list[dict[str, Any]],
    google_api_key: str,
    fallback_model: str = "",
    log_path: Path | None = None,
    mcp_search_completed: bool = False,
    provider: str = "gemini",
    raw_call: Callable[..., str] = _provider_raw_call,
) -> ResearcherAppResult:
    """Perform one core and at most one supplementary raw-JSON extraction call."""
    del fallback_model  # Reserved by the provider-neutral interface; no quota-chasing retries.
    configure_ssl()
    if provider == "groq":
        try:
            from groq import Groq
        except ImportError as error:
            raise RuntimeError("Groq SDK is not installed") from error
        client: Any = Groq(api_key=google_api_key)
    elif provider == "openrouter":
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("OpenAI-compatible SDK is not installed") from error
        client = OpenAI(
            api_key=google_api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    else:
        try:
            from google import genai
        except ImportError as error:
            raise RuntimeError("Google GenAI SDK is not installed") from error
        client = genai.Client(api_key=google_api_key)
    prepared = [
        {**source, "_prompt_id": f"source_{index:03d}"}
        for index, source in enumerate(sources, start=1)
    ]
    if provider == "openrouter":
        fields, notes, _ = _extract_call(
            client=client,
            provider=provider,
            model=model,
            app=app,
            sources=prepared,
            requested_fields=CORE_FIELDS + SUPPLEMENTARY_FIELDS,
            group="main",
            log_path=log_path,
            raw_call=raw_call,
        )
        return _build_result(
            app=app,
            fields=fields,
            sources=prepared,
            normalizations=notes,
            mcp_search_completed=mcp_search_completed,
        )
    core, notes, _ = _extract_call(
        client=client,
        provider=provider,
        model=model,
        app=app,
        sources=prepared,
        requested_fields=CORE_FIELDS,
        group="core",
        log_path=log_path,
        raw_call=raw_call,
    )
    try:
        supplementary, supplementary_notes, _ = _extract_call(
            client=client,
            provider=provider,
            model=model,
            app=app,
            sources=prepared,
            requested_fields=SUPPLEMENTARY_FIELDS,
            group="supplementary",
            log_path=log_path,
            raw_call=raw_call,
        )
        notes.extend(supplementary_notes)
    except (CoreExtractionError, ModelQuotaExhausted, ValueError, json.JSONDecodeError) as error:
        supplementary = {field: _default_field(field) for field in SUPPLEMENTARY_FIELDS}
        notes.append(f"supplementary extraction degraded safely: {type(error).__name__}")
    fields = {**core, **supplementary}
    return _build_result(
        app=app,
        fields=fields,
        sources=prepared,
        normalizations=notes,
        mcp_search_completed=mcp_search_completed,
    )


def empty_result(
    *, app: dict[str, str], mcp_search_completed: bool = False
) -> ResearcherAppResult:
    """Create an honest unknown result when no usable source text exists."""
    fields = {
        field: _default_field(field) for field in CORE_FIELDS + SUPPLEMENTARY_FIELDS
    }
    return _build_result(
        app=app,
        fields=fields,
        sources=[],
        normalizations=["no usable source text; all fields remain unknown"],
        mcp_search_completed=mcp_search_completed,
    )
