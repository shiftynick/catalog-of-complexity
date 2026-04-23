---
name: plan-backlog
description: Empty-queue branch of the autonomous run. Inspects registry coverage and existing task states, then proposes zero or more new task manifests into ops/tasks/inbox/ so the next scheduled run has productive work. Does not promote manifests to ready/ — that remains a human or review-records decision. Invoked directly by prompts/autonomous-run.md; not dispatched from the queue.
status: postrun
inputs:
  - 'run_id — id of the current run (used for the plan-report path).'
  - 'inbox_cap — maximum pending inbox manifests before treating the backlog as saturated. Default 20.'
outputs:
  - 'Zero or more ops/tasks/inbox/tsk-YYYYMMDD-NNNNNN.yaml proposals — valid against schemas/task.schema.json with state: inbox.'
  - 'ops/runs/YYYY/MM/DD/<run-id>/plan-report.md summarising the coverage scoreboard and what was proposed or skipped.'
stop_conditions:
  - 'Inbox already holds at least inbox_cap manifests — emit no new proposals, record saturation in the plan-report.'
  - 'A coverage gap was selected, the corresponding proposal was written, and coc validate accepts the new manifest(s).'
  - 'No coverage gap found after scanning all registry folders — write a plan-report marked saturated and exit.'
---

## When to use

This skill runs only when [`coc next`](../../src/coc/cli.py) reports an empty
`ops/tasks/ready/` queue during an autonomous run. It is invoked directly by
[prompts/autonomous-run.md](../../prompts/autonomous-run.md) — do not create
queue manifests of type `plan-backlog`; no such task type exists.

Use this skill to:

- Surface the next most-valuable work when the queue is idle.
- Translate registry coverage gaps into concrete task manifests.
- Keep the queue seeded so scheduled runs never stall on an empty queue.

Do **not** use this skill to promote tasks from `inbox/` to `ready/`, edit
canonical records, or touch `registry/sources/*/raw/`. Those are out of
scope and covered by `review-records` and by human gatekeeping.

## Preconditions

- `ops/tasks/ready/` is empty (otherwise Branch A of the autonomous run
  should have fired).
- `registry/` exists and `coc validate` passed in the run's preflight step.
- Taxonomy exports are current; if not, the plan-report should note the
  staleness and propose an `export-taxonomy` follow-up rather than propose
  skill tasks that depend on it.

## Procedure

1. Load the coverage scoreboard — cheap reads only:
   - Count systems by `status` (`candidate`, `validated`, `superseded`).
   - Count metrics by `status` and whether each has a rubric file.
   - Count observations per system from `registry/observations/**/*.jsonl`.
   - Count pending manifests per state under `ops/tasks/{inbox,blocked,review}/`.
2. Compare against the saturation cap:
   - If `len(inbox) >= inbox_cap`, skip all proposal emission — write only
     the plan-report with `status: saturated`.
3. Apply the gap heuristic, in priority order. Stop after the first tier
   that produces at least one proposal:
   0. **Bootstrap** — if `registry/systems/` has zero entries *and* there
      are fewer than 2 `scout-systems` tasks across `inbox/ + ready/`,
      emit **one `scout-systems` task per zero-count `system-domain`** up
      to `max_scouts_per_run: 3`, each with `Budget: 2 candidate systems`
      in `notes` (see Domain rotation below). Tier 0 fires only during
      true cold-start; once the registry has any system, later tiers
      take over.
   0.5. **Priority seed** — consume unfulfilled entries from
      [config/priority-systems.yaml](../../config/priority-systems.yaml)
      top-down. An entry is *fulfilled* when either
      `registry/systems/sys-*--<slug>/` exists or any task manifest under
      `ops/tasks/` carries `notes` beginning with
      `"Priority seed: <slug>."`. For the next up to 3 unfulfilled
      entries, emit a `scout-systems` task with `topic: <entry.name>`,
      `domain_hint: <entry.domain>`, and
      `notes: "Priority seed: <slug>. Target system-domain:<domain>.
      Budget: 1 candidate system."`. Cap of 3 matches the auto-promote
      per-type ready cap on `scout-systems`. This tier fires regardless
      of registry size (not just at cold-start) and takes priority over
      Tier 3's profile debt so curated picks complete before organic
      expansion; it yields to Tier 1's review debt because reviewer
      backlog is time-sensitive. See Priority seed file below for the
      entry schema.
   1. **Review debt** — any record with `review_state: proposed` older than
      14 days → emit one `review-records` task per distinct reviewer target
      (system, metric, or observation batch). `auto-validated` records do
      **not** trigger this tier on their own; they're considered usable
      until the webUI prune tool flags them or a separate sweep of
      auto-validated batches is scheduled.
   2. **Observation debt** — any `validated` system with zero observations
      against its declared metrics → emit one `extract-observations` task
      per (system, metric-family) pair, cap 5 per run.
   3. **Profile debt** — any `candidate` system without a completed profile
      (`boundary`, `components`, `interaction_types`, `scales` all set) →
      emit one `profile-system` task per system, cap 3 per run.
   4. **Metric debt** — any `candidate` metric without a rubric file → emit
      one `define-metrics` task per metric, cap 3 per run.
   5. **Coverage expansion** — if the top tiers are all empty, emit
      `scout-systems` tasks for the under-covered `system-domain` slugs:
      one per slug in the bottom half of the coverage histogram, capped
      at `max_scouts_per_run: 3`, each with `Budget: 2 candidate systems`
      in `notes`. Fanning across multiple domains avoids the lock-in
      where one scout's 5-candidate budget dominates several subsequent
      autoruns with a single domain before rotation can resume. If only
      one domain is under-covered, emit a single scout with `Budget: 3`.
