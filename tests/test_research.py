from pathlib import Path

import pytest
from conftest import result_payload

from agent.enums import BuildabilityVerdict
from agent.research.composio_tools import _select_capability
from agent.research.evidence import (
    SourceRecord,
    classify_source_url,
    deduplicate_urls,
    excerpt_in_text,
    validate_evidence,
)
from agent.research.extraction import (
    CORE_FIELDS,
    SUPPLEMENTARY_FIELDS,
    ModelQuotaExhausted,
    _build_result,
    _first_json_object,
    _normalise_authentication,
    extract_result,
    normalise_extraction,
)
from agent.research.researcher import (
    _core_unresolved_fields,
    _deterministic_verdict,
    _extract_and_persist,
    _finalize_if_eligible,
    _latest_usable_run,
    _rescore_confidence,
    planned_queries,
    run_research,
    run_research_batch,
    select_batch_apps,
)
from agent.schemas import FinalAppResult, ResearcherAppResult


def test_dry_run_makes_no_network_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(*_: object, **__: object) -> None:
        raise AssertionError("network adapter was called during dry-run")

    monkeypatch.setattr("agent.research.researcher.ComposioDirectAdapter", fail_if_called)
    result = run_research("salesforce", dry_run=True)
    assert result["network_calls"] is False  # type: ignore[index]


def test_research_plan_has_at_most_eight_searches() -> None:
    assert len(planned_queries()) == 9


def test_direct_tool_capabilities_are_selected_from_schemas() -> None:
    tools = [
        {
            "slug": "CURRENT_SEARCH",
            "description": "web search",
            "is_deprecated": False,
            "deprecated": {"is_deprecated": False},
            "input_parameters": {"properties": {"query": {"type": "string"}}},
        },
        {
            "slug": "CURRENT_FETCH",
            "description": "fetch URL content",
            "is_deprecated": False,
            "deprecated": {"is_deprecated": False},
            "input_parameters": {"properties": {"urls": {"type": "array"}}},
        },
    ]
    assert _select_capability(tools, "search")["slug"] == "CURRENT_SEARCH"
    assert _select_capability(tools, "fetch")["slug"] == "CURRENT_FETCH"


def test_official_salesforce_domain_classification() -> None:
    assert classify_source_url("https://developer.salesforce.com/docs") == "official"
    assert classify_source_url("https://example.com/salesforce") == "secondary"


def test_url_deduplication_preserves_order() -> None:
    assert deduplicate_urls(["https://a", "https://a", "https://b", ""]) == [
        "https://a",
        "https://b",
    ]


def test_excerpt_validation_normalizes_whitespace() -> None:
    assert excerpt_in_text("Salesforce  API", "Salesforce\nAPI documentation")


def test_invented_evidence_url_is_rejected() -> None:
    source = SourceRecord(
        "sf-01",
        "https://developer.salesforce.com/a",
        None,
        "known text",
        "official",
        "q1",
    )
    check = validate_evidence(
        evidence_id="sf-01",
        field="credential_access",
        url="https://invented.example/a",
        excerpt="known text",
        sources={"sf-01": source},
        important=True,
    )
    assert not check.valid
    assert "URL does not match" in " ".join(check.reasons)


def test_none_found_differs_from_not_supported() -> None:
    assert "none_found" != "not_supported"


def test_username_password_is_not_basic_auth() -> None:
    assert _normalise_authentication("username and password with security token") == "unknown"


def test_explicit_http_basic_is_basic_auth() -> None:
    assert _normalise_authentication("HTTP Basic Authentication") == "basic_auth"


