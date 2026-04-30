"""Generate `config/bootstrap_seed_v2.yaml` from `scripts/_seed_v2_data.py`.

The v0.2 seed is the long-tail thin-stub portion of the catalog import.
v0.1 (`config/bootstrap_seed.yaml`) holds rich hand-authored P0 anchors
and boundary cases; this file fills in the rest of
`docs/framework/02-candidate-systems-catalog.md` §3-25 with stubs
flagged `status: bootstrap-stub` for later upgrade.

Re-run any time `_seed_v2_data.py` changes:

    uv run python scripts/build_seed_v2.py

Then apply via the normal bootstrap chain:

    uv run python scripts/bootstrap_from_seed.py --apply
    uv run coc validate
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from coc.taxonomy import load_index  # noqa: E402
from coc.yamlio import dump_yaml  # noqa: E402

from _seed_v2_data import (  # noqa: E402
    ALL_SECTIONS,
    DOMAIN_STUB_TEMPLATES,
    PER_SECTION_DOMAIN_OVERRIDES,
    V01_SLUGS,
)
from _seed_v2_metrics_data import (  # noqa: E402
    ALL_METRIC_SECTIONS,
    FAMILY_ESTIMATION_METHODS,
    V01_METRIC_SLUGS,
)

OUT_FILE = REPO_ROOT / "config" / "bootstrap_seed_v2.yaml"


def build_entry(slug: str, name: str, classes: list[str], priority: str, kind: str | None,
                section: str, default_kind: str, default_domain: str) -> dict:
    """Translate a tuple from _seed_v2_data into a seed-shaped dict."""
    domain_override = PER_SECTION_DOMAIN_OVERRIDES.get(section, {}).get(slug)
    domain = domain_override or default_domain
    template = DOMAIN_STUB_TEMPLATES[domain]
    record: dict = {
        "slug": slug,
        "name": name,
        "domain": domain,
        "classes": list(classes),
        "priority": priority,
        "system_kind": kind or default_kind,
        "status": "bootstrap-stub",
        "summary": (
            f"Type-level archetype imported from "
            f"docs/framework/02-candidate-systems-catalog.md §{section} "
            f"(priority {priority}). Bootstrap stub awaiting profile-system upgrade."
        ),
        "boundary": dict(template["boundary"]),
        "components": list(template["components"]),
        "interaction_types": list(template["interaction_types"]),
        "scales": dict(template["scales"]),
    }
    return record


def main() -> int:
    index = load_index()
    systems: list[dict] = []
    seen: set[str] = set(V01_SLUGS)
    skipped_classes: set[str] = set()
    skipped_domains: set[str] = set()
    skipped_dupes: int = 0

    for section in ALL_SECTIONS:
        sec_id = section["section"]
        default_domain = section["domain"]
        default_kind = section["default_kind"]
        for tup in section["entries"]:
            slug = tup[0]
            name = tup[1]
            classes = tup[2]
            priority = tup[3]
            kind = tup[4] if len(tup) > 4 else None

            if slug in seen:
                skipped_dupes += 1
                continue
            seen.add(slug)

            entry = build_entry(slug, name, classes, priority, kind, sec_id, default_kind, default_domain)

            # Pre-validate domain + classes against the loaded taxonomy.
            if not index.has(f"system-domain:{entry['domain']}"):
                skipped_domains.add(entry["domain"])
                continue
            valid_classes = []
            for c in entry["classes"]:
                if index.has(f"system-class:{c}"):
                    valid_classes.append(c)
                else:
                    skipped_classes.add(c)
            entry["classes"] = valid_classes

            systems.append(entry)

    # Strip per-entry `status` so the file-level default_status applies. v0.2
    # is purely thin-stub.
    for s in systems:
        s.pop("status", None)

    # ---- Metrics ----
    metrics: list[dict] = []
    metric_seen: set[str] = set(V01_METRIC_SLUGS)
    metric_dupes = 0
    skipped_families: set[str] = set()
    for section in ALL_METRIC_SECTIONS:
        sec_id = section["section"]
        family = section["family"]
        default_vt = section["default_value_type"]
        default_sl = section["default_scale_level"]
        default_ml = section["default_maturity_level"]
        for tup in section["entries"]:
            slug = tup[0]
            name = tup[1]
            value_type = tup[2] or default_vt
            scale_level = tup[3] or default_sl
            maturity = tup[4] or default_ml
            description = tup[5]

            if slug in metric_seen:
                metric_dupes += 1
                continue
            metric_seen.add(slug)

            if not index.has(f"metric-family:{family}"):
                skipped_families.add(family)
                continue

            metric_record = {
                "slug": slug,
                "name": name,
                "family": family,
                "value_type": value_type,
                "scale_level": scale_level,
                "maturity_level": maturity,
                "description": description,
                "estimation_methods": list(FAMILY_ESTIMATION_METHODS.get(family, ["expert-estimate"])),
                "applicability": {},
                "evidence_requirements": {
                    "minimum_source_count": 1,
                    "review_required": True,
                },
            }
            metrics.append(metric_record)

    out = {
        "phase_label": "bootstrap-v2",
        "description": (
            "Long-tail catalog seed: thin-stub entries imported from "
            "docs/framework/02-candidate-systems-catalog.md §3-25 (systems) "
            "and docs/framework/03-metric-ontology.md §4-21 (metrics). "
            "All entries carry status: bootstrap-stub. Systems have minimum-required "
            "boundary/components/interaction_types/scales placeholders. Metrics have "
            "skeleton applicability + family-default estimation_methods awaiting "
            "rubric upgrade via define-metrics. "
            "Generated by scripts/build_seed_v2.py from "
            "scripts/_seed_v2_data.py + scripts/_seed_v2_metrics_data.py — "
            "do not hand-edit; edit the source data and re-run the build."
        ),
        "default_system_status": "bootstrap-stub",
        "default_metric_status": "bootstrap-stub",
        "systems": systems,
        "metrics": metrics,
    }
    dump_yaml(out, OUT_FILE)
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT).as_posix()}")
    print(f"  systems:                  {len(systems)}")
    print(f"  duplicates skipped:       {skipped_dupes}")
    if skipped_classes:
        print(f"  unresolved class slugs:  {sorted(skipped_classes)}")
    if skipped_domains:
        print(f"  unresolved domain slugs: {sorted(skipped_domains)}")
    print(f"  metrics:                  {len(metrics)}")
    print(f"  metric duplicates skipped:{metric_dupes}")
    if skipped_families:
        print(f"  unresolved family slugs: {sorted(skipped_families)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
