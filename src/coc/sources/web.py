"""Generic URL resolver: fetch the URL, infer kind from content-type.

Used as the last-resort resolver for `url:` refs. Titles are best-effort
extracted from HTML `<title>` tags; everything else defaults to the URL path.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from coc.sources.base import Fetcher, FetchError, ResolvedArtifact, ResolvedSource
from coc.sources.http import extension_for, http_get
from coc.sources.slugs import slugify

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


def _default_fetcher(url: str, headers: dict[str, str] | None) -> tuple[int, dict[str, str], bytes]:
    return http_get(url, headers=headers)


def _strip_prefix(ref: str) -> str:
    if not ref.startswith("url:"):
        raise ValueError(f"not a url ref: {ref!r}")
    return ref[4:]


def _title_from_html(body: bytes) -> str | None:
    try:
        text = body.decode("utf-8", errors="replace")
    except UnicodeDecodeError:
        return None
    m = _TITLE_RE.search(text)
    if not m:
        return None
    return re.sub(r"\s+", " ", m.group(1)).strip() or None


def _kind_for(content_type: str) -> str:
    ct = content_type.split(";", 1)[0].strip().lower()
    if ct == "application/pdf":
        return "technical-report"
    if ct in ("application/json", "text/csv", "application/x-parquet"):
        return "dataset"
    return "web"


def resolve(ref: str, fetcher: Fetcher | None = None) -> ResolvedSource:
    """Resolve a ``url:`` ref to a ResolvedSource."""
    fetch = fetcher or _default_fetcher
    url = _strip_prefix(ref)
    status, hdrs, body = fetch(url, None)
    if status != 200:
        raise FetchError(f"GET {url} returned {status}")
    ct = hdrs.get("content-type", "application/octet-stream")
    ext = extension_for(ct)
    artifacts = [ResolvedArtifact(f"landing.{ext}", body, ct)]
    title = _title_from_html(body) if ext == "html" else None
    if not title:
        title = url
    return ResolvedSource(
        slug=slugify(title, fallback=slugify(url)),
        title=title,
        kind=_kind_for(ct),
        retrieved_at=datetime.now(UTC),
        authors=[],
        year=None,
        doi=None,
        url=url,
        license=None,
        citation=f"{title}. {url}",
        artifacts=artifacts,
    )