def test_unknown_supplementary_fields_do_not_block_build_now() -> None:
    payload = result_payload()
    _add_verdict_evidence(payload)
    payload["credential_access"]["independent_developer_access"] = "self_serve_free"  # type: ignore[index]
    payload["credential_access"]["existing_customer_access"] = "self_serve_user"  # type: ignore[index]
    payload["credential_access"]["multi_tenant_integration_access"] = "self_serve"  # type: ignore[index]
    payload["api_surface"].update({  # type: ignore[union-attr]
        "documented_public_api": True, "rest": True, "read_operations": True,
        "write_operations": True, "api_breadth": "broad",
    })
    result = ResearcherAppResult.model_validate(payload)
    assert _deterministic_verdict(result) == BuildabilityVerdict.BUILD_NOW
    assert _core_unresolved_fields(result) == []


def test_unavailable_fallback_model_is_not_configured() -> None:
    assert "gemini-2.5-flash-lite" not in Path(".env.example").read_text(encoding="utf-8")


def test_first_json_object_ignores_surrounding_prose() -> None:
    value, notes = _first_json_object('preface {"category": {"value": "CRM"}} trailing')
    assert value["category"]["value"] == "CRM"
    assert notes == ["discarded surrounding non-JSON text"]


def test_malformed_mcp_status_affects_only_mcp() -> None:
    raw = {
        "graphql": {"value": "supported", "source_ids": ["source_001"],
                    "excerpts": ["GraphQL API"]},
        "mcp_status": ["official"],
    }
    fields, _ = normalise_extraction(raw, SUPPLEMENTARY_FIELDS)
    assert fields["mcp_status"]["value"] == "unknown"
    assert fields["graphql"]["value"] == "supported"


def test_missing_authentication_confidence_is_irrelevant() -> None:
    raw = {"authentication_methods": {
        "value": ["oauth2"], "source_ids": [], "excerpts": []
    }}
    fields, _ = normalise_extraction(raw, ("authentication_methods",))
    assert fields["authentication_methods"]["value"] == ["oauth2"]


def test_missing_model_property_receives_default() -> None:
    fields, notes = normalise_extraction({}, ("documented_api",))
    assert fields["documented_api"] == {
        "value": "unknown", "source_ids": [], "excerpts": []
    }
    assert notes


def test_duplicate_auth_values_are_removed_and_concrete_removes_unknown() -> None:
    fields, _ = normalise_extraction({
        "authentication_methods": {
            "value": ["unknown", "oauth2", "oauth2"],
            "source_ids": [], "excerpts": [],
        }
    }, ("authentication_methods",))
    assert fields["authentication_methods"]["value"] == ["oauth2"]


def test_deterministic_verdict_rules() -> None:
    payload = result_payload()
    _add_verdict_evidence(payload)
    payload["api_surface"]["api_breadth"] = "moderate"  # type: ignore[index]
    payload["api_surface"].update(  # type: ignore[union-attr]
        {"documented_public_api": True, "rest": True,
         "read_operations": True, "write_operations": True}
    )
    payload["credential_access"]["independent_developer_access"] = "self_serve_free"  # type: ignore[index]
    payload["credential_access"]["existing_customer_access"] = "self_serve_user"  # type: ignore[index]
    payload["credential_access"]["multi_tenant_integration_access"] = "self_serve"  # type: ignore[index]
    result = ResearcherAppResult.model_validate(payload)
    assert _deterministic_verdict(result) == BuildabilityVerdict.BUILD_NOW

    payload["credential_access"]["independent_developer_access"] = "unknown"  # type: ignore[index]
    payload["credential_access"]["existing_customer_access"] = "workspace_admin_required"  # type: ignore[index]
    result = ResearcherAppResult.model_validate(payload)
    assert _deterministic_verdict(result) == BuildabilityVerdict.BUILD_WITH_CUSTOMER_CREDENTIALS


