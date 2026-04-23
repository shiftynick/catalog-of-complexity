"""Resolver protocol, ResolvedSource dataclass, and error hierarchy.

A `Resolver` takes a prefixed reference string (e.g. `doi:10.1038/nature12345`)
and produces a `ResolvedSource`: enough metadata to write a `source.yaml` plus
the raw artifacts to drop into `raw/`.

Resolvers do not touch the filesystem. That's the writer's job. This
separation keeps resolvers trivially testable — inject a fake fetcher and
assert the returned dataclass.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


class ResolutionError(RuntimeError):
    """Base class for resolver failures."""


class UnsupportedRefError(ResolutionError):
    """No resolver registered for this ref prefix / shape."""


class NotFoundError(ResolutionError):
    """Upstream returned 404 or equivalent (DOI not minted, arxiv id bogus)."""


class PaywallError(ResolutionError):
    """Metadata was fetched but no accessible full-text could be retrieved."""


class FetchError(ResolutionError):
    """Transient network / HTTP failure. Callers may retry."""


@dataclass(frozen=True)
class ResolvedArtifact:
    """One raw file to drop under `registry/sources/<src>/raw/`."""

    filename: str
    content: bytes
    content_type: str


@dataclass(frozen=True)
class ResolvedSource:
    """Everything the writer needs to materialize a registered source.

    `slug` is the normalized slug the writer will use for the `src-NNNNNN--<slug>`
    directory (the writer may append a disambiguating suffix on collision).
    `artifacts` are written in order under `raw/`.
    """

    slug: str
    title: str
    kind: str  # one of source.schema.json#kind enum
    retrieved_at: datetime
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    license: str | None = None
    citation: str | None = None
    artifacts: list[ResolvedArtifact] = field(default_factory=list)


# A fetcher returns (status_code, headers_lowercased, body_bytes).
Fetcher = Callable[[str, dict[str, str] | None], tuple[int, dict[str, str], bytes]]


class Resolver(Protocol):
    """Protocol for per-prefix resolvers.

    Implementations must be pure (no filesystem writes) and injectable
    (accept a fetcher for test doubles).
    """

    prefix: str

    def can_handle(self, ref: str) -> bool: ...

    def resolve(self, ref: str, fetcher: Fetcher | None = None) -> ResolvedSource: ...
