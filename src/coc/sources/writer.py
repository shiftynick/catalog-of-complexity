"""Materialize a ResolvedSource under `registry/sources/src-NNNNNN--<slug>/`.

Idempotent on DOI / arxiv / url match: if an existing source has the same
identifier, no new directory is created — the existing path is returned.

Writes are staged under a `.tmp-<src>/` sibling and renamed into place atomically
(on the same filesystem), so a crash mid-write never leaves a partial
`src-NNNNNN--<slug>/` for `coc validate` to trip over.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path

from coc.paths import REG_SOURCES
from coc.schemas import validate_instance
from coc.sources.base import ResolvedSource
from coc.sources.dispatch import resolve
from coc.sources.slugs import (
    find_existing_by_arxiv,
    find_existing_by_doi,
    find_existing_by_url,
    next_source_id,
)
from coc.yamlio import dump_yaml


def _iso_z(dt) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _existing_for(resolved: ResolvedSource, reg_sources: Path) -> Path | None:
    if resolved.doi:
        hit = find_existing_by_doi(resolved.doi, reg_sources)
        if hit:
            return hit
    if resolved.arxiv_id:
        hit = find_existing_by_arxiv(resolved.arxiv_id, reg_sources)
        if hit:
            return hit
    if resolved.url:
        hit = find_existing_by_url(resolved.url, reg_sources)
        if hit:
            return hit
    return None


def _combined_hash(resolved: ResolvedSource) -> str:
    """SHA-256 across the raw artifact bytes in order."""
    h = hashlib.sha256()
    for art in resolved.artifacts:
        h.update(art.filename.encode("utf-8"))
        h.update(b"\x00")
        h.update(art.content)
        h.update(b"\x00")
    return h.hexdigest()


def _allocate_src_dir(resolved: ResolvedSource, reg_sources: Path) -> Path:
    src_id_prefix = next_source_id(reg_sources)
    full_id = f"{src_id_prefix}--{resolved.slug}"
    target = reg_sources / full_id
    # If the computed slug happens to collide (different DOI, same slug),
    # append a disambiguating numeric suffix.
    suffix = 2
    while target.exists():
        full_id = f"{src_id_prefix}--{resolved.slug}-{suffix}"
        target = reg_sources / full_id
        suffix += 1
    return target


def write_source(resolved: ResolvedSource, reg_sources: Path = REG_SOURCES) -> Path:
    """Write `resolved` to `reg_sources/` and return the final directory path.

    If an existing source already covers this identifier, that path is
    returned instead (no write performed).
    """
    existing = _existing_for(resolved, reg_sources)
    if existing is not None:
        return existing

    reg_sources.mkdir(parents=True, exist_ok=True)
    target = _allocate_src_dir(resolved, reg_sources)
    src_id = target.name
    staging = reg_sources / f".tmp-{src_id}"
    if staging.exists():
        shutil.rmtree(staging)
    try:
        (staging / "raw").mkdir(parents=True, exist_ok=True)
        (staging / "parsed").mkdir(parents=True, exist_ok=True)
        for art in resolved.artifacts:
            (staging / "raw" / art.filename).write_bytes(art.content)
        (staging / "evidence.jsonl").write_text("", encoding="utf-8")

        source_yaml: dict = {
            "id": src_id,
            "slug": src_id.split("--", 1)[1],
            "title": resolved.title,
            "authors": list(resolved.authors),
            "kind": resolved.kind,
            "year": resolved.year,
            "doi": resolved.doi,
            "url": resolved.url,
            "license": resolved.license,
            "retrieved_at": _iso_z(resolved.retrieved_at),
            "citation": resolved.citation,
            "hash": _combined_hash(resolved) if resolved.artifacts else None,
            "raw_path": f"registry/sources/{src_id}/raw/",
            "parsed_path": f"registry/sources/{src_id}/parsed/",
        }
        errors = validate_instance("source", source_yaml)
        if errors:
            raise ValueError(f"resolver produced invalid source record: {errors}")
        dump_yaml(source_yaml, staging / "source.yaml")
        os.rename(staging, target)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise
    return target


def acquire(ref: str, reg_sources: Path = REG_SOURCES) -> Path:
    """Resolve `ref` and write the result. Shortcut for `write_source(resolve(ref))`."""
    resolved = resolve(ref)
    return write_source(resolved, reg_sources)