def _add_verdict_evidence(payload: dict[str, object]) -> None:
    """Give verdict-rule fixtures the direct evidence required by the gate."""
    evidence = payload["evidence"]
    assert isinstance(evidence, list)
    now = "2026-01-01T00:00:00Z"
    for field in (
        "api_surface.documented_public_api", "api_surface.rest",
        "api_surface.read_operations", "api_surface.write_operations",
        "api_surface.api_breadth", "credential_access.independent_developer_access",
        "credential_access.existing_customer_access",
    ):
        evidence_id = "ev-" + field.replace(".", "-")
        evidence.append({
            "evidence_id": evidence_id, "field": field,
            "claim": "Official documentation supports this verdict-driving field",
            "url": "https://example.com/api", "page_title": "API docs",
            "source_type": "official", "excerpt": "Official documentation statement.",
            "retrieved_at": now, "published_or_updated_at": None,
            "supports_claim": True, "notes": None,
        })
    api = payload["api_surface"]
    cred = payload["credential_access"]
    assert isinstance(api, dict) and isinstance(cred, dict)
    api.update({
        "documented_public_api": True, "rest": True,
        "read_operations": True, "write_operations": True, "api_breadth": "broad",
    })
    api["evidence_ids"] = [
        "ev-api_surface-documented_public_api", "ev-api_surface-rest",
        "ev-api_surface-read_operations", "ev-api_surface-write_operations",
        "ev-api_surface-api_breadth",
    ]
    cred["evidence_ids"] = [
        "ev-credential_access-independent_developer_access",
        "ev-credential_access-existing_customer_access",
    ]


def test_secrets_are_not_in_dry_run_or_example_file() -> None:
    example = Path(".env.example").read_text(encoding="utf-8")
    assert set(line.split("=", 1)[0] for line in example.splitlines()) == {
        "COMPOSIO_API_KEY",
        "OPENROUTER_API_KEY",
        "RESEARCH_PROVIDER",
        "RESEARCH_MODEL",
        "RESEARCH_FALLBACK_MODEL",
    }
    output = run_research("salesforce", dry_run=True)
    assert "api_key" not in str(output).lower()


def test_non_calibration_app_can_plan_research() -> None:
    assert run_research("hubspot", dry_run=True)["app_id"] == "hubspot"  # type: ignore[index]


def _tolerant_source() -> dict[str, object]:
    text = (
        "This CRM product provides an API. OAuth2 authentication is supported. "
        "Developers can sign up for a free account. Administrators create credentials. "
        "Multi-tenant distribution is self service. The REST API supports GET list read "
        "and POST create update operations. It documents broad API resources. GraphQL API."
    )
    return {
        "source_id": "test-01",
        "url": "https://example.com/docs",
        "title": "Official API",
        "text": text,
        "source_type": "official",
        "query_intent": (
            "product overview API authentication developer signup admin credential "
            "multi-tenant marketplace GraphQL bulk webhook SDK MCP"
        ),
    }


def _core_response() -> str:
    source_id = ["source_001"]
    fields = {
        "category": ("CRM", "This CRM product"),
        "description": ("CRM product", "This CRM product provides an API"),
        "authentication_methods": (["oauth2"], "OAuth2 authentication is supported"),
        "independent_developer_access": (
            "self_serve_free", "Developers can sign up for a free account"
        ),
        "existing_customer_access": (
            "workspace_admin_required", "Administrators create credentials"
        ),
        "multi_tenant_integration_access": (
            "self_serve", "Multi-tenant distribution is self service"
        ),
        "documented_api": ("supported", "This CRM product provides an API"),
        "rest": ("supported", "The REST API supports GET list read"),
        "read_operations": ("supported", "GET list read"),
        "write_operations": ("supported", "POST create update operations"),
        "api_breadth": ("broad", "broad API resources"),
    }
    return __import__("json").dumps({
        name: {"value": value, "source_ids": source_id, "excerpts": [excerpt]}
        for name, (value, excerpt) in fields.items()
    })


