# Catalog of Complexity — Agent Rules

This file is the canonical operating model. Both Claude Code and OpenAI Codex
read it on every session. Tool-specific settings live in `.claude/` and
`.codex/`; the substance of how to work in this repo is here.

## Mission

Build a canonical, provenance-rich catalog of complex systems, metrics, and
observations across scientific domains, and surface cross-domain structural and
dynamical patterns.

## Architecture in one paragraph

The filesystem is the source of truth. `registry/` holds canonical entities
(systems, metrics, sources, observations) as YAML and JSONL. `taxonomy/` holds
controlled vocabularies. `schemas/` holds JSON Schema Draft 2020-12 definitions
that every canonical record must validate against. `ops/` holds operational
state for agents: a directory-based task queue, run reports, and event logs.
`warehouse/` holds derived Parquet and DuckDB that are **never hand-edited** —
always regenerable from `registry/`. `releases/` holds publishable snapshots
described by Data Package and optional RO-Crate metadata.

## Non-negotiables

- The filesystem is the source of truth.
- Never edit files under `registry/sources/*/raw/`.
- Never hand-edit anything under `warehouse/`.
- Claim exactly one task before writing.
- Only write files declared in the task manifest's `output_targets`.
- Validate every changed structured file against its schema before marking a
  task complete.
- Append a run report (`ops/runs/YYYY/MM/DD/<run-id>/run.json`) and at least
  one event entry before marking a task complete.
- If evidence is insufficient or contradictory, block the task with a clear
  reason; do not guess values.

## Quality bar

