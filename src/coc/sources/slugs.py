"""Slug normalization + next-free src id allocation."""

from __future__ import annotations

import re
from pathlib import Path

from coc.paths import REG_SOURCES

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")
_MULTIHYPHEN = re.compile(r"-{2,}")
MAX_SLUG_LEN = 60


def slugify(text: str, fallback: str = "untitled") -> str:
    """Lowercase → alnum+hyphen → collapse → trim. Returns `fallback` if empty."""
    s = _SLUG_STRIP.sub("-", (text or "").lower())
    s = _MULTIHYPHEN.sub("-", s).strip("-")
    if not s:
        return fallback
    return s[:MAX_SLUG_LEN].rstrip("-") or fallback


def next_source_id(reg_sources: Path = REG_SOURCES) -> str:
    """Return the next unused `src-NNNNNN` numeric prefix (no slug)."""
    max_n = 0
    if reg_sources.exists():
        for entry in reg_sources.iterdir():
            if not entry.is_dir():
                continue
            name = entry.name
            if not name.startswith("src-"):
                continue
            rest = name[4:]
            num = rest.split("--", 1)[0]
            if num.isdigit():
                max_n = max(max_n, int(num))
    return f"src-{max_n + 1:06d}"


def find_existing_by_doi(doi: str, reg_sources: Path = REG_SOURCES) -> Path | None:
    """Return an existing `src-*` dir whose source.yaml has a matching DOI."""
    from coc.yamlio import load_yaml

    if not reg_sources.exists() or not doi:
        return None
    target = doi.lower().strip()
    for entry in sorted(reg_sources.iterdir()):
        sy = entry / "source.yaml"
        if not sy.exists():
            continue
        data = load_yaml(sy) or {}
        existing = (data.get("doi") or "").lower().strip()
        if existing and existing == target:
            return entry
    return None


def find_existing_by_arxiv(arxiv_id: str, reg_sources: Path = REG_SOURCES) -> Path | None:
    """Return an existing src whose url or doi references this arxiv id."""
    from coc.yamlio import load_yaml

    if not reg_sources.exists() or not arxiv_id:
        return None
    target = arxiv_id.lower().strip()
    for entry in sorted(reg_sources.iterdir()):
        sy = entry / "source.yaml"
        if not sy.exists():
            continue
        data = load_yaml(sy) or {}
        url = (data.get("url") or "").lower()
        if target in url:
            return entry
    return None


def find_existing_by_url(url: str, reg_sources: Path = REG_SOURCES) -> Path | None:
    """Return an existing src whose url field matches exactly."""
    from coc.yamlio import load_yaml

    if not reg_sources.exists() or not url:
        return None
    target = url.strip()
    for entry in sorted(reg_sources.iterdir()):
        sy = entry / "source.yaml"
        if not sy.exists():
            continue
        data = load_yaml(sy) or {}
        existing = (data.get("url") or "").strip()
        if existing and existing == target:
            return entry
    return None