4. For each proposal, generate a task manifest with:
   - `id` — `tsk-YYYYMMDD-NNNNNN` where the `NNNNNN` suffix is the next
     unused number for that date across all `ops/tasks/` subdirectories.
   - `state: inbox`, `priority: normal`, `lease: {ttl_minutes: 90, max_attempts: 1}`.
   - `output_targets` and `acceptance_tests` — pull the canonical shape
     from the target skill's SKILL.md. Do not fabricate acceptance tests.
   - `notes` — one sentence naming the gap this proposal fills, e.g.
     "Covers observation-debt gap: sys-000123 has zero observations against
     metric-family:dynamics."
5. Write the plan-report to
   `ops/runs/YYYY/MM/DD/<run-id>/plan-report.md` with sections:
   - **Scoreboard** — counts from step 1 as a table.
   - **Gap selected** — which tier fired and why.
   - **Proposals emitted** — list of task ids + one-line rationale.
   - **Skipped** — lower-priority tiers that had gaps but were not acted on.
6. Validate: `uv run coc validate ops/tasks/inbox/`. If any proposal fails
   validation, delete it, record the failure in the plan-report under
   **Errors**, and fall through to `status: blocked` for the run.

## Output shape

- Task manifests — valid against
  [schemas/task.schema.json](../../schemas/task.schema.json) with
  `state: inbox`.
- Plan-report — a markdown file with the four sections above. No YAML
  frontmatter; this is a free-form run artifact, not a canonical record.

## Domain rotation

Tier 0 (bootstrap) and Tier 5 (coverage expansion) both need to pick one
or more `system-domain` slugs to scout. Use this rule:

1. For each slug listed in
   [taxonomy/source/system-domains.yaml](../../taxonomy/source/system-domains.yaml),
   count matching `taxonomy_refs: [system-domain:<slug>]` entries across
   `registry/systems/*/system.yaml`. Call this the coverage histogram.
2. Select the under-covered slugs: all zero-count slugs for Tier 0, or
   the bottom half of the histogram for Tier 5 (slugs whose count is at
   or below the median). Order them ascending by count; tie-break on
   slug order (the order they appear in `system-domains.yaml`).
3. Emit one scout task per selected slug, capped at `max_scouts_per_run`
   (default 3) to stay within the auto-promote per-type cap on
   `scout-systems`. Each scout's `notes` hint names its target slug and
   the budget override, e.g. `notes: "Coverage-expansion Tier 5. Target
   system-domain:technological. Budget: 2 candidate systems."`.

This yields an *interleaved* rotation: a single plan-backlog run seeds
scouts across multiple thin domains simultaneously, so the subsequent
profile-system drain alternates between domains rather than burning
through one domain's candidates for several iterations before jumping.

## Priority seed file

[config/priority-systems.yaml](../../config/priority-systems.yaml) is a
hand-curated, ordered list of systems the maintainer wants profiled
before organic coverage expansion. It's the taste-injection point for
the catalog: edit the file to change what scouts run next.

**Entry shape** (root-level YAML list):

```yaml
- name: Human social systems        # passed to scout-systems as topic
  slug: human-social-system         # idempotency key vs. registry slug tail
  domain: social                    # resolves against taxonomy/source/system-domains.yaml
  notes: optional extra scoping context
```

**Fulfillment check** (Tier 0.5 skip logic): an entry is considered
done when any of the following holds —

- `registry/systems/sys-*--<slug>/` directory exists, or
- any `ops/tasks/**/*.yaml` has `notes` starting with
  `"Priority seed: <slug>."` (covers in-flight scout/profile tasks
  seeded from this list; prevents double-emission across runs).

Re-ordering entries reprioritizes; deleting an entry stops future
re-emission; re-adding a deleted entry after its system has been
removed from `registry/systems/` re-queues it.

**Validation**: the domain slug must resolve against
`taxonomy/source/system-domains.yaml`. Entries that fail resolution are
skipped (logged in the plan-report's **Skipped** section) rather than
blocking the run — the rest of the list should still make progress.

## Block or fail when

- `coc validate` fails on a proposal you wrote. Delete it (do not leave
  malformed YAML in `inbox/`), record the failure, block the run.
- The selected gap would require inventing a taxonomy slug. Skip to the
  next tier; do not invent.
- No tier fires *and* the inbox already holds `inbox_cap` items — exit
  `status: success` with a saturated-queue note. This is the healthy idle
  state, not a block.

## Retiring this skill

Plan-backlog is load-bearing only while the catalog is small enough that the
queue can run dry. Once the ready queue rarely reaches zero across a
sustained window (≥20 consecutive runs enter Branch A), the cost of running
this skill's scoreboard outweighs the benefit. At that point, flip `status`
to `disabled` and rely on human and `review-records` curation to keep the
queue seeded.

## References

- [AGENTS.md](../../AGENTS.md) — sensitive actions, quality bar.
- [prompts/autonomous-run.md](../../prompts/autonomous-run.md) — Branch B
  caller.
- [schemas/task.schema.json](../../schemas/task.schema.json) — manifest
  contract for every proposal emitted.
- [skills/scout-systems/SKILL.md](../scout-systems/SKILL.md),
  [skills/define-metrics/SKILL.md](../define-metrics/SKILL.md),
  [skills/profile-system/SKILL.md](../profile-system/SKILL.md),
  [skills/extract-observations/SKILL.md](../extract-observations/SKILL.md),
  [skills/review-records/SKILL.md](../review-records/SKILL.md) — sources of
  truth for `output_targets` and `acceptance_tests` when proposing.