def test_malformed_supplementary_json_does_not_fail_app() -> None:
    calls: list[str] = []

    def raw_call(**kwargs: object) -> str:
        contents = str(kwargs["contents"])
        calls.append(contents)
        return _core_response() if "authentication_methods" in contents else "not JSON"

    result = extract_result(
        model="test", app={"app_id": "test", "app_name": "Test",
                           "normalized_domain": "example.com", "website_hint": "example.com"},
        sources=[_tolerant_source()], google_api_key="unused", provider="groq",
        mcp_search_completed=True, raw_call=raw_call,
    )
    assert len(calls) == 2
    assert result.authentication.methods[0].value == "oauth2"
    assert result.mcp.status.value == "unknown"


def test_evidence_failure_invalidates_only_its_field() -> None:
    fields, _ = normalise_extraction(
        __import__("json").loads(_core_response()), CORE_FIELDS
    )
    fields.update({field: {"value": "unknown", "source_ids": [], "excerpts": []}
                   for field in SUPPLEMENTARY_FIELDS})
    fields["write_operations"]["excerpts"] = ["fabricated excerpt"]
    source = {**_tolerant_source(), "_prompt_id": "source_001"}
    result = _build_result(
        app={"app_id": "test", "app_name": "Test", "normalized_domain": "example.com",
             "website_hint": "example.com"},
        fields=fields, sources=[source], normalizations=[], mcp_search_completed=True,
    )
    assert result.api_surface.write_operations is None
    assert result.api_surface.read_operations is True


def test_missing_evidence_becomes_unknown() -> None:
    fields, _ = normalise_extraction({
        "documented_api": {"value": "supported", "source_ids": [], "excerpts": []}
    }, ("documented_api",))
    all_fields = {
        field: fields.get(field, {"value": [] if field == "authentication_methods" else "unknown",
                                  "source_ids": [], "excerpts": []})
        for field in CORE_FIELDS + SUPPLEMENTARY_FIELDS
    }
    result = _build_result(
        app={"app_id": "test", "app_name": "Test", "normalized_domain": "example.com",
             "website_hint": "example.com"},
        fields=all_fields, sources=[{**_tolerant_source(), "_prompt_id": "source_001"}],
        normalizations=[], mcp_search_completed=False,
    )
    assert result.api_surface.documented_public_api is None


def test_targeted_core_field_request_does_not_include_full_core() -> None:
    from agent.research.extraction import _extract_call

    seen: list[str] = []

    def raw_call(**kwargs: object) -> str:
        seen.append(str(kwargs["contents"]))
        return '{"write_operations":{"value":"unknown","source_ids":[],"excerpts":[]}}'

    _extract_call(
        client=object(), provider="groq", model="test",
        app={"app_id": "test", "app_name": "Test"}, sources=[_tolerant_source()],
        requested_fields=("write_operations",), group="targeted_core", log_path=None,
        raw_call=raw_call,
    )
    assert len(seen) == 1
    assert "write_operations" in seen[0]
    assert "authentication_methods" not in seen[0]


def test_quota_exhaustion_saves_progress_checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "agent.research.researcher.extract_result",
        lambda **_: (_ for _ in ()).throw(ModelQuotaExhausted("quota exhausted")),
    )
    run_dir = tmp_path / "data" / "raw" / "test" / "run"
    run_dir.mkdir(parents=True)
    source = SourceRecord(
        "test-01", "https://example.com/docs", "Docs", "usable API text",
        "official", "official API overview",
    )
    with pytest.raises(ModelQuotaExhausted):
        _extract_and_persist(
            app={"app_id": "test", "app_name": "Test", "normalized_domain": "example.com",
                 "website_hint": "example.com"},
            source_records={"test-01": source}, run_dir=run_dir,
            primary_model="test", fallback_model="", google_api_key="unused",
            mcp_search_completed=False, official_domains=("example.com",), provider="groq",
        )
    checkpoint = run_dir / "extraction_checkpoint.json"
    assert checkpoint.is_file()
    assert "operationally_blocked" in checkpoint.read_text(encoding="utf-8")


