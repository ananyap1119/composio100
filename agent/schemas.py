"""Strict Pydantic models for every Phase 1 pipeline boundary."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

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


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class EvidenceItem(StrictModel):
    evidence_id: str = Field(min_length=1)
    field: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    url: HttpUrl
    page_title: str | None = None
    source_type: Literal["official", "official_github", "secondary"]
    excerpt: str | None = None
    retrieved_at: datetime
    published_or_updated_at: datetime | None = None
    supports_claim: bool | None = None
    notes: str | None = None


class AuthenticationSection(StrictModel):
    methods: list[AuthenticationMethod] = Field(default_factory=list)
    notes: str | None = None
    field_confidence: Confidence
    evidence_ids: list[str] = Field(default_factory=list)


class CredentialAccessSection(StrictModel):
    independent_developer_access: IndependentDeveloperAccess
    existing_customer_access: ExistingCustomerAccess
    multi_tenant_integration_access: MultiTenantIntegrationAccess
    free_or_trial_notes: str | None = None
    paid_plan_notes: str | None = None
    admin_or_approval_notes: str | None = None
    field_confidence: Confidence
    evidence_ids: list[str] = Field(default_factory=list)


class ApiSurfaceSection(StrictModel):
    documented_public_api: bool | None = None
    rest: bool | None = None
    graphql: bool | None = None
    webhooks: bool | None = None
    websocket: bool | None = None
    sdk_available: bool | None = None
    read_operations: bool | None = None
    write_operations: bool | None = None
    bulk_operations: bool | None = None
    api_breadth: ApiBreadth
    important_resources: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    field_confidence: Confidence
    evidence_ids: list[str] = Field(default_factory=list)


class McpSection(StrictModel):
    status: McpStatus
    official_url: HttpUrl | None = None
    transport_or_hosting_notes: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    field_confidence: Confidence
    evidence_ids: list[str] = Field(default_factory=list)


class BuildabilitySection(StrictModel):
    verdict: BuildabilityVerdict
    main_blocker: str | None = None
    secondary_blockers: list[str] = Field(default_factory=list)
    single_workspace_buildable: bool | None = None
    public_multi_tenant_buildable: bool | None = None
    # Scoped paths prevent a gated public distribution path from erasing a
    # separately established customer-specific build path.
    customer_specific_verdict: str | None = None
    multi_customer_distribution_verdict: str | None = None
    overall_recommended_path: str | None = None
    reasoning_summary: str | None = None
    field_confidence: Confidence
    evidence_ids: list[str] = Field(default_factory=list)


class VerificationSection(StrictModel):
    status: VerificationStatus = VerificationStatus.NOT_STARTED
    researcher_completed_at: datetime | None = None
    verifier_completed_at: datetime | None = None
    human_reviewed_at: datetime | None = None
    researcher_model: str | None = None
    verifier_model: str | None = None
    researcher_verifier_disagreements: list[str] = Field(default_factory=list)
    human_corrections: list[str] = Field(default_factory=list)
    human_failure_types: dict[str, str | None] = Field(default_factory=dict)
    researcher_policy_version: str | None = None
    finalized_by: str | None = None
    human_reviewed: bool = False
    audit_status: str = "not_sampled"
    overall_confidence: Confidence


class ResultTimestamps(StrictModel):
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def updated_not_before_created(self) -> "ResultTimestamps":
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot be earlier than created_at")
        return self


class AppResearchResult(StrictModel):
    app_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    app_name: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    category: str | None = None
    description: str | None = None
    authentication: AuthenticationSection
    credential_access: CredentialAccessSection
    api_surface: ApiSurfaceSection
    mcp: McpSection
    buildability: BuildabilitySection
    evidence: list[EvidenceItem] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    verification: VerificationSection
    timestamps: ResultTimestamps

    @model_validator(mode="after")
    def evidence_ids_exist(self) -> "AppResearchResult":
        known = {item.evidence_id for item in self.evidence}
        if len(known) != len(self.evidence):
            raise ValueError("evidence_id values must be unique")
        sections = (
            self.authentication,
            self.credential_access,
            self.api_surface,
            self.mcp,
            self.buildability,
        )
        missing = {value for section in sections for value in section.evidence_ids} - known
        if missing:
            raise ValueError(f"unknown evidence IDs referenced: {sorted(missing)}")
        return self


class ResearcherAppResult(AppResearchResult):
    """Researcher's independent structured result."""


class FinalAppResult(AppResearchResult):
    source_order: int = Field(ge=1, le=100)


class ManualAuditEntry(StrictModel):
    app_id: str
    field: str
    researcher_value: object
    human_value: object
    correct: bool
    reason: str
    supporting_source_urls: list[HttpUrl] = Field(default_factory=list)
    failure_type: str | None = None
    reviewed_at: datetime


class ManualAudit(StrictModel):
    app_id: str
    reviewed_at: datetime
    decisions: list[ManualAuditEntry]