- No uncited numeric claims in canonical records (metrics, observations).
  Type-level **system** entries are exempt from per-claim citation when the
  claim is canonical knowledge (e.g. "metabolic networks contain reactions
  catalyzed by enzymes"); cite when making specific quantitative or
  contested claims.
- Every observation must include `value_kind`, `confidence`, and at least one
  `evidence_ref`.
- Every metric must declare applicability conditions.
- Every system must include `boundary`, `components`, `interaction_types`,
  and `scales`.
- Taxonomy references (`system-domain:*`, `system-class:*`, `metric-family:*`)
  must resolve against `taxonomy/source/*.yaml`.

## What counts as a system worth cataloging

The catalog holds **types of complex systems, not specific instances**.
"Cell" is a system; *E. coli* is an example of a cell. "Market" is a
system; the NYSE is an example. Entries are organized as a *periodic
table of complexity* — one entry per archetypal system kind, mostly
mirroring `taxonomy/source/system-classes.yaml` and the priority list
in `config/priority-systems.yaml`.

A candidate qualifies for a registry entry iff **all** of the following
hold:

1. **Type, not instance.** The candidate names a recurring kind, not a
   single named example. (`multicellular-organism` ✓, `Caenorhabditis
   elegans` ✗; `ecosystem` ✓, `Amazon rainforest` ✗.)
2. **Distinct organizational level.** Fits one Boulding-style level
   cleanly — atoms, molecules, reactions, cells, organisms, brains,
   minds, social organizations, economies, ecosystems, Earth system, etc.
   Conceptual blends spanning multiple levels (e.g. "Mediterranean
   diet") don't qualify; they're cross-cuts to be analyzed downstream,
   not catalog entries.
3. **Recognizable characteristic structure** — boundary, components,
   interaction types, and characteristic spatial/temporal scales that
   survive across instances. If the structure is instance-specific
   (you have to specify *which* X to describe it), it's an instance.
4. **At least 3 well-known concrete examples** that can be listed in
   `canonical_examples`. Genuinely-singular types (`the-internet`,
   `earth-system`) are exempt and noted in the entry.
5. **Cross-applicable measurability.** Admits at least one metric (graph
   modularity, characteristic timescale ratio, response-recovery time,
   etc.) that produces a value comparable to the same metric on systems
   at other organizational levels.

**Source policy under this framing.** Type-level entries (`system.yaml`)
do **not** require literature acquisition for the entry's bare existence
— "cells exist," "metabolic networks have stoichiometric matrices,"
etc. is canonical knowledge. The `source_refs` field is optional on
systems. Cite when the entry's prose makes a specific quantitative or
contested claim. Metrics (`metric.yaml`) and observations (`*.jsonl`)
**do** require sources — operationalization and measurement values must
be grounded.

**Implication for `scout-systems`.** The skill's job is to propose
*missing type-level archetypes* against the priority list and existing
taxonomy, not to surface specific case studies. Literature search is
optional, not required. See `skills/scout-systems/SKILL.md`.

## Operating loop

1. Read the task manifest (`ops/tasks/leased/<task-id>.yaml`).
2. Read the active skill (`skills/<skill>/SKILL.md`).
3. Read the schemas referenced by the task's `acceptance_tests`.
4. Read **only** the source records the task references. Avoid broad repo
   scans unless the task explicitly requires them.
5. Produce the declared outputs.
6. Run `uv run coc validate` on anything structured you wrote.
7. Append a run report and event; call `uv run coc complete <task-id>`.

## Task lifecycle

```
inbox → ready → leased → running → review → done
                    │         │
                    │         └→ blocked
                    │
                    └→ failed
```

Atomic move semantics (via `os.rename`) guarantee that two agents cannot lease
the same task. A lease carries a TTL (default 90 min). A janitor requeues
stale leases.

## Three-layer prompt stack

1. **Layer 1 — AGENTS.md (this file):** durable rules, applies every time.
2. **Layer 2 — `skills/<name>/SKILL.md`:** workflow-specific instructions,
   scripts, and references.
3. **Layer 3 — task manifest:** the concrete job, inputs, outputs, and
   acceptance tests for this single run.

Agents read all three in order before acting. The task manifest overrides
skill defaults; the skill overrides AGENTS.md silence.

## Autonomous runs — sweep model

Scheduled runs (driven by Claude Code and Codex desktop schedulers) start
from [prompts/autonomous-run.md](prompts/autonomous-run.md).

**Master switch.** [config/autorun.yaml](config/autorun.yaml) carries a
top-level `disabled` boolean. When `true`, every scheduled invocation
exits immediately on entry — no preflight, no queue work, no git
activity. Use it to pause the scheduler during large hand-curation
passes (schema rollouts, bulk bootstraps, phase-advance migrations)
without reconfiguring the desktop routine.

The sweep model: each cron tick reads the active phase from
`config/phase.yaml`, asks `coc.worklist.next_worklist_items(phase, K)`
for the next K subjects (in priority-then-domain-interleave order for
system phases, maturity-level order for the metric phase), emits one
task manifest per subject via `coc.dispatch.emit_phase_task()`, executes
them via the task envelope, runs a retrospective per iteration, commits
per iteration, and on the last iteration's commit checks
`coc.phase.phase_completion_check()` — if the phase's worklist is now
empty, the autorun flips `current` to the next phase and writes a
`phase.advance` event in a trailing commit.

`max_tasks_per_run` defaults to 1 (clamp [1, 10]) — under the sweep
model each task is a single subject and may run 30–60 minutes
wall-clock (e.g. fill-system-metrics produces 50–100 observations in
one integrated pass).

**The previous "Branch A loop / Branch B plan-backlog tier walk" model
is gone.** The 8-tier hierarchy (Tier 0 / 0.5 / 1 / 2 / 3 / 4 / 5)
moved into the worklist resolver as a single phase-driven query;
plan-backlog shrinks to (1) source-debt sweep embedded in preflight
and (2) periodic apply-retros trigger.

Retros run "every iteration" by default, **per-phase**: the "10
consecutive non-actionable → narrow cadence" rule resets at each
phase advance because system-profiling retros differ from matrix-fill
retros and we want to learn separately.

### Project phase

`config/phase.yaml::current` is one of:

- `system-profiling` — walk every `bootstrap-stub` system, P0 first
  then domain-interleave, upgrade each to status `candidate` via
  `profile-system`. Done when zero systems remain at `bootstrap-stub`.
- `metric-definition` — walk every `bootstrap-stub` metric, L2 first
  then L1 / L0 / L3+, upgrade each to status `proposed` (or
  `canonical`) via `define-metrics`. Done when zero metrics remain.
- `matrix-fill` — walk every candidate-or-profiled system and run
  `fill-system-metrics` on it (one task per system, all applicable
  metrics in one integrated pass). Open-ended; advanced manually to
  `analysis` when matrix density justifies cross-system analysis.
- `analysis` — `analyze-archetypes` / clustering / hypothesis
  generation. Human-promoted only; not auto-dispatched.

Auto-advance triggers and side-channel caps are documented in
`config/phase.yaml`. Helper functions live in `coc.phase` —
`current_phase()`, `phase_to_task_type()`, `side_channel_cap()`,
`phase_completion_check()`, `advance_phase()`.

### Autonomy policy (what promotes without human review)

`uv run coc advance` auto-promotes these task types from `inbox/` to
`ready/` (default per-type cap 3, `review-records` overridden to 1):
`scout-systems`, `profile-system`, `define-metrics`,
`extract-observations`, `review-records`, `apply-retros`,
`analyze-archetypes`, `acquire-source`. The tighter `review-records` cap keeps the
retro → cluster → review self-improvement loop from starving
catalog-growth types of promotion slots.

The following types stay in `inbox/` until a human promotes them:
`materialize-warehouse` and `build-release`. These publish artifacts
(`warehouse/`, `releases/`) that a webUI prune can't easily retract.
Everything else — including `review-records` tasks that edit `taxonomy/`
or `schemas/` — auto-promotes. The webUI prune workflow and
`coc validate` together cover the post-hoc correctness story: a bad
taxonomy slug or schema change surfaces as validation failures on
dependent records, and the prune tool can roll edits back.

Records produced by agents default to `review_state: auto-validated`
(observations) — usable downstream immediately. A human or a
`review-records` pass promotes them to `validated`. The planned webUI
exploration/prune tool is the post-hoc review mechanism. Use
`review_state: proposed` only when the authoring agent wants human eyes
before the record is counted as usable.

Task terminal state defaults to `done`. Use `review` only for explicit
escalations.

## Skill roster

- `setup-repo` — bootstrap or repair repository scaffolding.
- `scout-systems` — discover candidate systems and candidate metrics.
- `define-metrics` — curate metric definitions, rubrics, applicability rules.
- `profile-system` — define a system's boundary, components, scales, taxonomy.
- `extract-observations` — fill a single (system, metric) cell or small
  batch with evidence and confidence. Used for one-off / manual curation;
  the matrix-fill phase uses `fill-system-metrics` instead.
- `fill-system-metrics` — primary task type for the `matrix-fill` phase.
  One task per system; walks the metric registry, classifies each
  metric as extracted / skipped_undefined / blocked_source_not_acquired,
  appends 50–100 observations across many metric-family files in one
  git commit. Does NOT block the whole task on missing sources; emits
  acquire-source tasks and continues.
- `review-records` — schema, provenance, citation, methodological checks.
- `materialize-warehouse` — rebuild Parquet, DuckDB, release snapshots.
- `analyze-archetypes` — clustering, graph building, hypothesis generation
  (scaffolded; enabled once registry breadth warrants it).
- `apply-retros` — consume unprocessed retrospectives, cluster
  `proposed_improvements` by target, and emit one `review-records` task per
  cluster. Queue-driven; closes the retrospective feedback loop.
- `acquire-source` — fetch one prefixed source reference (`doi:`, `arxiv:`,
  `url:`) and register it under `registry/sources/src-NNNNNN--<slug>/` with
  immutable raw artifacts and a validated source.yaml. The only skill that
  writes to `registry/sources/*/raw/`. plan-backlog Tier 0.75 feeds it.
- `retrospective` *(status: postrun)* — post-task assessment invoked by
  `prompts/autonomous-run.md` after every task, not queue-driven.
- `plan-backlog` *(status: postrun)* — under the sweep model, two narrow
  responsibilities only: (1) source-debt sweep embedded in every cron
  tick's preflight; (2) periodic apply-retros trigger fired every K
  retros. The legacy 8-tier hierarchy moved to `coc.worklist` +
  `coc.dispatch`; no `plan-backlog` task type exists.

Each skill directory is self-contained. Read `skills/<name>/SKILL.md` before
starting work of that type.

## Tools available to you

Use native file-editing and shell tools. For repo-aware operations prefer the
`coc` CLI:

- `uv run coc validate [path]` — validate structured files against schemas.
- `uv run coc advance` — sweep blocked/ for satisfied `unblock` conditions, then auto-promote eligible inbox tasks to ready (per-type cap applies).
- `uv run coc unblock [<task-id>]` — move one blocked task back to ready (explicit), or sweep all satisfied `unblock` conditions when no id is given.
- `uv run coc next [--lane <lane>]` — print the highest-priority ready task id.
- `uv run coc requeue` — reap stale leases (watchdog).
- `uv run coc lease <task-id>` — claim a task (ready → leased).
- `uv run coc heartbeat <task-id>` — keep your lease alive.
- `uv run coc complete <task-id> --outputs <json> [--state review|done|blocked|failed] [--unblock-on-taxonomy <qualified-slug> | --unblock-on-task <tsk-id>]` — the `--unblock-on-*` flags apply only with `--state blocked` and record the auto-unblock condition that `coc advance` checks on subsequent runs.
- `uv run coc materialize` — rebuild the warehouse from the registry.
- `uv run coc release` — build a release snapshot.
- `uv run coc export-taxonomy` — regenerate SKOS exports.
- `uv run coc eval [skill]` — run QC evals.
- `uv run coc acquire <ref>` — resolve a prefixed source ref (`doi:`,
  `arxiv:`, `url:`) and register it under `registry/sources/`.

## Sensitive actions (require explicit approval)

- Deleting accepted records under `registry/`.
- Overwriting canonical metric definitions.
- Modifying anything under `registry/sources/*/raw/`.
- Publishing to `releases/`.
- Bulk modifications spanning multiple systems.
- Pushing to `git remote` or opening a PR.

When in doubt: write the change as a task manifest, leave it in
`ops/tasks/review/`, and let a reviewer run it.

## Domain knowledge pointers

- Boulding's Hierarchy of Systems Complexity informs `taxonomy/source/system-classes.yaml`.
- Metric families (boundary-scale, composition, topology, dynamics,
  information, feedback-adaptation, throughput, resilience) are documented in
  `taxonomy/source/metric-families.yaml`.
- Evidence types (`direct`, `derived`, `proxy`, `simulation`, `expert_estimate`)
  are documented in `taxonomy/source/evidence-types.yaml`.

## Common mistakes to avoid

- Do not invent taxonomy slugs. If a domain/class/family doesn't exist,
  propose it in a task manifest to `taxonomy/source/` rather than using an
  ad-hoc string.
- Do not put free-form prose inside canonical records. `notes.md` and
  `rubric.md` are the appropriate places for discursive content; YAML and
  JSONL fields are for structured data only.
- Do not recompute or mutate records in `registry/observations/*.jsonl`
  in-place; append new observations with fresh IDs and mark older records
  superseded via `review_state`.
