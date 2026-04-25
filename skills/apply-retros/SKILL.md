---
name: apply-retros
description: Consume unprocessed retrospectives, cluster their proposed_improvements by target file, and emit one well-scoped review-records task per cluster. Does not apply edits directly — edits stay under human-reviewable `review-records` gating. Closes the feedback loop so retrospectives actually change the system.
status: active
inputs:
  - 'window_days — how far back to scan ops/retrospectives/ for unconsumed entries. Default 7.'
  - 'severity_floor — minimum proposal severity to include. One of `minor`, `moderate`, `major`. Default `moderate`.'
  - 'max_clusters — cap on number of clusters emitted per run (each cluster becomes one review-records task). Default 5.'
outputs:
  - 'One ops/tasks/inbox/tsk-YYYYMMDD-NNNNNN.yaml per cluster (type `review-records`).'
  - 'ops/runs/YYYY/MM/DD/<run-id>/retro-consumption.md summarising consumed retros, clusters formed, and per-target rationale.'
  - 'One ops/events/run-events.jsonl append of kind `retro.consumed` per retro processed (regardless of whether any proposal survived the severity filter).'
stop_conditions:
  - 'All in-window retros already appear as subjects of `retro.consumed` events — nothing to do, exit cleanly with a consumption report noting zero clusters.'
  - '`max_clusters` clusters emitted — further work rolls forward to the next run.'
  - 'Every candidate proposal has `target` pointing to a path that does not exist on disk — block the task, do not emit clusters against ghost paths.'
---

## When to use

Retrospectives pile up faster than humans can review them. Without a
consumer, `proposed_improvements` becomes write-only and the feedback loop
is broken. Use this skill on a cadence (queue-driven — a reviewer or a cron
promotes an `apply-retros` task from `inbox/` to `ready/`, typically weekly)
to aggregate and route.

Use this skill to:

- Cluster related proposals so AGENTS.md / a SKILL.md / a schema gets *one*
  thoughtful review task, not N duplicates.
- Mark processed retros so the next run doesn't re-cluster them.
- Escalate proposal clusters that touch non-negotiables or sensitive paths.

Do **not** use this skill to:

- Edit `AGENTS.md`, `SKILL.md`, schemas, or prompts directly. Edits go
  through `review-records`, which has its own quality bar and human
  checkpoint.
- Edit the retrospective files themselves. Retros are immutable; use the
  `retro.consumed` event as the processed-marker.
- Drop proposals silently. Below-threshold severities are summarised in the
  consumption report with an explicit "skipped: below severity_floor" note.

## Preconditions

- `ops/retrospectives/` exists and contains at least one retro within
  `window_days`.
- `ops/events/run-events.jsonl` is readable (for `retro.consumed` lookups).
  If missing, treat all in-window retros as unconsumed.
- `coc validate` passes on the repo before starting — edits emitted as
  review-records tasks must start from a valid baseline.

## Procedure

1. Load the consumed-retro set: every `event_id` in
   `ops/events/run-events.jsonl` of kind `retro.consumed` has its `subject`
   (a `retro_id`) added to a set.
2. Walk `ops/retrospectives/YYYY/MM/DD/retro-*.md`. For each file:
   - Parse its YAML frontmatter.
   - Skip if `retro_id` is in the consumed set.
   - Skip if the retro's `timestamp` is older than `window_days`.
3. From the remaining retros, collect `proposed_improvements` whose
   `severity` meets `severity_floor` (ordering: `minor` < `moderate` <
   `major`; a missing `severity` is treated as `minor`).
4. Cluster by `target`:
   - Group proposals sharing the exact `target` path.
   - If two targets are sibling SKILL.md files under the same skill dir,
     keep them separate — one skill per cluster.
