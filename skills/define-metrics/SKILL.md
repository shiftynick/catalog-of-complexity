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

Use this skill when a metric that `extract-observations` or `scout-systems` needs does not yet exist in `registry/metrics/`, or when an existing metric's rubric has gaps that block repeatable extraction.

Do **not** use this skill to record measurements — that is `extract-observations`. Do **not** use it to propose new metric families (taxonomy changes go through `taxonomy-proposal` tasks).

## Preconditions

- `family_slug` resolves in `taxonomy/source/metric-families.yaml`.
- The next free `mtr-NNNNNN` ID has been determined: `ls registry/metrics | sort | tail -1`, then increment.
- `candidate_description` is substantive (>= 1 paragraph).

## Procedure

1. Allocate the metric ID: `mtr-NNNNNN--<metric_slug>` where N is the next unused zero-padded 6-digit integer.
2. Read 2-3 canonical sources for the metric. Capture:
   - The mathematical or operational definition.
   - Units / dimensionless status.
   - Known applicability boundaries (value domain, system classes where it fails, common pitfalls).
   - Typical observed ranges.
3. Draft `metric.yaml` with all required fields from [metric.schema.json](../../schemas/metric.schema.json):
   - `id`, `slug`, `name`, `status: active`.
   - `taxonomy_refs` including `metric-family:*` and optionally `system-class:*` for restricted applicability.
   - `definition`, `unit`, `value_kind`, `applicability` (object with `required_system_properties`, `undefined_when`, `cautions`).
   - `created_at`, `updated_at`.
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
