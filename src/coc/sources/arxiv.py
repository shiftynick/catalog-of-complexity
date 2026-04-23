"""arXiv resolver: Atom metadata + PDF.

arXiv's query API returns Atom XML. We treat it as opaque bytes and parse just
enough (title, authors, published) via a small regex pass — adding a full XML
dep is not worth it for the handful of fields we need.
"""

from __future__ import annotations

import re
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

ARXIV_QUERY = "http://export.arxiv.org/api/query?id_list={aid}"
ARXIV_PDF = "https://arxiv.org/pdf/{aid}.pdf"


def _default_fetcher(url: str, headers: dict[str, str] | None) -> tuple[int, dict[str, str], bytes]:
    return http_get(url, headers=headers)


def _strip_prefix(ref: str) -> str:
    if not ref.startswith("arxiv:"):
        raise ValueError(f"not an arxiv ref: {ref!r}")
    return ref[6:]


_TITLE_RE = re.compile(r"<entry>.*?<title>(.*?)</title>", re.DOTALL)
_AUTHOR_RE = re.compile(r"<author>\s*<name>(.*?)</name>", re.DOTALL)
_PUB_RE = re.compile(r"<entry>.*?<published>(\d{4})-", re.DOTALL)


def _parse_atom(xml: str) -> tuple[str, list[str], int | None]:
    title_m = _TITLE_RE.search(xml)
    title = (title_m.group(1).strip() if title_m else "").replace("\n", " ")
    title = re.sub(r"\s+", " ", title)
    authors = [a.strip() for a in _AUTHOR_RE.findall(xml)]
    pub_m = _PUB_RE.search(xml)
    year = int(pub_m.group(1)) if pub_m else None
    return title, authors, year


def resolve(ref: str, fetcher: Fetcher | None = None) -> ResolvedSource:
    """Resolve an ``arxiv:`` ref to a ResolvedSource."""
    fetch = fetcher or _default_fetcher
    aid = _strip_prefix(ref)

    q_url = ARXIV_QUERY.format(aid=aid)
    status, _hdrs, body = fetch(q_url, {"Accept": "application/atom+xml"})
    if status != 200:
        raise FetchError(f"arXiv returned {status} for {aid}")
    xml = body.decode("utf-8", errors="replace")
    if "<entry>" not in xml:
        raise NotFoundError(f"arXiv has no entry for {aid}")
    title, authors, year = _parse_atom(xml)
    if not title:
        title = f"arXiv:{aid}"

    artifacts: list[ResolvedArtifact] = [
        ResolvedArtifact("metadata.xml", body, "application/atom+xml"),
    ]

    pdf_url = ARXIV_PDF.format(aid=aid)
    try:
        pdf_status, _pdf_hdrs, pdf_body = fetch(pdf_url, None)
        if pdf_status == 200 and pdf_body:
            artifacts.append(ResolvedArtifact("paper.pdf", pdf_body, "application/pdf"))
    except (FetchError, NotFoundError):
        pass

    return ResolvedSource(
        slug=slugify(title, fallback=slugify(aid)),
        title=title,
        kind="preprint",
        retrieved_at=datetime.now(UTC),
        authors=authors,
        year=year,
        doi=None,
        arxiv_id=aid,
        url=f"https://arxiv.org/abs/{aid}",
        license=None,
        citation=f"{', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')}. "
        f"{title}. arXiv:{aid}.",
        artifacts=artifacts,
    )
