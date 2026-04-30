---
name: fill-system-metrics
description: >
  Walk the metric registry against one fully-profiled system, identify
  all applicable metrics, and extract observations for each in a single
  integrated pass. One task per system; produces typically 50-100
  observation rows across many metric-family files in one git commit.
  Replaces the per-(system, metric-family) shape of extract-observations
  for the matrix-fill phase. Phase-driven (only fires under
  matrix-fill); not directly tier-emitted.
status: active
inputs:
  - 'system_id — sys-NNNNNN--<slug>; must exist with status `candidate` or `profiled` (NOT `bootstrap-stub`).'
  - 'metric_filter — optional list of metric_ids. If absent, walk every metric with status in (`proposed`, `canonical`). If present, restrict to that subset (used by review-records when re-extracting after rubric changes).'
  - 'review_state — initial state for new observations. Default `auto-validated`; use `proposed` when the agent specifically wants human eyes on this batch before downstream consumption.'
outputs:
  - 'Many appended rows in `registry/observations/<system>/<topic>.jsonl` (one .jsonl per metric family). Append-only.'
  - 'Many appended rows in `registry/sources/<src>/evidence.jsonl` for evidence cited in newly-extracted observations.'
  - 'Zero or more `acquire-source` task manifests in `ops/tasks/inbox/` for cited prefixed refs not yet registered. The fill task does NOT block on these; it gracefully classifies dependent observations as `blocked-source-not-acquired` and continues.'
  - 'A run.json summary listing applicable_metrics, observations_extracted, metrics_skipped_undefined, metrics_blocked_source_not_acquired, acquire_source_tasks_emitted.'
stop_conditions:
  - 'Every metric in scope has been classified into exactly one of: {extracted, skipped_undefined, blocked_source_not_acquired}.'
  - 'All extracted observations validate against `schemas/observation.schema.json` (v0.3 — including `run_id` and `produced_by_task_id` set to this task''s identifiers).'
  - 'For every blocked_source_not_acquired entry, an acquire-source task either already exists or has been emitted in this pass (idempotent on prefixed-ref).'
---

## When to use

This skill is the **primary task type for `phase: matrix-fill`**. It is
emitted by the autonomous-run worklist resolver, one task per system,
in priority-then-domain-interleave order (P0 first, then round-robin
across domains within each priority bucket).

It is also emitted opportunistically by `review-records` when a metric
rubric change invalidates prior observations — in that case
`metric_filter` constrains the re-extraction scope.

Do **not** use this skill to:

- Fill a single (system, metric) cell — that's still
  `extract-observations`'s shape and remains valid for one-off / manual
  curation.
- Profile a system — that's `profile-system`. This skill assumes the
  system is already substantively profiled.
- Define a metric — that's `define-metrics`. This skill assumes every
  in-scope metric has a rubric.

## Preconditions

- `system_id` exists in `registry/systems/` with status `candidate`
  or `profiled`. **Block** with `system-not-profiled` if status is
  `bootstrap-stub` (defensive — phase ordering should make this
  impossible, but the check costs nothing).
- The system has at least 4 of the 9 v0.2 structural facets populated
  (`system_kind`, `substrate`, `origin`, `boundary_clarity`,
  `primary_function`, `lifecycle_stage`, `main_feedbacks`,
  `dominant_constraints`, `emergent_properties`, `failure_modes`,
  `primary_resources`). **Block** with `system-profile-thin` otherwise.
- The metric registry contains at least one metric with status
  `proposed` or `canonical`. (Vacuously satisfied after metric-definition
  phase completes.)

## Procedure

1. **Load the system's full context.** Read
   `registry/systems/<system_id>/system.yaml` plus its `notes.md` and
   any `relations.yaml` and `links.yaml` files. Internalize the
   archetype's boundary, components, scales, and v0.2 facets — these
   drive applicability decisions for every metric.

2. **Load the metric registry.** Read every
   `registry/metrics/mtr-*--<slug>/metric.yaml` with status in
   (`proposed`, `canonical`). If `metric_filter` is provided, restrict
   to that subset. Group by `family` for downstream output-file
   routing.

