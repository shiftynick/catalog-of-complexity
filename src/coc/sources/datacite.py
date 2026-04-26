"""DOI resolver: DataCite metadata (fallback for DOIs not minted at Crossref).

Crossref covers the bulk of journal-article DOIs; dataset DOIs (NIST
``10.18434/*``, Zenodo ``10.5281/*``, figshare ``10.6084/*``, and many
publisher-archived datasets) are minted at DataCite instead. This resolver
queries DataCite's unauthenticated JSON:API endpoint and produces a
ResolvedSource with metadata.json as the sole raw artifact — datasets do
not have an Unpaywall record, and following the landing URL would risk
saving HTML that often requires a session cookie.

The dispatcher (``coc.sources.dispatch``) tries Crossref first and falls
back here on NotFoundError.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from coc.sources.base import (
    Fetcher,
    FetchError,
    NotFoundError,
    ResolvedArtifact,
    ResolvedSource,
)
from coc.sources.http import http_get
from coc.sources.slugs import slugify

DATACITE_API = "https://api.datacite.org/dois/{doi}"


def _default_fetcher(url: str, headers: dict[str, str] | None) -> tuple[int, dict[str, str], bytes]:
    return http_get(url, headers=headers)


def _strip_prefix(ref: str) -> str:
    if not ref.startswith("doi:"):
        raise ValueError(f"not a doi ref: {ref!r}")
    return ref[4:]


def _datacite_kind(resource_type_general: str) -> str:
    """Map DataCite ``resourceTypeGeneral`` to source.schema.json ``kind`` enum."""
    mapping = {
        "Dataset": "dataset",
        "DataPaper": "dataset",
        "ComputationalNotebook": "dataset",
        "Collection": "dataset",
        "Book": "book",
        "BookChapter": "book",
        "JournalArticle": "peer-reviewed",
        "ConferencePaper": "peer-reviewed",
        "ConferenceProceeding": "peer-reviewed",
        "PeerReview": "peer-reviewed",
        "Preprint": "preprint",
        "Report": "technical-report",
        "Standard": "technical-report",
        "OutputManagementPlan": "technical-report",
        "Software": "model",
        "Model": "model",
        "Workflow": "model",
        "Dissertation": "unpublished",
        "StudyRegistration": "unpublished",
    }
    return mapping.get(resource_type_general, "peer-reviewed")


def _extract_title(attrs: dict) -> str:
    titles = attrs.get("titles") or []
    for t in titles:
        if isinstance(t, dict):
            v = (t.get("title") or "").strip()
            if v:
                return v
    return ""


def _extract_authors(attrs: dict) -> list[str]:
    out: list[str] = []
    for c in attrs.get("creators") or []:
        if not isinstance(c, dict):
            continue
        given = (c.get("givenName") or "").strip()
        family = (c.get("familyName") or "").strip()
        name = (c.get("name") or "").strip()
        if family and given:
            out.append(f"{given} {family}")
        elif family:
            out.append(family)
        elif name:
            out.append(name)
    return out


def _extract_year(attrs: dict) -> int | None:
    year = attrs.get("publicationYear")
    if isinstance(year, int):
        return year
    if isinstance(year, str) and year.isdigit():
        return int(year)
    # Fallback to dates[].date if publicationYear is missing.
    for d in attrs.get("dates") or []:
        if isinstance(d, dict):
            v = d.get("date")
            if isinstance(v, str) and len(v) >= 4 and v[:4].isdigit():
                return int(v[:4])
    return None


def _extract_license(attrs: dict) -> str | None:
    rights = attrs.get("rightsList") or []
    if rights and isinstance(rights, list):
        first = rights[0] or {}
        return first.get("rightsUri") or first.get("rightsIdentifier") or first.get("rights")
    return None


def _citation(attrs: dict, doi: str) -> str:
    authors = _extract_authors(attrs)
    year = _extract_year(attrs)
    title = _extract_title(attrs) or f"DOI {doi}"
    publisher = (attrs.get("publisher") or "").strip()
    parts: list[str] = []
    if authors:
        parts.append(", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""))
    if year:
        parts.append(f"({year})")
    parts.append(title)
    if publisher:
        parts.append(publisher)
    parts.append(f"https://doi.org/{doi}")
    return ". ".join(parts)


def resolve(ref: str, fetcher: Fetcher | None = None) -> ResolvedSource:
    """Resolve a ``doi:`` ref against DataCite to a ResolvedSource."""
    fetch = fetcher or _default_fetcher
    doi = _strip_prefix(ref)

    url = DATACITE_API.format(doi=doi)
    status, _hdrs, body = fetch(url, {"Accept": "application/vnd.api+json"})
    if status == 404:
        raise NotFoundError(f"DataCite has no record for {doi}")
    if status != 200:
        raise FetchError(f"DataCite returned {status} for {doi}")

    payload = json.loads(body.decode("utf-8"))
    data = payload.get("data") or {}
    attrs = data.get("attributes") or {}

    title = _extract_title(attrs) or f"DOI {doi}"
    types = attrs.get("types") or {}
    kind = _datacite_kind(types.get("resourceTypeGeneral") or "")
    authors = _extract_authors(attrs)
    year = _extract_year(attrs)
    license_str = _extract_license(attrs)
    landing_url = (attrs.get("url") or "").strip() or f"https://doi.org/{doi}"

    artifacts: list[ResolvedArtifact] = [
        ResolvedArtifact("metadata.json", body, "application/json"),
    ]

    return ResolvedSource(
        slug=slugify(title, fallback=slugify(doi)),
        title=title,
        kind=kind,
        retrieved_at=datetime.now(UTC),
        authors=authors,
        year=year,
        doi=doi,
        url=landing_url,
        license=license_str,
        citation=_citation(attrs, doi),
        artifacts=artifacts,
    )
