---
name: extract-observations
description: Populate the system x metric matrix with values grounded in specific sources. Each observation carries a value, a value_kind, confidence, and at least one evidence reference.
status: active
inputs:
  - 'system_id — `sys-NNNNNN--<slug>`; must exist with status active.'
  - 'metric_ids — list of `mtr-NNNNNN--<slug>`; each must exist with status active.'
  - 'source_refs — list of `src-NNNNNN--<slug>` or DOIs; at least one per intended observation.'
  - 'review_state — initial state for new observations (`auto-validated` by default: agent judges the record acceptable and webUI prune is the review mechanism). Use `proposed` only when the agent explicitly wants human eyes before the record is treated as usable; `validated` is reserved for human or `review-records` sign-off.'
outputs:
  - 'Appended rows in `registry/observations/<system>/<topic>.jsonl` (one line per observation).'
  - 'Appended rows in `registry/sources/<src>/evidence.jsonl` (one line per evidence citation).'
  - 'No mutations to prior observations — append-only.'
stop_conditions:
  - 'One observation recorded per (system, metric) pair requested, or the pair explicitly marked as `value_kind` undefined with rationale.'
  - 'Every observation validates against `schemas/observation.schema.json`.'
  - 'Every observation references at least one evidence entry in the relevant `evidence.jsonl`.'
---

## When to use

Use this skill to fill values in the catalog. Trigger:

- An `extract-observations` task lands in `ops/tasks/ready/` naming a system and metrics.
- A review task flagged an observation as needing re-extraction under a new source.

Do **not** use this skill to define new metrics or profile new systems — use `define-metrics` or `profile-system`.

## Preconditions

- `system_id` and every `metric_id` already exist in the registry.
- Every `src-*` id in `source_refs` already has `source.yaml` and raw/parsed content on disk. If any entry uses a prefixed form (`doi:`, `arxiv:`, `url:`) that isn't yet registered, **block** the task with reason `source-not-acquired`. `plan-backlog` Tier 0.75 owns acquisition — it will queue an `acquire-source` task on the next run. Do not fabricate a `src-*` id and do not attempt to fetch inline.

## Procedure

1. Read `registry/systems/<system_id>/system.yaml` and `registry/metrics/<metric_id>/metric.yaml` for each metric. Check the metric's `applicability.required_system_properties` against the system. Skip pairs where the metric is undefined — record them explicitly (see step 5).
2. Read source content in this order:
   - If `registry/sources/<src>/parsed/` has content, read it first — it's
     cheapest and carries page/section locators directly usable in
     `evidence.locator`.
   - Otherwise read the raw artifact directly from
     `registry/sources/<src>/raw/` via the agent's native Read tool
     (Claude Code and Codex can both ingest PDFs). When citing from raw/,
     approximate the locator (e.g. "pp. 4-5, §Methods") using page numbers
     you observe in the PDF itself — the citation is still valid; it's
     just less programmatically indexable than a parsed/ extract.
   - Do not modify `raw/` — it's immutable.
3. For each (system, metric) pair:
   - Locate the passage(s) in the source(s) that contain the value or let you derive one.
   - Determine `value_kind`: one of `measured`, `derived`, `estimated`, `undefined`.
   - If numeric, capture `value_numeric` and `unit`. If textual or categorical, capture `value_text`. If boolean, `value_boolean`. If undefined, note why in `notes`.
   - Assign `confidence`: 0.0-1.0 based on source quality, derivation distance, and sample size. See rubric in [qc/evals/](../../qc/evals/) (Phase 9).
4. Append an evidence entry per citation to `registry/sources/<src>/evidence.jsonl`:
   - `evidence_id: evi-<8-hex>`, `source_id`, `locator` (page, section, line, or DOI fragment), `excerpt` (verbatim quote or paraphrase with citation).
5. Append an observation entry to `registry/observations/<system>/<topic>.jsonl` (create a new topic file if needed — use the metric family as the topic name):
   - `observation_id: obs-<8-hex>`, `system_id`, `metric_id`, value fields, `value_kind`, `unit`, `confidence`, `evidence_refs: [evi-*, ...]`, `review_state: auto-validated` (default — use `proposed` only if you specifically want a human pass before the record counts), `observed_at` (date the source reports the value, not the date you extracted it).
6. Run `uv run coc validate registry/observations/<system>/` and `uv run coc validate registry/sources/<src>/`.
7. Append a run report listing: (system, metric, value, confidence, evidence_refs) tuples and any pairs skipped with rationale.

## Output shape

- Observations are append-only JSONL. One JSON object per line. Never rewrite a line in place — if a prior observation needs correction, append a new one with `supersedes: obs-<prev-id>` and set the prior observation's `review_state: superseded` via a separate `review-records` task.
- The default `review_state: auto-validated` means the record is usable downstream immediately. A human (or a `review-records` pass) can later promote it to `validated` or append a supersede to reject it. The webUI prune workflow substitutes for pre-merge human review.
- Evidence rows are append-only JSONL.

## Block or fail when

- A source's parsed content is ambiguous or contradictory — block with the specific passage highlighted and a request for reviewer judgement.
- Numeric values require a unit conversion where the source unit is ambiguous (e.g. "count" with no denominator) — block.
- The metric's applicability forbids the system (e.g. a cycle-based metric on a strictly acyclic system) — record an `undefined` observation with rationale, do not block.
- Zero sources supply usable data for a requested pair — record an `undefined` observation with rationale.
- Any `source_refs` entry uses a prefixed form (`doi:`, `arxiv:`, `url:`)
  with no matching `registry/sources/src-*/` — block with reason
  `source-not-acquired`. plan-backlog Tier 0.75 owns acquisition.
- The source is registered but its `raw/` directory contains only
  metadata (`metadata.json`, `unpaywall.json`) with no full-text artifact
  — block with reason `source-metadata-only`. Metadata-only sources
  cannot ground specific observations; either wait for an OA copy to
  appear or route the request to a source with full-text access.

## References

- [schemas/observation.schema.json](../../schemas/observation.schema.json)
- [registry/sources/src-000001--example-review/evidence.jsonl](../../registry/sources/src-000001--example-review/evidence.jsonl) — reference shape.
- [registry/observations/sys-000001--amazon-rainforest/topology.jsonl](../../registry/observations/sys-000001--amazon-rainforest/topology.jsonl) — reference shape.
