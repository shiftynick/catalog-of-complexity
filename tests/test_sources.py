"""Source acquisition: resolver dispatch, writer, slug, idempotency.

All tests inject a fake fetcher so none of them touch the network.
"""

from __future__ import annotations

import json

import pytest

from coc.sources import (
    NotFoundError,
    ResolutionError,
    UnsupportedRefError,
    resolve,
    write_source,
)
from coc.sources import arxiv as arxiv_resolver
from coc.sources import crossref as crossref_resolver
from coc.sources import isbn_books as isbn_books_resolver
from coc.sources import web as web_resolver
from coc.sources.base import ResolvedArtifact, ResolvedSource
from coc.sources.slugs import next_source_id, slugify
from coc.sources.writer import _existing_for


def _fetcher_from_map(responses: dict[str, tuple[int, dict[str, str], bytes]]):
    """Return a fetcher that looks up the URL in `responses`. Misses raise."""

    def _fetch(url: str, headers: dict[str, str] | None):
        if url not in responses:
            raise AssertionError(f"unexpected fetch: {url}")
        return responses[url]

    return _fetch


def test_slugify_handles_empty_and_unicode():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("   ") == "untitled"
    assert slugify("Σ-Systems & Complexity (2023)") == "systems-complexity-2023"


def test_next_source_id_starts_at_000001(tmp_path):
    assert next_source_id(tmp_path) == "src-000001"


def test_next_source_id_increments_past_existing(tmp_path):
    (tmp_path / "src-000003--foo").mkdir()
    (tmp_path / "src-000008--bar").mkdir()
    (tmp_path / "src-000002--baz").mkdir()
    assert next_source_id(tmp_path) == "src-000009"


def test_dispatch_rejects_unsupported_prefix():
    with pytest.raises(UnsupportedRefError):
        resolve("ftp://not-a-ref")


def test_isbn_books_resolve_happy_path():
    isbn = "9780815345053"
    gb_body = json.dumps({
        "kind": "books#volumes",
        "totalItems": 1,
        "items": [
            {
                "volumeInfo": {
                    "title": "Molecular Biology of the Cell",
                    "authors": ["Bruce Alberts", "Alexander Johnson"],
                    "publishedDate": "2014-11-18",
                    "publisher": "Garland Science",
                }
            }
        ],
    }).encode("utf-8")
    responses = {
        f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}": (
            200, {"content-type": "application/json"}, gb_body,
        ),
    }
    rs = isbn_books_resolver.resolve(
        f"isbn:{isbn}",
        fetcher=_fetcher_from_map(responses),
    )
    assert rs.kind == "book"
    assert rs.license is None
    assert rs.url == f"urn:isbn:{isbn}"
    assert len(rs.artifacts) == 1
    assert rs.artifacts[0].filename == "metadata.json"
    assert rs.artifacts[0].content == gb_body
    assert rs.slug == "molecular-biology-of-the-cell"
    assert rs.authors == ["Bruce Alberts", "Alexander Johnson"]
    assert rs.year == 2014


def test_isbn_books_falls_back_to_open_library():
    isbn = "9780199541423"
    gb_body = json.dumps({"kind": "books#volumes", "totalItems": 0}).encode("utf-8")
    ol_body = json.dumps({
        f"ISBN:{isbn}": {
            "title": "The Oxford Handbook of Innovation",
            "authors": [{"name": "Jan Fagerberg"}, {"name": "David C. Mowery"}],
            "publish_date": "2006",
            "publishers": [{"name": "Oxford University Press"}],
        }
    }).encode("utf-8")
    responses = {
        f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}": (
            200, {"content-type": "application/json"}, gb_body,
        ),
        f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data": (
            200, {"content-type": "application/json"}, ol_body,
        ),
    }
    rs = isbn_books_resolver.resolve(
        f"isbn:{isbn}",
        fetcher=_fetcher_from_map(responses),
    )
    assert rs.kind == "book"
    assert rs.license is None
    assert rs.url == f"urn:isbn:{isbn}"
    assert len(rs.artifacts) == 1
    assert rs.artifacts[0].filename == "metadata.json"
    assert rs.artifacts[0].content == ol_body
    assert rs.title == "The Oxford Handbook of Innovation"
    assert rs.authors == ["Jan Fagerberg", "David C. Mowery"]
    assert rs.year == 2006
    assert rs.slug == "the-oxford-handbook-of-innovation"


