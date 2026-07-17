"""Controlled vocabularies used by research, verification, and review."""

from enum import StrEnum


class AuthenticationMethod(StrEnum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    PERSONAL_ACCESS_TOKEN = "personal_access_token"
    SERVICE_ACCOUNT = "service_account"
    JWT = "jwt"
    SESSION_COOKIE = "session_cookie"
    CUSTOM = "custom"
    NONE = "none"
    UNKNOWN = "unknown"


class IndependentDeveloperAccess(StrEnum):
    SELF_SERVE_FREE = "self_serve_free"
    SELF_SERVE_FREE_CREDITS = "self_serve_free_credits"
    SELF_SERVE_TRIAL = "self_serve_trial"
    SELF_SERVE_PAID = "self_serve_paid"
    ADMIN_APPROVAL_REQUIRED = "admin_approval_required"
    EXISTING_CUSTOMER_REQUIRED = "existing_customer_required"
    PARTNER_PROGRAM_REQUIRED = "partner_program_required"
    CONTACT_SALES_REQUIRED = "contact_sales_required"
    NOT_AVAILABLE = "not_available"
    UNKNOWN = "unknown"


class ExistingCustomerAccess(StrEnum):
    SELF_SERVE_USER = "self_serve_user"
    WORKSPACE_ADMIN_REQUIRED = "workspace_admin_required"
    VENDOR_ENABLEMENT_REQUIRED = "vendor_enablement_required"
    PAID_PLAN_REQUIRED = "paid_plan_required"
    NOT_AVAILABLE = "not_available"
    UNKNOWN = "unknown"


class MultiTenantIntegrationAccess(StrEnum):
    SELF_SERVE = "self_serve"
    APP_REVIEW_REQUIRED = "app_review_required"
    MARKETPLACE_REVIEW_REQUIRED = "marketplace_review_required"
    PARTNER_APPROVAL_REQUIRED = "partner_approval_required"
    CONTACT_VENDOR_REQUIRED = "contact_vendor_required"
    NOT_SUPPORTED = "not_supported"
    UNKNOWN = "unknown"


class ApiBreadth(StrEnum):
    BROAD = "broad"
    MODERATE = "moderate"
    LIMITED = "limited"
    NONE = "none"
    UNKNOWN = "unknown"


class McpStatus(StrEnum):
    OFFICIAL = "official"
    OFFICIAL_PREVIEW = "official_preview"
    COMMUNITY = "community"
    NONE_FOUND = "none_found"
    NOT_SUPPORTED = "not_supported"
    UNKNOWN = "unknown"


class BuildabilityVerdict(StrEnum):
    BUILD_NOW = "build_now"
    BUILD_WITH_CUSTOMER_CREDENTIALS = "build_with_customer_credentials"
    BUILD_AFTER_APP_REVIEW = "build_after_app_review"
    OUTREACH_REQUIRED = "outreach_required"
    LIMITED_TOOLKIT = "limited_toolkit"
    NOT_CURRENTLY_BUILDABLE = "not_currently_buildable"
    UNKNOWN = "unknown"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerificationStatus(StrEnum):
    NOT_STARTED = "not_started"
    RESEARCHER_COMPLETE = "researcher_complete"
    VERIFIER_COMPLETE = "verifier_complete"
    DISAGREEMENT = "disagreement"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    HUMAN_REVIEWED = "human_reviewed"
    FINALIZED = "finalized"


class ReviewPriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"

