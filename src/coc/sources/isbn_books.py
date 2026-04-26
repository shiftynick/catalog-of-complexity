"""ISBN resolver: Google Books primary + Open Library fallback.

Both endpoints are unauthenticated, ISBN-keyed JSON APIs that return
bibliographic metadata for printed books. There is no full-text retrieval —
ISBN points to a physical or licensed digital book, not an OA artifact —
so the resolver is metadata-only and writes a `source.yaml` with
``license = null``. Downstream `extract-observations` tasks that need a
chapter excerpt must source it elsewhere (or block).

Flow:

1. Strip the ``isbn:`` prefix.
2. GET Google Books ``volumes?q=isbn:<isbn>``.
3. If Google Books returned at least one item, use its ``volumeInfo`` and
   write the raw response body to ``raw/metadata.json``.
4. Otherwise (``totalItems: 0`` or missing ``items``), GET Open Library
   ``api/books?bibkeys=ISBN:<isbn>&format=json&jscmd=data`` and use the
   keyed entry. Write the raw Open Library response to
   ``raw/metadata.json``.
5. NotFoundError when both providers come up empty.

The url field on the produced ResolvedSource is set to ``urn:isbn:<isbn>`` so
``writer._existing_for`` can match a re-fetch via ``find_existing_by_url``
regardless of which provider answered.
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

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
OPEN_LIBRARY_API = (
    "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
)


def _default_fetcher(url: str, headers: dict[str, str] | None) -> tuple[int, dict[str, str], bytes]:
    return http_get(url, headers=headers)


def _strip_prefix(ref: str) -> str:
    if not ref.startswith("isbn:"):
        raise ValueError(f"not an isbn ref: {ref!r}")
    return ref[5:].strip()


def _year_from_date(date_str: str | None) -> int | None:
    if not isinstance(date_str, str):
        return None
    s = date_str.strip()
    if len(s) >= 4 and s[:4].isdigit():
        return int(s[:4])
    return None


def _google_books_first_item(payload: dict) -> dict | None:
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    return first


def _from_google_books(volume_info: dict, isbn: str) -> tuple[str, list[str], int | None, str | None]:
    title = (volume_info.get("title") or "").strip() or f"ISBN {isbn}"
    subtitle = (volume_info.get("subtitle") or "").strip()
    if subtitle:
        title = f"{title}: {subtitle}"
    authors_raw = volume_info.get("authors") or []
    authors = [str(a).strip() for a in authors_raw if isinstance(a, str) and a.strip()]
    year = _year_from_date(volume_info.get("publishedDate"))
    publisher = (volume_info.get("publisher") or "").strip() or None
    return title, authors, year, publisher


def _from_open_library(entry: dict, isbn: str) -> tuple[str, list[str], int | None, str | None]:
    title = (entry.get("title") or "").strip() or f"ISBN {isbn}"
    subtitle = (entry.get("subtitle") or "").strip()
    if subtitle:
        title = f"{title}: {subtitle}"
    authors_raw = entry.get("authors") or []
    authors: list[str] = []
    for a in authors_raw:
        if isinstance(a, dict):
            name = (a.get("name") or "").strip()
            if name:
                authors.append(name)
        elif isinstance(a, str):
            v = a.strip()
            if v:
                authors.append(v)
    year = _year_from_date(entry.get("publish_date"))
    publishers = entry.get("publishers") or []
    publisher: str | None = None
    if publishers:
        first = publishers[0]
        if isinstance(first, dict):
            publisher = (first.get("name") or "").strip() or None
        elif isinstance(first, str):
            publisher = first.strip() or None
    return title, authors, year, publisher


def _citation(title: str, authors: list[str], year: int | None, publisher: str | None, isbn: str) -> str:
    parts: list[str] = []
    if authors:
        parts.append(", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""))
    if year:
        parts.append(f"({year})")
    parts.append(title)
    if publisher:
        parts.append(publisher)
    parts.append(f"ISBN:{isbn}")
    return ". ".join(parts)


def resolve(ref: str, fetcher: Fetcher | None = None) -> ResolvedSource:
    """Resolve an ``isbn:`` ref to a ResolvedSource using Google Books → Open Library."""
    fetch = fetcher or _default_fetcher
    isbn = _strip_prefix(ref)

    # 1. Google Books primary.
    gb_url = GOOGLE_BOOKS_API.format(isbn=isbn)
    gb_payload: dict | None = None
    gb_body: bytes | None = None
    try:
        status, _hdrs, body = fetch(gb_url, {"Accept": "application/json"})
        if status == 200:
            gb_body = body
            try:
                gb_payload = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                gb_payload = None
    except (FetchError, NotFoundError):
        gb_payload = None

    item = _google_books_first_item(gb_payload) if gb_payload else None
    if item is not None and gb_body is not None:
        volume_info = item.get("volumeInfo") or {}
        title, authors, year, publisher = _from_google_books(volume_info, isbn)
        artifacts = [ResolvedArtifact("metadata.json", gb_body, "application/json")]
        return ResolvedSource(
            slug=slugify(title, fallback=slugify(f"isbn-{isbn}")),
            title=title,
            kind="book",
            retrieved_at=datetime.now(UTC),
            authors=authors,
            year=year,
            doi=None,
            url=f"urn:isbn:{isbn}",
            license=None,
            citation=_citation(title, authors, year, publisher, isbn),
            artifacts=artifacts,
        )

    # 2. Open Library fallback.
    ol_url = OPEN_LIBRARY_API.format(isbn=isbn)
    try:
        ol_status, _ol_hdrs, ol_body = fetch(ol_url, {"Accept": "application/json"})
    except (FetchError, NotFoundError) as exc:
        raise NotFoundError(
            f"both Google Books and Open Library returned no record for isbn:{isbn} ({exc})"
        ) from exc
    if ol_status != 200:
        raise FetchError(f"Open Library returned {ol_status} for isbn:{isbn}")
    try:
        ol_payload = json.loads(ol_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FetchError(f"Open Library returned non-JSON for isbn:{isbn}") from exc

    entry = ol_payload.get(f"ISBN:{isbn}") if isinstance(ol_payload, dict) else None
    if not isinstance(entry, dict) or not entry:
        raise NotFoundError(
            f"both Google Books and Open Library returned no record for isbn:{isbn}"
        )
    title, authors, year, publisher = _from_open_library(entry, isbn)
    artifacts = [ResolvedArtifact("metadata.json", ol_body, "application/json")]
    return ResolvedSource(
        slug=slugify(title, fallback=slugify(f"isbn-{isbn}")),
        title=title,
        kind="book",
        retrieved_at=datetime.now(UTC),
        authors=authors,
        year=year,
        doi=None,
        url=f"urn:isbn:{isbn}",
        license=None,
        citation=_citation(title, authors, year, publisher, isbn),
        artifacts=artifacts,
    )