def test_isbn_books_not_found_when_both_empty():
    isbn = "9999999999999"
    gb_body = json.dumps({"kind": "books#volumes", "totalItems": 0}).encode("utf-8")
    ol_body = json.dumps({}).encode("utf-8")
    responses = {
        f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}": (
            200, {"content-type": "application/json"}, gb_body,
        ),
        f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data": (
            200, {"content-type": "application/json"}, ol_body,
        ),
    }
    with pytest.raises(NotFoundError):
        isbn_books_resolver.resolve(
            f"isbn:{isbn}",
            fetcher=_fetcher_from_map(responses),
        )


def test_crossref_resolve_happy_path(monkeypatch):
    crossref_body = json.dumps({
        "message": {
            "DOI": "10.1038/nrmicro3109",
            "type": "journal-article",
            "title": ["A Review of Microbial Metabolic Networks"],
            "author": [
                {"given": "Jane", "family": "Doe"},
                {"given": "John", "family": "Smith"},
            ],
            "published-print": {"date-parts": [[2022, 4, 1]]},
            "container-title": ["Nature Reviews Microbiology"],
            "license": [{"URL": "https://creativecommons.org/licenses/by/4.0/"}],
        }
    }).encode("utf-8")
    unpaywall_body = json.dumps({
        "best_oa_location": {"url_for_pdf": "https://oa.example/paper.pdf"},
    }).encode("utf-8")
    pdf_body = b"%PDF-1.4 fake"

    responses = {
        "https://api.crossref.org/works/10.1038/nrmicro3109": (
            200, {"content-type": "application/json"}, crossref_body,
        ),
        # Contact email comes from env; use the default in the test.
        "https://api.unpaywall.org/v2/10.1038/nrmicro3109?email=admin@catalog-of-complexity.local": (
            200, {"content-type": "application/json"}, unpaywall_body,
        ),
        "https://oa.example/paper.pdf": (
            200, {"content-type": "application/pdf"}, pdf_body,
        ),
    }
    monkeypatch.delenv("COC_CONTACT_EMAIL", raising=False)
    rs = crossref_resolver.resolve(
        "doi:10.1038/nrmicro3109",
        fetcher=_fetcher_from_map(responses),
    )
    assert rs.doi == "10.1038/nrmicro3109"
    assert rs.kind == "peer-reviewed"
    assert rs.year == 2022
    assert rs.authors == ["Jane Doe", "John Smith"]
    assert rs.license == "https://creativecommons.org/licenses/by/4.0/"
    assert rs.slug == "a-review-of-microbial-metabolic-networks"
    filenames = [a.filename for a in rs.artifacts]
    assert filenames == ["metadata.json", "unpaywall.json", "paper.pdf"]


def test_crossref_not_found_raises(monkeypatch):
    def _fetch(url, headers):
        raise NotFoundError("404")

    monkeypatch.delenv("COC_CONTACT_EMAIL", raising=False)
    with pytest.raises(ResolutionError):
        crossref_resolver.resolve("doi:10.9999/does-not-exist", fetcher=_fetch)


def test_arxiv_resolve_happy_path():
    atom = b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Deep Foo Bar Networks</title>
    <author><name>Alice Alpha</name></author>
    <author><name>Bob Beta</name></author>
    <published>2023-11-02T00:00:00Z</published>
  </entry>
