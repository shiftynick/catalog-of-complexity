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

- No uncited numeric claims in canonical records.
- Every observation must include `value_kind`, `confidence`, and at least one
  `evidence_ref`.
- Every metric must declare applicability conditions.
- Every system must include `boundary`, `components`, `interaction_types`,
  and `scales`.
- Taxonomy references (`system-domain:*`, `system-class:*`, `metric-family:*`)
  must resolve against `taxonomy/source/*.yaml`.

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

## Autonomous runs

Scheduled runs (driven by Claude Code and Codex desktop schedulers) start
from [prompts/autonomous-run.md](prompts/autonomous-run.md). That prompt
selects exactly one task via `coc next`, delegates execution to
`prompts/task-envelope.md`, and then invokes the `retrospective` skill. One
run = one task + one retro, then a local commit with `[auto]` suffix. Pushes
remain human-driven — see "Sensitive actions".

Retro cadence is "every run" by default and narrows to
`blocked`/`failed`-only once ≥10 consecutive retros report
`actionable: false`. The transition is itself a reviewable change.

### Autonomy policy (what promotes without human review)

`uv run coc advance` auto-promotes these task types from `inbox/` to
`ready/` (per-type cap 3): `scout-systems`, `profile-system`,
`define-metrics`, `extract-observations`, `review-records`, `apply-retros`,
`analyze-archetypes`.

The following types stay in `inbox/` until a human promotes them:
`materialize-warehouse`, `build-release`, and anything authored under
`taxonomy/` or `schemas/`. These affect published artifacts or controlled
vocabularies that a webUI prune can't easily undo.

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
- `extract-observations` — fill system–metric values with evidence and confidence.
- `review-records` — schema, provenance, citation, methodological checks.
- `materialize-warehouse` — rebuild Parquet, DuckDB, release snapshots.
- `analyze-archetypes` — clustering, graph building, hypothesis generation
  (scaffolded; enabled once registry breadth warrants it).
- `apply-retros` — consume unprocessed retrospectives, cluster
  `proposed_improvements` by target, and emit one `review-records` task per
  cluster. Queue-driven; closes the retrospective feedback loop.
- `retrospective` *(status: postrun)* — post-task assessment invoked by
  `prompts/autonomous-run.md` after every task, not queue-driven.
- `plan-backlog` *(status: postrun)* — empty-queue branch of the autonomous
  run; inspects registry coverage and proposes new inbox manifests.

Each skill directory is self-contained. Read `skills/<name>/SKILL.md` before
starting work of that type.

## Tools available to you

Use native file-editing and shell tools. For repo-aware operations prefer the
`coc` CLI:

- `uv run coc validate [path]` — validate structured files against schemas.
- `uv run coc advance` — auto-promote eligible inbox tasks to ready (per-type cap applies).
- `uv run coc next [--lane <lane>]` — print the highest-priority ready task id.
- `uv run coc requeue` — reap stale leases (watchdog).
- `uv run coc lease <task-id>` — claim a task (ready → leased).
- `uv run coc heartbeat <task-id>` — keep your lease alive.
- `uv run coc complete <task-id> --outputs <json> [--state review|done|blocked|failed]`.
- `uv run coc materialize` — rebuild the warehouse from the registry.
- `uv run coc release` — build a release snapshot.
- `uv run coc export-taxonomy` — regenerate SKOS exports.
- `uv run coc eval [skill]` — run QC evals.

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
