---
name: define-metrics
description: Curate a metric's canonical definition, measurement rubric, applicability rules, and worked examples. Produces records in `registry/metrics/<id>/` that downstream `extract-observations` tasks bind to.
status: active
inputs:
  - 'metric_slug — kebab-case slug for the metric (e.g. `network-modularity`, `shannon-entropy`).'
  - 'family_slug — `metric-family:*` taxonomy slug (must exist in `taxonomy/source/metric-families.yaml`).'
  - 'candidate_description — prose description from a scouting pass or reviewer.'
  - 'prior_sources — list of source IDs or DOIs that define or use this metric.'
outputs:
  - '`registry/metrics/mtr-NNNNNN--<slug>/metric.yaml` — canonical definition (schema-validated).'
  - '`registry/metrics/mtr-NNNNNN--<slug>/rubric.md` — prose measurement guide with 3+ worked examples.'
  - '`registry/metrics/mtr-NNNNNN--<slug>/examples.yaml` — structured examples (system, raw data sketch, computed value).'
stop_conditions:
  - '`metric.yaml` validates against `schemas/metric.schema.json`, all taxonomy refs resolve, applicability conditions are explicit.'
  - '`rubric.md` contains at least 3 worked examples spanning at least 2 `system-domain` slugs.'
  - '`examples.yaml` contains at least 3 entries, each referencing a real system in the registry or a well-known canonical example (cited).'
---

## When to use

Use this skill in two trigger modes:

1. **New metric** — a metric that `extract-observations` or
   `scout-systems` needs does not yet exist in `registry/metrics/`.
   Allocate a fresh `mtr-NNNNNN` id; write canonical definition,
   rubric, worked examples.
2. **Stub upgrade** — bootstrap v0.1 imported 16 metric stubs (one per
   metric-family) at `status: bootstrap-stub` with placeholder
   rubrics. plan-backlog Tier 4 (metric debt, gated to `bootstrap` and
   `metrics-fill` phases) emits `define-metrics` tasks for these.
   Reuse the existing `mtr-*` id; rewrite `metric.yaml`; create
   `rubric.md` and `examples.yaml`; promote status from
   `bootstrap-stub` to `proposed` (or `canonical` if textbook-standard).

Also trigger when an existing metric's rubric has gaps that block
repeatable extraction (review-records flag).

Do **not** use this skill to record measurements — that is `extract-observations`. Do **not** use it to propose new metric families (taxonomy changes go through `taxonomy-proposal` tasks).

## Preconditions

- `family_slug` resolves in `taxonomy/source/metric-families.yaml`.
  v0.2 expanded the families to 16 (added causality, constraints,
  governance, environment, function-performance, failure-mode,
  potentials, comparative).
- For **new** mode: no `registry/metrics/mtr-*--<slug>/` exists; allocate
  the next free `mtr-NNNNNN` ID: `ls registry/metrics | sort | tail -1`,
  then increment.
- For **upgrade** mode: exactly one `registry/metrics/mtr-*--<slug>/`
  exists with `status: bootstrap-stub`; reuse its id and `family`.
- `candidate_description` is substantive (>= 1 paragraph). For upgrade
  mode the existing stub's `description` field provides the seed
  content.

## Procedure

1. Allocate the metric ID: `mtr-NNNNNN--<metric_slug>` where N is the next unused zero-padded 6-digit integer.
2. Read 2-3 canonical sources for the metric. Capture:
   - The mathematical or operational definition.
   - Units / dimensionless status.
   - Known applicability boundaries (value domain, system classes where it fails, common pitfalls).
   - Typical observed ranges.
3. Draft `metric.yaml` with all required fields from
   [metric.schema.json](../../schemas/metric.schema.json):
   - `id`, `slug`, `name`, `status` — `proposed` for new entries
     (awaiting review) or `canonical` for textbook-standard metrics
     where the rubric is well established. **Upgrade mode:** if a
     `bootstrap-stub` metric record already exists for this slug,
     reuse its `id` and rewrite `metric.yaml` in place, promoting
     status to `proposed` (or `canonical` if textbook-standard).
   - `family` — `metric-family:*` slug.
   - `description`, `value_type`, `unit`, `directionality`,
     `applicability` (object with `requires`, `excludes`).
   - `estimation_methods` (array, ≥1).
   - **v0.2 facets** — populate where meaningful:
     - `scale_level` — `micro | meso | macro | multi-scale`. The level
       of description the metric applies to. Examples: component-count
       is `micro`, modularity is `meso`, energy-throughput is `macro`,
       Bar-Yam multiscale-complexity is `multi-scale`.
     - `maturity_level` — `L0 | L1 | L2 | L3 | L4 | L5`. Maturity ladder
       from docs/framework/03-metric-ontology.md §22. L0 qualitative
       tag, L1 ordinal score, L2 direct numeric, L3 computed from
       data/model, L4 validated predictive, L5 cross-domain invariant
       candidate. Bootstrap-stub metrics typically sit at L0–L1; a
       full define-metrics pass with rubric and 3+ worked examples
       can promote to L2 or L3.
     - `normalization` — object with `strategy` field (e.g.
       `raw-and-zscore`, `domain-typical-normalization`,
       `none`). Optional but recommended.
   - `evidence_requirements` — `{minimum_source_count: integer,
     review_required: boolean}`. Default
     `{minimum_source_count: 1, review_required: true}` for proposed;
     bump `minimum_source_count: 2-3` for canonical.
4. Draft `rubric.md` — the measurement procedure a reviewer would follow. Include:
   - Operational steps (what data you need, how to compute).
   - 3+ worked examples across domains.
   - Failure modes: what makes the metric ill-defined or misleading.
5. Write `examples.yaml` — structured companion to the rubric. Each entry: `system_slug`, `data_sketch`, `computed_value`, `value_kind`, `notes`.
6. Run `uv run coc validate registry/metrics/mtr-NNNNNN--<slug>/`.
7. Append a run report listing: metric id, sources consulted, applicability decisions, open questions.

## Output shape

- `metric.yaml` — must match [metric.schema.json](../../schemas/metric.schema.json). Every taxonomy ref resolves.
- `rubric.md` — markdown, no YAML frontmatter. Structured with: Overview, Procedure, Worked Examples (>=3), Failure Modes.
- `examples.yaml` — list of `{system_slug, data_sketch, computed_value, value_kind, notes, source_ref}`.

## Block or fail when

- The metric's applicability cannot be narrowed to specific system properties (too generic or too vague) — block with the ambiguity documented.
- Fewer than 2 canonical sources exist for this metric — block; request a literature pass from `scout-systems`.
- The metric overlaps substantively with an existing `registry/metrics/` entry — block; propose a rename/merge task instead.

## References

- [schemas/metric.schema.json](../../schemas/metric.schema.json)
- [taxonomy/source/metric-families.yaml](../../taxonomy/source/metric-families.yaml)
- [registry/metrics/mtr-000001--network-modularity/](../../registry/metrics/mtr-000001--network-modularity/) — reference shape.