3. **For each metric m in scope:**

   a) **Applicability check.** Walk `m.applicability.requires` and
      `m.applicability.excludes` against the system's profile. Examples:

      - `requires: [explicit_graph_representation]` → only fires if the
        system has an obvious graph view (most do; some boundary cases
        like `simple-pendulum` don't).
      - `excludes: [systems_without_interaction_model]` → skips entries
        whose interactions are described qualitatively only.

      If the metric is **not applicable**, append a `value_kind: undefined`
      observation with a one-sentence rationale in `notes`. Continue
      to the next metric. Count this as `skipped_undefined`.

   b) **Source check.** L0 / L1 metrics (qualitative tags, ordinal
      scores) and most L2 metrics on textbook archetypes can be
      extracted from the agent's canonical knowledge — no source
      lookup needed; cite the system's existing `source_refs` if any.
      L2+ metrics that need specific datasets or measured values
      (e.g. `lyapunov-exponent` for a specific oscillator) require
      registered sources.

      For each cited prefixed ref (`doi:`, `arxiv:`, `isbn:`, `url:`)
      that is NOT yet registered in `registry/sources/`:

      - Check whether an `acquire-source` task already exists in
        `ops/tasks/{inbox,ready,leased,blocked}/` with `notes` starting
        with `"Source debt: <ref>."`. If so, skip emitting a duplicate.
      - Otherwise emit one `acquire-source` task per missing ref into
        `ops/tasks/inbox/` with `notes: "Source debt: <ref>. Referenced
        by <this-task-id>."`.
      - Classify m as `blocked-source-not-acquired`. Append a
        `value_kind: undefined` observation with `notes: "blocked: cited
        ref <ref> not yet registered; acquire-source task <tsk-...>
        emitted"`. Continue to the next metric.

      **Critical: do NOT block the whole fill task.** The `extract-observations`
      "block on source-not-acquired" pattern is wrong here — one missing
      ref out of fifty would waste a task. We classify and continue.

   c) **Extraction.** Apply the metric's rubric to the system. Capture:

      - `value` (numeric / string / boolean) and `unit`
      - `value_kind` — one of `direct | derived | proxy | simulation | expert_estimate`
      - `confidence` (0.0–1.0) — based on source quality, derivation
        distance, and applicability fit
      - `uncertainty` (when meaningful) — `{type, lower?, upper?, note?}`
      - `assumptions[]` — interpretive choices made (e.g. "edges
        treated as undirected", "weighted by interaction frequency")
      - `source_refs[]` — registered `src-*` ids used; may be empty for
        L0/L1 metrics on textbook archetypes
      - `evidence_refs[]` — newly-appended `evi-*` ids for any cited
        passages (append to the source's `evidence.jsonl`)
      - `scale_level` — should match the metric's declared scale_level
        unless drilling in
      - `temporal_context` / `spatial_context` — for time- or
        place-specific values
      - `run_id` — this task's run-<ulid> (v0.3 schema field)
      - `produced_by_task_id` — this task's tsk-id (v0.3 schema field)
      - `review_state: auto-validated` (default) or `proposed`

      Append the observation to
      `registry/observations/<system>/<m.family>.jsonl`. Create the file
      if it does not exist. Count this as `extracted`.

4. **Validate.** `uv run coc validate registry/observations/<system_id>/`
   and `uv run coc validate registry/sources/<src>/` for every source
   that received new evidence rows.

5. **Run report.** Write `ops/runs/YYYY/MM/DD/<run_id>/run.json` with:

   ```json
   {
     "task_id": "<tsk-id>",
     "agent": {"runtime": "claude-code", "model": "<...>"},
     "started_at": "<ISO>",
     "ended_at": "<ISO>",
     "status": "success",
     "outputs": [
       "registry/observations/<system>/<topic>.jsonl",
       "registry/observations/<system>/<topic>.jsonl",
       "..."
     ],
     "events_appended": <int>,
     "notes": "applicable_metrics=N extracted=X skipped_undefined=Y blocked_source_not_acquired=Z acquire_source_tasks_emitted=K"
   }
   ```

6. **Complete.** `uv run coc complete <task-id> --state done --outputs '<json>'`.

## Output shape

- Many appended JSONL rows across `registry/observations/<system>/`.
  Typically 50–100 observations per task across 8–14 family files.
- Append-only: never rewrite a prior observation in place. Corrections
  go through `review-records` with explicit supersede semantics.
- One git commit covering all writes for this task.

## Block or fail when

- The system's status is `bootstrap-stub` — block with `system-not-profiled`.
- The system has fewer than 4 of the 9 v0.2 structural facets populated
  — block with `system-profile-thin`.
- More than 50% of in-scope metrics blocked on source-not-acquired —
  block with `excessive-source-debt`. The acquire-source backlog should
  be drained before re-attempting on this system; otherwise the task is
  mostly empty and the retros will fire on near-empty extractions.
- Per-iteration soft budget exceeded (default 60 minutes for matrix-fill
  phase; configured in `config/autorun.yaml::budgets.matrix-fill`) —
  partial-success: complete with `status: blocked` and `partial_extraction`
  in notes. The next sweep will retry on the same system. Observations
  are append-only so partial work isn't wasted.

## How re-extraction works

After a metric's rubric changes (via `define-metrics` in upgrade mode
or `review-records`), prior observations against that metric become
candidates for re-extraction. A `review-records` task will:

1. Identify affected (system, metric) pairs by querying observations
   with `metric_id = <m>` and `produced_by_task_id` whose run pre-dated
   the rubric change.
2. Mark those observations `review_state: superseded`.
3. Emit one `fill-system-metrics` task per affected system with
   `metric_filter: [<changed-metric-ids>]`. The fill task re-extracts
   only those metrics, not the full registry.

This is why the v0.3 schema added `run_id` and `produced_by_task_id`
as queryable fields — they make this audit trail tractable.

## References

- [schemas/observation.schema.json](../../schemas/observation.schema.json)
  — v0.3 observation record shape, including `run_id` /
  `produced_by_task_id`.
- [schemas/task.schema.json](../../schemas/task.schema.json) — task
  type enum (added `fill-system-metrics` in v0.3).
- [skills/extract-observations/SKILL.md](../extract-observations/SKILL.md)
  — single-cell shape, retained for one-off and review-driven curation.
- [skills/profile-system/SKILL.md](../profile-system/SKILL.md) — what
  "fully profiled" means; this skill's preconditions depend on it.
- [skills/define-metrics/SKILL.md](../define-metrics/SKILL.md) — what
  "rubric exists" means; this skill's per-metric rubric application
  depends on it.
- [docs/framework/03-metric-ontology.md](../../docs/framework/03-metric-ontology.md)
  §22 (maturity ladder), §23 (core required metric set), §24 (optional
  modules) — guidance on which metrics apply to which system kinds.
