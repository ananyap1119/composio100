"""Source records, official-source filtering, and deterministic evidence checks."""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    url: str
    title: str | None
    text: str
    source_type: str
    query_intent: str


@dataclass(frozen=True)
class EvidenceCheck:
    valid: bool
    reasons: tuple[str, ...] = ()


def is_official_salesforce_url(url: str) -> bool:
    """Classify Salesforce-controlled hosts as official (legacy helper)."""
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return host == "salesforce.com" or host.endswith(".salesforce.com")


def classify_source_url(url: str, official_domains: Iterable[str] | None = None) -> str:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    domains = list(official_domains or ("salesforce.com",))
    official = any(host == domain or host.endswith("." + domain) for domain in domains)
    return "official" if official else "secondary"


def deduplicate_urls(urls: Iterable[str]) -> list[str]:
    """Deduplicate URLs while retaining first-seen order."""
    return list(dict.fromkeys(url for url in urls if url))


def normalize_excerpt(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def excerpt_in_text(excerpt: str, page_text: str) -> bool:
    return normalize_excerpt(excerpt) in normalize_excerpt(page_text)


def validate_evidence(
    *,
    evidence_id: str,
    field: str,
    url: str,
    excerpt: str | None,
    sources: dict[str, SourceRecord],
    important: bool = False,
) -> EvidenceCheck:
    reasons: list[str] = []
    source = sources.get(evidence_id)
    if source is None:
        reasons.append("referenced source does not exist")
    else:
        if source.url != url:
            reasons.append("evidence URL does not match the referenced source")
        if excerpt and not excerpt_in_text(excerpt, source.text):
            reasons.append("excerpt is not present in fetched source text")
        if important and source.source_type not in {"official", "official_github"}:
            reasons.append("important claim lacks official evidence")
    return EvidenceCheck(valid=not reasons, reasons=tuple(reasons))
