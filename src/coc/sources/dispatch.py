"""Ref prefix → resolver dispatch.

Known prefixes: ``doi:``, ``arxiv:``, ``url:``. ``isbn:`` is accepted by the
schema but not resolvable without a book-metadata provider we haven't added
yet — calls raise UnsupportedRefError so the caller blocks rather than
silently skipping.
"""

from __future__ import annotations

from coc.sources.base import Fetcher, ResolvedSource, UnsupportedRefError


def resolve(ref: str, fetcher: Fetcher | None = None) -> ResolvedSource:
    """Dispatch `ref` to the matching resolver and return its ResolvedSource."""
    from coc.sources import arxiv, crossref, web

    if ref.startswith("doi:"):
        return crossref.resolve(ref, fetcher=fetcher)
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
