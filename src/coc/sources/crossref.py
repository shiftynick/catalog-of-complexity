"""DOI resolver: Crossref metadata + Unpaywall OA lookup.

Flow:

1. Strip the ``doi:`` prefix.
2. GET Crossref API for bibliographic metadata.
3. GET Unpaywall for an OA full-text URL (if any).
4. If an OA URL is returned, fetch the PDF/HTML.
5. Assemble ResolvedSource with raw/ artifacts:
   - ``metadata.json`` — full Crossref payload.
   - ``unpaywall.json`` — Unpaywall payload (always included; free to fetch).
   - ``paper.<ext>`` — the OA full-text, if any.

Paywalled sources still write a source.yaml with metadata; the writer will
flag ``hash`` correctly even if only ``metadata.json`` is present.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime

from coc.sources.base import (
    Fetcher,
    FetchError,
    NotFoundError,
    PaywallError,
    ResolvedArtifact,
    ResolvedSource,
)
from coc.sources.http import extension_for, http_get
from coc.sources.slugs import slugify

CROSSREF_API = "https://api.crossref.org/works/{doi}"
UNPAYWALL_API = "https://api.unpaywall.org/v2/{doi}?email={email}"


def _contact_email() -> str:
    return os.environ.get("COC_CONTACT_EMAIL", "admin@catalog-of-complexity.local")


def _default_fetcher(url: str, headers: dict[str, str] | None) -> tuple[int, dict[str, str], bytes]:
    return http_get(url, headers=headers)


def _strip_prefix(ref: str) -> str:
    if not ref.startswith("doi:"):
        raise ValueError(f"not a doi ref: {ref!r}")
    return ref[4:]


def _crossref_kind(crossref_type: str) -> str:
    """Map Crossref ``type`` to source.schema.json ``kind`` enum."""
    mapping = {
        "journal-article": "peer-reviewed",
        "proceedings-article": "peer-reviewed",
        "book-chapter": "book",
        "book": "book",
        "monograph": "book",
        "edited-book": "book",
        "reference-book": "book",
        "report": "technical-report",
        "report-component": "technical-report",
        "posted-content": "preprint",
        "dataset": "dataset",
    }
    return mapping.get(crossref_type, "peer-reviewed")


def _extract_authors(crossref_msg: dict) -> list[str]:
    out: list[str] = []
    for a in crossref_msg.get("author") or []:
        given = (a.get("given") or "").strip()
        family = (a.get("family") or "").strip()
        name = (a.get("name") or "").strip()
        if family and given:
            out.append(f"{given} {family}")
        elif family:
            out.append(family)
        elif name:
            out.append(name)
    return out


def _extract_year(crossref_msg: dict) -> int | None:
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (crossref_msg.get(key) or {}).get("date-parts") or []
        if parts and parts[0] and isinstance(parts[0][0], int):
            return parts[0][0]
    return None


def _extract_license(crossref_msg: dict) -> str | None:
    licenses = crossref_msg.get("license") or []
    if licenses and isinstance(licenses, list):
        return (licenses[0] or {}).get("URL")
    return None


def _citation(crossref_msg: dict) -> str:
    authors = _extract_authors(crossref_msg)
    year = _extract_year(crossref_msg)
    titles = crossref_msg.get("title") or []
    title = titles[0] if titles else "Untitled"
    container = (crossref_msg.get("container-title") or [""])[0]
    doi = crossref_msg.get("DOI", "")
    parts: list[str] = []
    if authors:
        parts.append(", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""))
    if year:
        parts.append(f"({year})")
    parts.append(title)
    if container:
        parts.append(container)
    if doi:
        parts.append(f"https://doi.org/{doi}")
    return ". ".join(parts)


def resolve(ref: str, fetcher: Fetcher | None = None) -> ResolvedSource:
    """Resolve a ``doi:`` ref to a ResolvedSource."""
    fetch = fetcher or _default_fetcher
    doi = _strip_prefix(ref)

    # 1. Crossref metadata.
    cr_url = CROSSREF_API.format(doi=doi)
    status, _hdrs, body = fetch(cr_url, {"Accept": "application/json"})
    if status == 404:
        raise NotFoundError(f"Crossref has no record for {doi}")
    if status != 200:
        raise FetchError(f"Crossref returned {status} for {doi}")
    cr_payload = json.loads(body.decode("utf-8"))
    msg = cr_payload.get("message") or {}

    titles = msg.get("title") or []
    title = (titles[0] if titles else "").strip() or f"DOI {doi}"
    kind = _crossref_kind(msg.get("type") or "")
    authors = _extract_authors(msg)
    year = _extract_year(msg)
    license_str = _extract_license(msg)

    artifacts: list[ResolvedArtifact] = [
        ResolvedArtifact("metadata.json", body, "application/json"),
    ]

    # 2. Unpaywall OA lookup (best-effort; failures are non-fatal).
    oa_url: str | None = None
    try:
        up_url = UNPAYWALL_API.format(doi=doi, email=_contact_email())
        up_status, _up_hdrs, up_body = fetch(up_url, {"Accept": "application/json"})
        if up_status == 200:
            artifacts.append(ResolvedArtifact("unpaywall.json", up_body, "application/json"))
            up_payload = json.loads(up_body.decode("utf-8"))
            best = up_payload.get("best_oa_location") or {}
            oa_url = best.get("url_for_pdf") or best.get("url")
    except (FetchError, NotFoundError, PaywallError, json.JSONDecodeError):
        pass

    # 3. If an OA URL is known, fetch the full text.
    if oa_url:
        try:
            oa_status, oa_hdrs, oa_body = fetch(oa_url, None)
            if oa_status == 200 and oa_body:
                ct = oa_hdrs.get("content-type", "application/octet-stream")
                ext = extension_for(ct)
                fname = f"paper.{ext}"
                artifacts.append(ResolvedArtifact(fname, oa_body, ct))
        except (FetchError, NotFoundError, PaywallError):
            pass

    return ResolvedSource(
        slug=slugify(title, fallback=slugify(doi)),
        title=title,
        kind=kind,
        retrieved_at=datetime.now(UTC),
        authors=authors,
        year=year,
        doi=doi,
        url=f"https://doi.org/{doi}",
        license=license_str,
        citation=_citation(msg),
        artifacts=artifacts,
    )
