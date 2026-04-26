"""Ref prefix → resolver dispatch.

Known prefixes: ``doi:``, ``arxiv:``, ``url:``. ``isbn:`` is accepted by the
schema but not resolvable without a book-metadata provider we haven't added
yet — calls raise UnsupportedRefError so the caller blocks rather than
silently skipping.

For ``doi:`` refs, Crossref is queried first and DataCite is the fallback
when Crossref returns a NotFoundError. This covers dataset / standards
DOIs (NIST ``10.18434/*``, Zenodo ``10.5281/*``, figshare ``10.6084/*``,
etc.) that are minted at DataCite rather than Crossref. A NotFoundError
is propagated only if both registrars miss.
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
    from coc.sources import arxiv, crossref, datacite, web

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
        raise UnsupportedRefError(
            f"isbn refs not yet resolvable: {ref!r} "
            "(add a book-metadata resolver before using isbn: in manifests)"
        )
    raise UnsupportedRefError(
        f"no resolver for ref {ref!r}; expected one of doi:/arxiv:/url:/isbn:"
    )
