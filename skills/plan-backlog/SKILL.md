---
name: plan-backlog
description: Two narrow responsibilities under the sweep autorun model — (1) source-debt sweep, embedded in every cron tick's preflight, that scans for prefixed `source_refs` (`doi:`, `arxiv:`, `url:`, `isbn:`) lacking a matching `registry/sources/src-*` and emits `acquire-source` task manifests; (2) periodic `apply-retros` trigger, fired every K new retrospectives. The legacy 8-tier hierarchy is gone — phase-driven catalog growth is now handled by `prompts/autonomous-run.md` via `coc.worklist` + `coc.dispatch`. plan-backlog is no longer queue-dispatched and no `plan-backlog` task type exists.
status: postrun
inputs:
  - 'sweep_kind — "source-debt" or "apply-retros". Defaults to "source-debt" when called from preflight.'
  - 'inbox_cap — maximum pending inbox manifests before treating the backlog as saturated. Default 20.'
outputs:
  - 'For source-debt: zero or more `ops/tasks/inbox/tsk-YYYYMMDD-NNNNNN.yaml` `acquire-source` manifests.'
  - 'For apply-retros: zero or one `ops/tasks/inbox/tsk-...` `apply-retros` manifest.'
stop_conditions:
  - 'Inbox already holds at least `inbox_cap` manifests — emit nothing.'
  - 'Sweep completed; emitted manifests validate against `schemas/task.schema.json`.'
---

## When to use

Two embeddings, both invoked directly from `prompts/autonomous-run.md`:

1. **Source-debt sweep** — runs in every preflight (before the
   worklist resolver fires). Scans active task manifests and emits
   acquire-source tasks for any cited prefixed ref not yet
   registered. Bounded by the active phase's `acquire-source` side-
   channel cap (`coc.phase.side_channel_cap("acquire-source")`):
   3 in system-profiling/metric-definition, 10 in matrix-fill, 3
   in analysis.
2. **Apply-retros trigger** — runs at the end of preflight when the
   number of new retros since the last apply-retros run exceeds K
   (default K=25). Emits a single apply-retros task into inbox/.
   The apply-retros skill consumes unprocessed retros and clusters
   `proposed_improvements` into review-records tasks.

Do **not** use this skill to:

- Promote tasks from `inbox/` to `ready/` — that is `coc advance`.
- Edit canonical records — those are out of scope and covered by
  `review-records` and human gatekeeping.
- Touch `registry/sources/*/raw/`.
- Walk the catalog growth tiers (Tier 0 / 0.5 / 1 / 2 / 3 / 4 / 5
  from the legacy version) — those responsibilities moved to the
  worklist resolver in `coc.worklist` and the autonomous-run prompt.

## Source-debt sweep procedure

1. Determine the cap N for this tick:
   `coc.phase.side_channel_cap("acquire-source")`. If
   `len(ops/tasks/inbox/) >= 20`, exit early — the backlog is
   saturated.
2. Walk every task manifest under
   `ops/tasks/{inbox,ready,leased,running,blocked}/`. For each
   manifest's `source_refs`, identify entries using prefixed forms
   (`doi:`, `arxiv:`, `url:`, `isbn:`). Skip entries already
   registered as `src-*`.
3. Build the candidate set: each unique unregistered prefixed ref
   plus the list of tasks referencing it.
4. **Idempotency:** skip a ref if any task under `ops/tasks/` already
   has `notes` starting with `"Source debt: <ref>."`.
5. For up to N remaining refs, emit one `acquire-source` task each
   with:
   - `source_refs: [<ref>]`
   - `notes: "Source debt: <ref>. Referenced by <tsk-id>[, <tsk-id>...]."`
   - Standard task-manifest fields (allocated id, state: inbox,
     priority: normal, lease ttl 60 min, max attempts 2, valid
     output_targets per the acquire-source skill).
6. **Unblock wiring** for blocked tasks whose ref is being acquired:
   set the blocked task's `unblock` field to
   `{kind: task-complete, task_id: <acquire-tsk-id>}` (or
   `{kind: sources-resolved}` when the blocked task references
   multiple refs and that schema kind exists). Edit the blocked
   manifest in place; do not move it out of `blocked/`. The next
   `coc advance` sweep flips it once the unblock fires.
7. `uv run coc validate ops/tasks/inbox/`.

## Apply-retros trigger procedure

1. Count retros under `ops/retrospectives/` whose `created_at` is
   newer than the most recent `apply-retros` task's `created_at`
   (or all retros if no apply-retros task has ever run).
2. If count < K (default 25), exit early.
3. Emit one `apply-retros` task with:
   - `output_targets: ["ops/tasks/inbox/", "ops/runs/"]`
   - `notes: "Auto-fired after <count> new retros since last apply-retros."`
4. `uv run coc validate ops/tasks/inbox/`.

## Block or fail when

- `coc validate` fails on a proposal you wrote. Delete it, record
  the failure in the run report, abort preflight with `run.aborted`.
- The selected ref would require a registry/sources schema change.
  Skip it; record in the run report.

## Retiring this skill

Once the source-debt backlog stays consistently empty for ≥20
consecutive ticks, the source-debt sweep can be retired (acquire-source
tasks would be emitted only by skills that explicitly cite
unregistered refs, e.g. fill-system-metrics during matrix-fill).
The apply-retros trigger remains useful indefinitely.

## References

- [AGENTS.md](../../AGENTS.md) — sensitive actions, quality bar.
- [prompts/autonomous-run.md](../../prompts/autonomous-run.md) —
  preflight caller for both responsibilities.
- [src/coc/phase.py](../../src/coc/phase.py) — `side_channel_cap()`
  for the active phase's acquire-source budget.
- [src/coc/worklist.py](../../src/coc/worklist.py),
  [src/coc/dispatch.py](../../src/coc/dispatch.py) — where the
  catalog-growth tiers went.
- [schemas/task.schema.json](../../schemas/task.schema.json) —
  manifest contract for emitted proposals.
- [skills/acquire-source/SKILL.md](../acquire-source/SKILL.md) —
  consumer of the source-debt sweep's output.
- [skills/apply-retros/SKILL.md](../apply-retros/SKILL.md) — consumer
  of the periodic trigger.