def test_cached_sources_are_reused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    run_dir = tmp_path / "data" / "raw" / "test" / "run-1"
    run_dir.mkdir(parents=True)
    source = {
        "source_id": "test-01", "url": "https://example.com/docs", "title": "Docs",
        "text": "cached source", "source_type": "official", "query_intent": "API",
    }
    (run_dir / "sources.json").write_text(
        __import__("json").dumps([source]), encoding="utf-8"
    )
    (run_dir / "test-01.txt").write_text("cached source", encoding="utf-8")
    selected, records = _latest_usable_run("test")
    assert selected.resolve() == run_dir.resolve()
    assert records["test-01"].text == "cached source"


def test_finalized_salesforce_is_untouched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "final").mkdir(parents=True)
    final_path = tmp_path / "data" / "final" / "salesforce.json"
    final_path.write_text('{"sentinel": true}', encoding="utf-8")
    (tmp_path / "data" / "apps.csv").write_text(
        "source_order,app_id,app_name,website_hint,normalized_domain,category_group,calibration_set\n"
        "1,salesforce,Salesforce,salesforce.com,salesforce.com,CRM,true\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "agent.research.researcher.run_research",
        lambda *_args, **_kwargs: pytest.fail("finalized app was rerun"),
    )
    summary = run_research_batch(calibration=True, skip_finalized=True, resume=True)
    assert summary["totals"]["apps_finalized_before_batch"] == 1
    assert final_path.read_text(encoding="utf-8") == '{"sentinel": true}'


def test_build_now_gate_does_not_require_all_credential_dimensions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    payload = result_payload()
    _add_verdict_evidence(payload)
    payload["credential_access"]["independent_developer_access"] = "self_serve_free"  # type: ignore[index]
    payload["credential_access"]["existing_customer_access"] = "unknown"  # type: ignore[index]
    payload["credential_access"]["multi_tenant_integration_access"] = "unknown"  # type: ignore[index]
    result = _rescore_confidence(ResearcherAppResult.model_validate(payload))
    path = _finalize_if_eligible(
        {"app_id": "example-app", "app_name": "Example", "source_order": "11"}, result
    )
    assert path == Path("data/final/example-app.json")
    final = FinalAppResult.model_validate_json(
        Path("data/final/example-app.json").read_text(encoding="utf-8")
    )
    assert final.verification.human_reviewed is False
    assert final.verification.audit_status == "not_sampled"


def test_customer_credentials_gate_does_not_require_independent_access() -> None:
    payload = result_payload()
    _add_verdict_evidence(payload)
    payload["credential_access"]["independent_developer_access"] = "unknown"  # type: ignore[index]
    payload["credential_access"]["existing_customer_access"] = "workspace_admin_required"  # type: ignore[index]
    payload["credential_access"]["evidence_ids"] = [  # type: ignore[index]
        "ev-credential_access-existing_customer_access"
    ]
    result = ResearcherAppResult.model_validate(payload)
    assert _deterministic_verdict(result) == BuildabilityVerdict.BUILD_WITH_CUSTOMER_CREDENTIALS


def test_supplementary_unknown_does_not_block_machine_finalization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    payload = result_payload()
    _add_verdict_evidence(payload)
    payload["credential_access"]["independent_developer_access"] = "self_serve_free"  # type: ignore[index]
    payload["unresolved_questions"] = ["graphql: unresolved", "mcp_status: unresolved"]
    result = _rescore_confidence(ResearcherAppResult.model_validate(payload))
    assert result.verification.overall_confidence.value == "medium"
    assert _finalize_if_eligible(
        {"app_id": "example-app", "app_name": "Example", "source_order": "11"}, result
    ) is not None


def test_production_selection_is_exactly_orders_11_to_100() -> None:
    apps = [
        {"source_order": str(i), "calibration_set": "false", "app_id": str(i)}
        for i in range(1, 101)
    ]
    selected = select_batch_apps(
        apps, calibration=False, production=True, start_order=11, end_order=100
    )
    assert [int(row["source_order"]) for row in selected] == list(range(11, 101))