</feed>"""
    pdf = b"%PDF-1.5 fake"
    responses = {
        "http://export.arxiv.org/api/query?id_list=2311.01234": (
            200, {"content-type": "application/atom+xml"}, atom,
        ),
        "https://arxiv.org/pdf/2311.01234.pdf": (
            200, {"content-type": "application/pdf"}, pdf,
        ),
    }
    rs = arxiv_resolver.resolve(
        "arxiv:2311.01234",
        fetcher=_fetcher_from_map(responses),
    )
    assert rs.kind == "preprint"
    assert rs.arxiv_id == "2311.01234"
    assert rs.year == 2023
    assert rs.authors == ["Alice Alpha", "Bob Beta"]
    assert [a.filename for a in rs.artifacts] == ["metadata.xml", "paper.pdf"]


def test_web_resolve_extracts_html_title():
    html = b"<html><head><title>Example Landing Page</title></head><body/></html>"
    responses = {
        "https://example.com/thing": (
            200, {"content-type": "text/html; charset=utf-8"}, html,
        ),
    }
    rs = web_resolver.resolve(
        "url:https://example.com/thing",
        fetcher=_fetcher_from_map(responses),
    )
    assert rs.kind == "web"
    assert rs.title == "Example Landing Page"
    assert rs.slug == "example-landing-page"


def _fake_resolved(**overrides) -> ResolvedSource:
    from datetime import UTC, datetime

    base = dict(
        slug="test-paper",
        title="Test Paper",
        kind="peer-reviewed",
        retrieved_at=datetime(2026, 4, 23, 18, 0, 0, tzinfo=UTC),
        authors=["Author One"],
        year=2024,
        doi="10.0000/test",
        arxiv_id=None,
        url="https://doi.org/10.0000/test",
        license="CC-BY-4.0",
        citation="Author One (2024). Test Paper.",
        artifacts=[
            ResolvedArtifact("metadata.json", b"{\"x\":1}", "application/json"),
        ],
    )
    base.update(overrides)
    return ResolvedSource(**base)


def test_write_source_creates_full_layout(tmp_path):
    rs = _fake_resolved()
    path = write_source(rs, reg_sources=tmp_path)
    assert path.name.startswith("src-000001--")
    assert (path / "source.yaml").exists()
    assert (path / "raw" / "metadata.json").exists()
    assert (path / "parsed").is_dir()
    assert (path / "evidence.jsonl").read_text() == ""


def test_write_source_idempotent_on_doi_match(tmp_path):
    rs = _fake_resolved()
    first = write_source(rs, reg_sources=tmp_path)
    rs2 = _fake_resolved(title="Test Paper (revised)")  # same DOI
    second = write_source(rs2, reg_sources=tmp_path)
    assert first == second
    # Only one src-* dir should exist.
    dirs = sorted(p.name for p in tmp_path.iterdir() if p.is_dir())
    assert len(dirs) == 1


def test_write_source_produces_valid_source_yaml(tmp_path):
    from coc.schemas import validate_instance
    from coc.yamlio import load_yaml

    rs = _fake_resolved()
    path = write_source(rs, reg_sources=tmp_path)
    data = load_yaml(path / "source.yaml")
    assert validate_instance("source", data) == []
    assert data["hash"] is not None
    assert data["kind"] == "peer-reviewed"
    assert data["raw_path"].endswith("/raw/")


def test_write_source_rolls_back_on_invalid_record(tmp_path):
    # An empty title string — not caught by resolvers but the schema requires minLength 1.
    rs = _fake_resolved(title="")
    with pytest.raises(ValueError):
        write_source(rs, reg_sources=tmp_path)
    # Nothing left behind.
    leftover = list(tmp_path.iterdir())
    assert leftover == []


def test_existing_for_matches_on_url_when_no_doi(tmp_path):
    from coc.yamlio import dump_yaml

    src_dir = tmp_path / "src-000001--legacy"
    (src_dir / "raw").mkdir(parents=True)
    dump_yaml(
        {
            "id": "src-000001--legacy",
            "slug": "legacy",
            "title": "Legacy",
            "kind": "web",
            "retrieved_at": "2026-04-01T00:00:00Z",
            "url": "https://example.com/x",
            "raw_path": "registry/sources/src-000001--legacy/raw/",
        },
        src_dir / "source.yaml",
    )
    rs = _fake_resolved(doi=None, url="https://example.com/x")
    existing = _existing_for(rs, tmp_path)
    assert existing == src_dir
