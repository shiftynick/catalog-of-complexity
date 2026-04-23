---
name: setup-repo
description: Bootstrap or repair the repository scaffolding according to BOOTSTRAP_PLAN.md. Use this skill when the task manifest declares a `bootstrap` type, or when a structural gap (missing schemas, missing taxonomy, broken warehouse) needs a full rebuild pass.
status: active
inputs:
  - 'target_phase — integer 0-12 or "all". Which phase of BOOTSTRAP_PLAN.md to execute.'
  - 'dry_run — boolean. If true, report the diff without writing.'
outputs:
  - 'Files and directories enumerated under the target phase in BOOTSTRAP_PLAN.md.'
  - 'One commit per completed phase (message `phase N: <name>`).'
  - 'Event log entry per phase gate (kind `task.complete` with payload.phase=N).'
stop_conditions:
  - 'The phase gate listed in BOOTSTRAP_PLAN.md §4 passes.'
  - 'Any open decision (§5) is unresolved — block the task with the decision text.'
  - 'A pre-existing file conflicts with the plan and editing it is not listed in `output_targets` — block.'
---

## When to use

This skill owns the repository's structural invariants. Invoke it to:

- Bring a fresh clone to a specified phase of [BOOTSTRAP_PLAN.md](../../BOOTSTRAP_PLAN.md).
- Repair a phase whose gate has regressed (e.g. `coc validate` fails, warehouse can't materialize).
- Add a new file type mandated by a future phase without disturbing earlier phases.

Do **not** use this skill for adding registry records — those belong to `scout-systems`, `profile-system`, `define-metrics`, or `extract-observations`.

## Preconditions

- Task manifest specifies `target_phase` in `notes` or `output_targets` paths imply a phase.
- [BOOTSTRAP_PLAN.md](../../BOOTSTRAP_PLAN.md) is present and has not been hand-edited for this task (the plan is the spec, not an output).
- `uv sync` has run at least once in this checkout.

## Procedure

1. Read [BOOTSTRAP_PLAN.md](../../BOOTSTRAP_PLAN.md) §4 for the target phase. Note the enumerated files, the gate, and any cross-phase dependencies.
2. Enumerate existing state: `git status`, `ls` the directories the phase creates. Identify which items are already present versus missing.
3. For each missing item, write the file as specified. Prefer the exact shape given in the plan; deviations require a new task manifest or a plan amendment, not an inline decision.
4. Run the phase gate commands verbatim from §4 (e.g. Phase 5 = `coc lease` → `coc heartbeat` → `coc complete` with three event log entries).
5. Append a run report summarising: phase number, files created/modified, gate output, and any deviations.
6. Call `uv run coc complete <task-id> --state done --outputs <json>`.

## Output shape

- New or updated files listed in the phase checklist. No other files should appear in `git status`.
- A `run.json` under `ops/runs/YYYY/MM/DD/<run-id>/` with `phase`, `gate_passed`, and `deviations[]`.
- Event log: one `task.complete` event per phase with `payload.phase` set.

## Block or fail when

- An open decision in §5 is not already resolved in `AGENTS.md` or a prior committed plan — block with the decision text.
- Running the gate command surfaces an error that cannot be fixed inside the phase's scope (would require touching a later phase).
- The plan references a tool or dep that is missing from `pyproject.toml` — block and propose a plan amendment task.

## References

- [BOOTSTRAP_PLAN.md](../../BOOTSTRAP_PLAN.md) — canonical phase spec.
- [AGENTS.md](../../AGENTS.md) — non-negotiables that hold across all phases.