5. For each cluster (up to `max_clusters`, ordered by cluster size
   descending then by severity max descending):
   - Verify the `target` path exists on disk. If it does not, skip this
     cluster and note "ghost-target" in the consumption report.
   - **Already-satisfied skip** (narrow form, analogous to "ghost-target"):
     when the target is `taxonomy/source/*.yaml` or
     `schemas/*.schema.json` and *every* proposal in the cluster requests
     adding a single named slug, key, or enum value that already resolves
     in the target, skip the cluster and note "already-satisfied" in the
     consumption report. Keep the satisfaction check deliberately narrow
     to avoid false-positive skips on substantive content edits:
     - YAML taxonomy: a proposal naming `<prefix>:<slug>` (e.g.
       `system-class:atomic-system`) is satisfied iff an entry under the
       file's top-level `items:` list has `slug: <slug>`.
     - JSON Schema: a proposal naming a property or enum value at an
       indicated path (e.g. "add `sources-resolved` to
       `properties.unblock.properties.kind.enum`") is satisfied iff that
       exact name already resolves at that path in the schema.
     Any proposal in the cluster that does not match one of these narrow
     forms — or that requests anything beyond a pure additive slug/key
     check (e.g. wording revisions, reordering, behavioral changes in
     adjacent code) — defeats the skip: emit the cluster's
     review-records task and let the reviewer decide. The contributing
     retros are still marked `retro.consumed` per step 6; only the
     review-records emission is suppressed.
   - Compose a `review-records` task manifest with:
     - `type: review-records`, `skill: review-records`, `state: inbox`.
     - `priority` = `high` if any proposal in the cluster is
       `severity: major`, else `normal`.
     - `output_targets: [<target-path>]` — the review task will edit the
       target directly or emit a further proposal.
     - `notes` — a bullet-listed digest of the clustered proposals,
       including each source retro's `retro_id` for traceability.
     - `acceptance_tests` — the bare minimum: `uv run coc validate`
       must pass after the edit.
6. For **every** retro touched in step 2 (including those whose proposals
   did not survive filtering), append one `retro.consumed` event:
   ```json
   {
     "event_id": "ev-<ulid>",
     "timestamp": "<now>",
     "kind": "retro.consumed",
     "subject": "<retro_id>",
     "actor": "<agent-id>",
     "payload": {
       "proposals_considered": <int>,
       "proposals_clustered": <int>,
       "clusters_this_retro_contributed_to": ["<target-path>", "..."]
     }
   }
   ```
7. Write the consumption report to
   `ops/runs/YYYY/MM/DD/<run-id>/retro-consumption.md` with sections:
   **Window**, **Retros processed**, **Clusters emitted**, **Skipped
   targets**, **Errors (if any)**.
8. Validate: `uv run coc validate ops/tasks/inbox/`. If any emitted
   manifest fails, delete it, record the failure, set `status: blocked`.

## Output shape

- Inbox task manifests — valid against
  [schemas/task.schema.json](../../schemas/task.schema.json),
  `type: review-records`, `state: inbox`.
- Consumption report — free-form markdown, one file per run. No frontmatter.
- Event-log appends — valid against
  [schemas/event.schema.json](../../schemas/event.schema.json) with
  `kind: retro.consumed`.

## Block or fail when

- The only in-window retro has `actionable: false` and a consumed marker is
  already present → not a block, this is the cleanest possible outcome:
  emit zero clusters and exit `status: success`.
- A proposal's `target` resolves to a path outside the repo (absolute, or
  with `..` components) → treat as ghost-target, skip the cluster, and flag
  the originating retro in the report.
- The retrospective schema has drifted such that frontmatter no longer
  parses for a file in-window → block with `reason: retro-schema-drift`;
  schema changes are exactly what this loop is designed to catch.

## Cadence

Default cadence: **weekly**, queue-driven. A reviewer promotes one
`apply-retros` task from `inbox/` to `ready/` at a time. If
`proposals_clustered` counts in recent `retro.consumed` payloads trend to
zero across ≥4 consecutive runs, narrow the cadence to monthly and review
whether the retrospective skill itself should flip to
`postrun-onfailure` per the retirement policy in
[skills/retrospective/SKILL.md](../retrospective/SKILL.md).

## References

- [AGENTS.md](../../AGENTS.md) — quality bar, sensitive actions,
  non-negotiables.
- [skills/retrospective/SKILL.md](../retrospective/SKILL.md) — producer of
  the retros this skill consumes.
- [skills/review-records/SKILL.md](../review-records/SKILL.md) — consumer
  of the clusters this skill emits.
- [schemas/retrospective.schema.json](../../schemas/retrospective.schema.json)
  — retro frontmatter contract.
- [schemas/task.schema.json](../../schemas/task.schema.json) — emitted
  manifest contract.
- [schemas/event.schema.json](../../schemas/event.schema.json) —
  `retro.consumed` kind.
