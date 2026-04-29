"""Bulk-import the catalog from `config/bootstrap_seed.yaml`.

Writes one `registry/systems/sys-NNNNNN--<slug>/system.yaml` per system
entry and one `registry/metrics/mtr-NNNNNN--<slug>/metric.yaml` per
metric entry. Allocates IDs in seed-file order, padded to 6 digits.

Idempotent on slug: if a system or metric directory already exists for
a slug, the script reuses the existing ID rather than allocating a new
one (a re-run after partial failure picks up where it left off).

Manifest shape (top-level YAML):

```yaml
phase_label: bootstrap-v1
description: |
  ...

systems:
  - slug: <kebab-case>
    name: <human-readable>
    domain: <system-domain slug>          # required
    classes: [<system-class slug>, ...]    # required (>=1)
    priority: P0 | P1 | P2 | P3 | C        # optional
    system_kind: class | transition | ...  # optional, default `class`
    substrate: <free text>                 # optional
    origin: natural | designed | ...       # optional
    boundary_clarity: crisp | fuzzy | ...  # optional
    primary_function: <free text>          # optional
    lifecycle_stage: maturity | ...        # optional
    summary: <multi-line>                  # optional but recommended
    boundary:                              # required
      type: spatial | temporal | ...
      description: <multi-line>
    components: [<bullet>, ...]            # required, >=1
    interaction_types: [<bullet>, ...]     # required, >=1
    scales:                                # required
      spatial: [<descriptor>, ...]
      temporal: [<descriptor>, ...]
    main_feedbacks: [<bullet>, ...]        # optional
    dominant_constraints: [<bullet>, ...]  # optional
    emergent_properties: [<bullet>, ...]   # optional
    failure_modes: [<bullet>, ...]         # optional
    primary_resources: [<bullet>, ...]     # optional
    canonical_examples:                    # optional but recommended
      - { name: <text>, note: <text> }
    aliases: [<text>, ...]                 # optional

metrics:
  - slug: <kebab-case>
    name: <human-readable>
    family: <metric-family slug>           # required
    value_type: continuous | discrete | ...# required
    description: <multi-line>              # required
    estimation_methods: [<bullet>, ...]    # required, >=1
    applicability:                         # optional but recommended
      requires: [<text>, ...]
      excludes: [<text>, ...]
    unit: <text> | null                    # optional
    directionality: ...                    # optional
    scale_level: micro | meso | macro      # optional
    maturity_level: L0..L5                 # optional
    normalization:                         # optional
      strategy: <text>
    evidence_requirements:                 # optional, defaults below
      minimum_source_count: 1
      review_required: true
```

Stub fields default sensibly:

* system `status` = `bootstrap-stub` (so plan-backlog Tier 3
  picks it up for upgrade once `phase=metrics-fill`).
* metric `status` = `bootstrap-stub`, `evidence_requirements`
  defaults to `{minimum_source_count: 1, review_required: true}`,
  `maturity_level` defaults to `L0`.

The script writes only the canonical YAML files. It does **not**
write `notes.md`, `links.yaml`, `relations.yaml`, or rubrics — those
are filled in later by curation passes.

Usage:

    uv run python scripts/bootstrap_from_seed.py             # dry run
    uv run python scripts/bootstrap_from_seed.py --apply     # write files
    uv run python scripts/bootstrap_from_seed.py --apply -v  # noisy

Run `uv run coc validate` after `--apply` to confirm. Exit code is
non-zero if any seed entry would fail validation.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from coc.paths import REG_METRICS, REG_SYSTEMS  # noqa: E402
from coc.schemas import validate_instance  # noqa: E402
from coc.taxonomy import load_index  # noqa: E402
from coc.yamlio import dump_yaml, load_yaml  # noqa: E402

SEED_FILE = REPO_ROOT / "config" / "bootstrap_seed.yaml"
SEED_GLOB = "bootstrap_seed*.yaml"  # picks up bootstrap_seed.yaml + bootstrap_seed_v2.yaml + future tiers

SLUG_RE = re.compile(r"^[a-z0-9-]+$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def existing_id(folder: Path, prefix: str, slug: str) -> str | None:
    """Return existing dir name `{prefix}-NNNNNN--{slug}` if present, else None."""
    if not folder.exists():
        return None
    for p in folder.iterdir():
        if p.is_dir() and p.name.endswith(f"--{slug}"):
            return p.name
    return None


def next_id(folder: Path, prefix: str, slug: str) -> str:
    """Allocate the next free `{prefix}-NNNNNN--{slug}` based on the highest extant integer."""
    existing = existing_id(folder, prefix, slug)
    if existing is not None:
        return existing
    folder.mkdir(parents=True, exist_ok=True)
    used: set[int] = set()
    pat = re.compile(rf"^{re.escape(prefix)}-([0-9]{{6}})--")
    for p in folder.iterdir():
        if not p.is_dir():
            continue
        m = pat.match(p.name)
        if m:
            used.add(int(m.group(1)))
    n = 1
    while n in used:
        n += 1
    return f"{prefix}-{n:06d}--{slug}"


def build_system_record(entry: dict, sys_id: str, ts: str, default_status: str = "bootstrap-stub") -> dict:
    """Translate a seed entry into a system.yaml record (v0.2 shape).

    `default_status` is supplied per seed file (see seed file's top-level
    `default_status` field). Entry-level `status` overrides; absence
    falls back to the file-level default; final fallback is bootstrap-stub.
    """
    domain = entry["domain"]
    classes = entry.get("classes", [])
    taxonomy_refs = [f"system-domain:{domain}"]
    taxonomy_refs.extend(f"system-class:{c}" for c in classes)

    rec: dict = {
        "id": sys_id,
        "slug": entry["slug"],
        "name": entry["name"],
        "status": entry.get("status", default_status),
        "taxonomy_refs": taxonomy_refs,
        "boundary": entry["boundary"],
        "components": entry["components"],
        "interaction_types": entry["interaction_types"],
        "scales": entry["scales"],
        "created_at": ts,
        "updated_at": ts,
    }

    # Optional v0.1 fields
    if "aliases" in entry:
        rec["aliases"] = entry["aliases"]
    if "summary" in entry:
        rec["summary"] = entry["summary"]
    if "source_refs" in entry:
        rec["source_refs"] = entry["source_refs"]
    if "canonical_examples" in entry:
        rec["canonical_examples"] = entry["canonical_examples"]

    # Optional v0.2 fields
    for k in (
        "priority",
        "system_kind",
        "substrate",
        "origin",
        "boundary_clarity",
        "primary_function",
        "lifecycle_stage",
        "main_feedbacks",
        "dominant_constraints",
        "emergent_properties",
        "failure_modes",
        "primary_resources",
    ):
        if k in entry:
            rec[k] = entry[k]

    return rec


def build_metric_record(entry: dict, mtr_id: str, default_status: str = "bootstrap-stub") -> dict:
    """Translate a seed entry into a metric.yaml record (v0.2 shape)."""
    rec: dict = {
        "id": mtr_id,
        "slug": entry["slug"],
        "name": entry["name"],
        "family": entry["family"],
        "status": entry.get("status", default_status),
        "value_type": entry["value_type"],
        "description": entry["description"],
        "applicability": entry.get("applicability", {}),
        "estimation_methods": entry["estimation_methods"],
        "evidence_requirements": entry.get(
            "evidence_requirements",
            {"minimum_source_count": 1, "review_required": True},
        ),
    }
    if "unit" in entry:
        rec["unit"] = entry["unit"]
    if "directionality" in entry:
        rec["directionality"] = entry["directionality"]
    if "scale_level" in entry:
        rec["scale_level"] = entry["scale_level"]
    if "maturity_level" in entry:
        rec["maturity_level"] = entry["maturity_level"]
    if "normalization" in entry:
        rec["normalization"] = entry["normalization"]
    return rec


def check_taxonomy(entry: dict, kind: str, index, where: str) -> list[str]:
    """Pre-validate domain/class/family slugs against the loaded taxonomy."""
    problems: list[str] = []
    if kind == "system":
        domain = entry.get("domain")
        if not domain or not index.has(f"system-domain:{domain}"):
            problems.append(f"{where}: unknown system-domain '{domain}'")
        for c in entry.get("classes") or []:
            if not index.has(f"system-class:{c}"):
                problems.append(f"{where}: unknown system-class '{c}'")
    elif kind == "metric":
        fam = entry.get("family")
        if not fam or not index.has(f"metric-family:{fam}"):
            problems.append(f"{where}: unknown metric-family '{fam}'")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Bulk-import catalog from config/bootstrap_seed*.yaml. "
        "Reads all matching files; later files extend earlier ones (slug-level idempotent)."
    )
    ap.add_argument("--apply", action="store_true", help="Write files (default is dry run)")
    ap.add_argument(
        "--seed",
        default=None,
        help="Path to a single seed YAML (overrides the default config/bootstrap_seed*.yaml glob)",
    )
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if args.seed:
        seed_paths = [Path(args.seed)]
        if not seed_paths[0].exists():
            print(f"ERROR: seed file not found: {seed_paths[0]}", file=sys.stderr)
            return 2
    else:
        seed_paths = sorted((REPO_ROOT / "config").glob(SEED_GLOB))
        if not seed_paths:
            print(f"ERROR: no seed files found (looked for config/{SEED_GLOB})", file=sys.stderr)
            return 2

    systems: list[dict] = []
    metrics: list[dict] = []
    # Track default status per seed file. Systems and metrics have distinct
    # status enums (candidate is valid for systems, not metrics) so the seed
    # file may declare them separately. Falls back to a single
    # `default_status` (kept for back-compat), then to bootstrap-stub.
    sys_default_status: dict[int, str] = {}
    mtr_default_status: dict[int, str] = {}
    for sp in seed_paths:
        data = load_yaml(sp) or {}
        sys_block = data.get("systems") or []
        mtr_block = data.get("metrics") or []
        legacy_ds = data.get("default_status", "bootstrap-stub")
        ds_sys = data.get("default_system_status", legacy_ds)
        ds_mtr = data.get("default_metric_status", "bootstrap-stub" if legacy_ds == "candidate" else legacy_ds)
        for entry in sys_block:
            sys_default_status[id(entry)] = ds_sys
        for entry in mtr_block:
            mtr_default_status[id(entry)] = ds_mtr
        systems.extend(sys_block)
        metrics.extend(mtr_block)
        print(
            f"Loaded {sp.relative_to(REPO_ROOT).as_posix()}: "
            f"{len(sys_block)} systems (default={ds_sys}), "
            f"{len(mtr_block)} metrics (default={ds_mtr})"
        )
    # Slug-level dedup (later occurrence loses; earlier file wins).
    seen_sys: set[str] = set()
    deduped_sys: list[dict] = []
    for e in systems:
        s = e.get("slug")
        if s and s not in seen_sys:
            seen_sys.add(s)
            deduped_sys.append(e)
    seen_mtr: set[str] = set()
    deduped_mtr: list[dict] = []
    for e in metrics:
        s = e.get("slug")
        if s and s not in seen_mtr:
            seen_mtr.add(s)
            deduped_mtr.append(e)
    systems = deduped_sys
    metrics = deduped_mtr
    print(f"Seed (deduped): {len(systems)} systems, {len(metrics)} metrics")

    index = load_index()
    ts = now_iso()
    problems: list[str] = []
    written: list[str] = []
    skipped: list[str] = []

    # --- Systems ---
    for i, entry in enumerate(systems):
        slug = entry.get("slug", "")
        if not SLUG_RE.match(slug):
            problems.append(f"systems[{i}]: bad slug '{slug}'")
            continue
        where = f"systems[{i}] slug={slug}"
        problems.extend(check_taxonomy(entry, "system", index, where))
        # Required fields
        for k in ("name", "domain", "classes", "boundary", "components", "interaction_types", "scales"):
            if k not in entry:
                problems.append(f"{where}: missing required field '{k}'")

        if any(p.startswith(where + ":") for p in problems):
            continue

        sys_id = next_id(REG_SYSTEMS, "sys", slug)
        rec = build_system_record(entry, sys_id, ts, default_status=sys_default_status.get(id(entry), "bootstrap-stub"))
        # Schema check before writing
        errs = validate_instance("system", rec)
        if errs:
            for e in errs:
                problems.append(f"{where}: {e}")
            continue

        target_dir = REG_SYSTEMS / sys_id
        target = target_dir / "system.yaml"
        if target.exists():
            skipped.append(target.relative_to(REPO_ROOT).as_posix())
            if args.verbose:
                print(f"SKIP exists  {target.relative_to(REPO_ROOT)}")
            continue

        if args.apply:
            target_dir.mkdir(parents=True, exist_ok=True)
            dump_yaml(rec, target)
            written.append(target.relative_to(REPO_ROOT).as_posix())
            if args.verbose:
                print(f"WRITE        {target.relative_to(REPO_ROOT)}")
        else:
            written.append(target.relative_to(REPO_ROOT).as_posix())

    # --- Metrics ---
    for i, entry in enumerate(metrics):
        slug = entry.get("slug", "")
        if not SLUG_RE.match(slug):
            problems.append(f"metrics[{i}]: bad slug '{slug}'")
            continue
        where = f"metrics[{i}] slug={slug}"
        problems.extend(check_taxonomy(entry, "metric", index, where))
        for k in ("name", "family", "value_type", "description", "estimation_methods"):
            if k not in entry:
                problems.append(f"{where}: missing required field '{k}'")
        if any(p.startswith(where + ":") for p in problems):
            continue

        mtr_id = next_id(REG_METRICS, "mtr", slug)
        rec = build_metric_record(entry, mtr_id, default_status=mtr_default_status.get(id(entry), "bootstrap-stub"))
        errs = validate_instance("metric", rec)
        if errs:
            for e in errs:
                problems.append(f"{where}: {e}")
            continue

        target_dir = REG_METRICS / mtr_id
        target = target_dir / "metric.yaml"
        if target.exists():
            skipped.append(target.relative_to(REPO_ROOT).as_posix())
            if args.verbose:
                print(f"SKIP exists  {target.relative_to(REPO_ROOT)}")
            continue

        if args.apply:
            target_dir.mkdir(parents=True, exist_ok=True)
            dump_yaml(rec, target)
            written.append(target.relative_to(REPO_ROOT).as_posix())
            if args.verbose:
                print(f"WRITE        {target.relative_to(REPO_ROOT)}")
        else:
            written.append(target.relative_to(REPO_ROOT).as_posix())

    print()
    print(f"Files {'written' if args.apply else 'pending (dry run)'}: {len(written)}")
    print(f"Files skipped (already exist):                 {len(skipped)}")
    print(f"Validation problems:                           {len(problems)}")
    for p in problems[:50]:
        print(f"  ! {p}")
    if len(problems) > 50:
        print(f"  ... and {len(problems) - 50} more")
    if not args.apply:
        print()
        print("(Dry run. Re-run with --apply to write files.)")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
