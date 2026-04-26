"""Ref prefix → resolver dispatch.

Known prefixes: ``doi:``, ``arxiv:``, ``url:``, ``isbn:``.

For ``doi:`` refs, Crossref is queried first and DataCite is the fallback
when Crossref returns a NotFoundError. This covers dataset / standards
DOIs (NIST ``10.18434/*``, Zenodo ``10.5281/*``, figshare ``10.6084/*``,
etc.) that are minted at DataCite rather than Crossref. A NotFoundError
is propagated only if both registrars miss.

For ``isbn:`` refs, Google Books is queried first and Open Library is the
fallback when Google Books returns an empty ``items`` array. Both endpoints
are unauthenticated JSON APIs; the resolver writes metadata-only source
records (no OA full text — ISBNs point to printed/licensed books).
"""

from __future__ import annotations

from coc.sources.base import (
    Fetcher,
    NotFoundError,
    ResolvedSource,
    UnsupportedRefError,
)


def resolve(ref: str, fetcher: Fetcher | None = None) -> ResolvedSource:
    """Dispatch `ref` to the matching resolver and return its ResolvedSource."""
    from coc.sources import arxiv, crossref, datacite, isbn_books, web

    if ref.startswith("doi:"):
        try:
            return crossref.resolve(ref, fetcher=fetcher)
        except NotFoundError:
            return datacite.resolve(ref, fetcher=fetcher)
    if ref.startswith("arxiv:"):
        return arxiv.resolve(ref, fetcher=fetcher)
    if ref.startswith("url:"):
        return web.resolve(ref, fetcher=fetcher)
    if ref.startswith("isbn:"):
        return isbn_books.resolve(ref, fetcher=fetcher)
    raise UnsupportedRefError(
        f"no resolver for ref {ref!r}; expected one of doi:/arxiv:/url:/isbn:"
    )
