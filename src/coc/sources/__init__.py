"""Source acquisition: prefixed refs (`doi:`, `arxiv:`, `url:`) → registered src-* dirs.

Public surface:

    resolve(ref)        — dispatch a ref to its resolver; returns ResolvedSource.
    write_source(rs)    — write the resolver output to `registry/sources/src-NNNNNN--<slug>/`.
    acquire(ref)        — one-call resolve-then-write; returns the written Path.

Two abstractions live here:

- **Resolver** (this module, now): address → artifact. One ref in, one source out.
- **DeepSearch** (future): query → addresses. Placeholder only; see ``deep_search/``.
"""

from __future__ import annotations

from coc.sources.base import (
    FetchError,
    NotFoundError,
    PaywallError,
    ResolutionError,
    ResolvedArtifact,
    ResolvedSource,
    UnsupportedRefError,
)
from coc.sources.dispatch import resolve
from coc.sources.writer import acquire, write_source

__all__ = [
    "FetchError",
    "NotFoundError",
    "PaywallError",
    "ResolutionError",
    "ResolvedArtifact",
    "ResolvedSource",
    "UnsupportedRefError",
    "acquire",
    "resolve",
    "write_source",
]
