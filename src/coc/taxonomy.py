"""Load and export taxonomy vocabularies.

Taxonomy YAML under taxonomy/source/ is the editable source of truth. Agents
and humans may extend or reorganize it; the JSON Schemas only enforce the
*shape* of taxonomy references (e.g. `system-domain:<slug>`). Actual resolution
happens here, against the live YAML files. Re-run `coc validate` after edits
to catch dangling references.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SKOS

from coc.paths import TAXONOMY_EXPORTS, TAXONOMY_SRC
from coc.yamlio import load_yaml

COC_NS = Namespace("https://catalog-of-complexity.org/taxonomy/")

# Which YAML file maps to which prefix used in taxonomy_refs / fields.
FILE_TO_PREFIX = {
    "system-domains.yaml": "system-domain",
    "system-classes.yaml": "system-class",
    "metric-families.yaml": "metric-family",
    "evidence-types.yaml": "evidence-type",
}


@dataclass
class TaxonomyIndex:
    """In-memory index of taxonomy slugs grouped by prefix."""

    by_prefix: dict[str, set[str]]

    def has(self, qualified: str) -> bool:
        """True if `qualified` (e.g. 'system-domain:ecological') is defined."""
        if ":" not in qualified:
            return False
        prefix, slug = qualified.split(":", 1)
        return slug in self.by_prefix.get(prefix, set())

    def all_qualified(self) -> list[str]:
        out: list[str] = []
        for prefix, slugs in self.by_prefix.items():
            out.extend(f"{prefix}:{s}" for s in slugs)
        return sorted(out)


def load_index() -> TaxonomyIndex:
    by_prefix: dict[str, set[str]] = {}
    for filename, prefix in FILE_TO_PREFIX.items():
        path = TAXONOMY_SRC / filename
        if not path.exists():
            by_prefix[prefix] = set()
            continue
        data = load_yaml(path) or {}
        items = data.get("items", [])
        slugs = {item["slug"] for item in items if "slug" in item}
        by_prefix[prefix] = slugs
    return TaxonomyIndex(by_prefix=by_prefix)


def _flatten_items() -> list[tuple[str, str, dict]]:
    """Yield (prefix, slug, item_dict) across all taxonomy files."""
    rows: list[tuple[str, str, dict]] = []
    for filename, prefix in FILE_TO_PREFIX.items():
        path = TAXONOMY_SRC / filename
        if not path.exists():
            continue
        data = load_yaml(path) or {}
        for item in data.get("items", []):
            slug = item.get("slug")
            if slug:
                rows.append((prefix, slug, item))
    return rows


def export_skos(out_path: Path) -> Path:
    """Emit a SKOS Turtle file covering all taxonomy items."""
    g = Graph()
    g.bind("skos", SKOS)
    g.bind("coc", COC_NS)

    scheme = URIRef(str(COC_NS) + "scheme")
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, SKOS.prefLabel, Literal("Catalog of Complexity Taxonomy")))

    for prefix, slug, item in _flatten_items():
        subject = URIRef(f"{COC_NS}{prefix}/{slug}")
        g.add((subject, RDF.type, SKOS.Concept))
        g.add((subject, SKOS.inScheme, scheme))
        g.add((subject, SKOS.notation, Literal(f"{prefix}:{slug}")))
        label = item.get("label") or item.get("name") or slug
        g.add((subject, SKOS.prefLabel, Literal(label)))
        if "description" in item:
            g.add((subject, SKOS.definition, Literal(item["description"])))
        for alt in item.get("aliases", []) or []:
            g.add((subject, SKOS.altLabel, Literal(alt)))
        for broader in item.get("broader", []) or []:
            g.add((subject, SKOS.broader, URIRef(f"{COC_NS}{prefix}/{broader}")))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=out_path, format="turtle")
    return out_path


def export_labels_json(out_path: Path) -> Path:
    """Emit a flat JSON lookup: qualified_id -> label/description."""
    labels: dict[str, dict] = {}
    for prefix, slug, item in _flatten_items():
        qid = f"{prefix}:{slug}"
        labels[qid] = {
            "label": item.get("label") or item.get("name") or slug,
            "description": item.get("description", ""),
            "aliases": item.get("aliases", []) or [],
        }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(labels, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def export_all() -> list[Path]:
    ttl = export_skos(TAXONOMY_EXPORTS / "taxonomy.ttl")
    js = export_labels_json(TAXONOMY_EXPORTS / "labels.json")
    return [ttl, js]
