---
name: review-records
description: QC sweep over auto-validated or proposed records. Validates schema conformance, citation grounding, applicability respect, and methodological soundness. Advances `review_state` from `auto-validated` or `proposed` to `validated` (human/agent sign-off) or returns records for revision. Also the dispatch target of the `apply-retros` improvement pipeline.
status: active
inputs:
  - 'record_scope — one of `system:<sys-id>`, `metric:<mtr-id>`, `source:<src-id>`, or `observations:<sys-id>[,<sys-id>...]`.'
  - 'reviewer_depth — `shallow` (schema + citations only) or `deep` (schema + citations + methodology + cross-record consistency).'
outputs:
  - 'Updates to `review_state` on individual records (new append rows for observations; in-place edits with `updated_at` bumps for systems/metrics).'
  - 'A review report at `ops/runs/YYYY/MM/DD/<run-id>/review-report.md` listing each record reviewed, verdict, and rationale.'
  - 'Zero or more follow-up tasks in `ops/tasks/inbox/` for records returned for revision.'
stop_conditions:
  - 'Every in-scope record has a terminal verdict — one of `validated`, `superseded`, `rejected`, or `needs-revision` (with a task queued).'
  - 'No schema-level errors remain in scope.'
---

## When to use

Use this skill to close the review loop on records that need a second pass. Trigger:

- An `extract-observations` or `profile-system` task has completed into `review/` state (rare under the autonomous policy — skills default to `done`, so `review` parking is an explicit escalation).
- A scheduled QC sweep checks a system or source's full record set — typically auto-validated records the webUI flagged or that accumulated past a coverage threshold.
- A reviewer has flagged a specific metric or system as suspect.
- An `apply-retros` pass clustered retrospective improvements against this target path and emitted this task.

Do **not** use this skill to create records or to edit canonical values in place — revision is always a new append or a new task.

## Preconditions

- The records in scope exist and validate against their schemas at the shape level (two-pass validator passes).
- Taxonomy exports are current.
- For `deep` review: at least 3 prior observations exist for the metrics in scope, to enable cross-record consistency checks.

## Procedure

1. Read all in-scope records. For observations, read the full JSONL file plus every referenced evidence and source.
2. Run `uv run coc validate <scope-path>`. Any failure halts the review for that record; queue a revision task.
3. For each record, check the quality-bar criteria from [AGENTS.md](../../AGENTS.md):
   - No uncited numeric claims.
   - Observation has `value_kind`, `confidence`, and >=1 `evidence_ref`.
   - Metric has explicit `applicability`.
   - System has `boundary`, `components`, `interaction_types`, `scales`.
   - Taxonomy refs resolve.
4. For `deep` review, additionally:
   - Verify the cited evidence excerpt actually supports the claimed value (spot-check the source parsed/ content).
   - Check applicability: does the metric's `required_system_properties` hold for this system?
   - Check consistency: does this observation contradict a prior validated observation for the same (system, metric)? If so, flag for adjudication.
5. Assign verdict to each record:
   - `validated`: update `review_state`. For observations, this means appending a new line with the updated state (JSONL is append-only) and marking the prior `auto-validated` or `proposed` line as superseded. For systems/metrics, edit `system.yaml` / `metric.yaml` in place with new `review_state` and `updated_at`. Promoting `auto-validated` → `validated` is the common case; promoting `proposed` → `validated` happens only when a prior agent explicitly asked for a human pass.
   - `needs-revision`: keep the current `review_state` (likely `auto-validated`; do not demote to `proposed` unless the record is genuinely suspect). Emit a task in `ops/tasks/inbox/` with specific revision requests.
   - `rejected`: append an observation with `review_state: rejected` and rationale. For systems/metrics, set `status: deprecated` and add a `notes.md` entry.
6. Write the review report with one section per record: identifier, verdict, rationale, follow-up task id if any.

## Output shape

- Review verdicts are durable: the record shows its new `review_state` after the sweep.
- The review report is the human-readable index; the authoritative state is in the record files.

## Block or fail when

- A source cited by an observation no longer exists on disk — block and emit a source-acquisition task.
- Two prior validated observations contradict each other for the same pair — block and escalate; do not silently resolve.
- Review depth requested exceeds the reviewer's evidence (e.g. `deep` asked for a system with only 1 observation) — downgrade to `shallow` and note in the report.

## References

- [AGENTS.md](../../AGENTS.md) — quality bar.
- [schemas/observation.schema.json](../../schemas/observation.schema.json)
- [schemas/event.schema.json](../../schemas/event.schema.json) — review events use `kind: record.review`.
