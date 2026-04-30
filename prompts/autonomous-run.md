# Autonomous Run — Sweep Model

This is the master prompt fired on a schedule by Claude Code and OpenAI Codex.
It walks a known finite worklist subject-by-subject under the active project
phase, emitting one (or a few) tasks per cron tick, executing them through
the task envelope, and auto-advancing the phase when each phase's worklist
drains to zero.

The previous "Branch A loop / Branch B plan-backlog" model is gone.
Replaced by:

  1. Master switch + preflight (unchanged)
  2. **Worklist resolver** — read active phase, ask
     `coc.worklist.next_worklist_items(phase, k)`, emit task manifests
     via `coc.dispatch.emit_phase_task()`, promote to ready/
  3. Branch A loop — lease, execute via task envelope, complete, retro,
     commit (per-task semantics unchanged)
  4. **Phase completion check** — after the last commit, ask
     `coc.phase.phase_completion_check()`; if a next phase exists,
     `advance_phase()` and append a `phase.advance` event in the same
     commit

`max_tasks_per_run` is read from `config/autorun.yaml` (default 1 under
the sweep model — each task is a single subject with potentially many
sub-units inside it; e.g. fill-system-metrics emits 50–100 observations
per task).

---

## Contract

You are beginning a scheduled autonomous run. You must:

0. **Master switch.** Read [config/autorun.yaml](../config/autorun.yaml).
   If `disabled: true` is set, exit immediately with no side effects:
   write a single event of kind `run.skipped` with reason
   `autorun_disabled` and stop. Do **not** validate, advance the queue,
   touch git, or call any skill. The flag exists so curators running
   large hand-edits (schema rollouts, bulk bootstraps, phase-advance
   migrations) can pause the scheduler without reconfiguring it.
1. Read and obey [AGENTS.md](../AGENTS.md). Its "Non-negotiables", "Quality
   bar", and "Sensitive actions" sections govern everything below.
2. Run preflight (§Preflight) **once**. Then resolve `max_tasks_per_run`
   by reading [config/autorun.yaml](../config/autorun.yaml) (default 1,
   clamp [1, 10]). `$COC_max_tasks_per_run` overrides the config file
   when set.
3. Run the **Worklist resolver** (§Worklist). It reads the active phase
   from `config/phase.yaml`, asks the resolver for the next K subjects,
   and emits one task manifest per subject into `ops/tasks/inbox/`.
   Promote them to `ready/` (call `coc advance` again or move directly).
4. Execute up to `max_tasks_per_run` Branch-A iterations (§Branches).
   Each iteration is one task: lease → execute via task envelope →
   write `run.json` → retrospective → commit. Move to the next
   iteration only if the previous one ended cleanly *and* the queue
   still has work *and* the per-invocation budget hasn't been
   exceeded (§Budget).
5. Each iteration's retrospective runs for every terminal state
   (`done`, `review`, `blocked`, `failed`) until the cadence policy
   says otherwise (§Retrospective).
6. After the last iteration's commit, run the **Phase completion check**
   (§Phase advance). If a next phase exists, flip
   `config/phase.yaml::current` to it, append a `phase.advance` event,
   and amend that into a single trailing commit on the run.
7. Commit your changes locally only (`git commit`) **per iteration**
   plus optionally one trailing commit for phase advance. Do not push,
   open PRs, or modify remotes. A human handles promotion.
8. Stop when §Stop conditions apply. Do not ask clarifying questions
   during the run — an underspecified task resolves to `status: blocked`
   for that iteration only; the next iteration may still proceed.

---

## Preflight

Before the worklist resolver fires, confirm environment health and groom
the queue:

- `uv run coc validate` exits 0 on the repo as-is. If it already fails,
  abort this run, write an event of kind `run.aborted` with the failure
  summary, and do not touch the queue.
- `git status --porcelain` is clean. If there are uncommitted changes
  from a previous run, abort with `run.aborted` and note the dirty
  state — a human must resolve before another autonomous run is safe.
- `uv run coc advance` — first sweep `blocked/` for any task whose
  `unblock` condition is now satisfied (`taxonomy-slug-exists` —
  qualified slug resolves; `task-complete` — the named task is in
  `done/`; `sources-resolved` — every entry in `source_refs` resolves
  to a registered `src-*`). Satisfied tasks are moved
  `blocked/` → `ready/` with `lease.attempts` reset to 0 and a
  `task.unblock` event appended. Then auto-promote any eligible
  `inbox/` tasks to `ready/` (per-type cap from
  `coc advance`'s constants).
- **Tier-0.75 source-debt sweep** — execute the source-debt portion of
  [skills/plan-backlog/SKILL.md](../skills/plan-backlog/SKILL.md): scan
  `ops/tasks/{inbox,ready,leased,running,blocked}/` for prefixed
  `source_refs` with no matching `registry/sources/src-*/source.yaml`,
  emit up to N `acquire-source` tasks into `ops/tasks/inbox/` (where
  N is `coc.phase.side_channel_cap("acquire-source")` for the active
  phase — 3 for system-profiling/metric-definition, 10 for
  matrix-fill). Skip the sweep when `len(ops/tasks/inbox/) >= 20`.

Preflight runs **once per invocation**, before the worklist resolver.

Record preflight outputs in the **first iteration's** run report
`notes`: validate result, git cleanliness, list of promoted task ids,
and the list of acquire-source task ids emitted (or `none`).
Subsequent iterations note `"preflight inherited from invocation start"`.

---

## Worklist resolver

After preflight (and before the first Branch A iteration), emit fresh
task manifests for the active phase:

1. Read `config/phase.yaml::current`.
2. Get the primary task type:
   `coc.phase.phase_to_task_type(phase)`. If `None` (e.g. `analysis`
   phase), skip dispatch — the resolver does not auto-seed analysis
   tasks; humans promote those.
3. Compute K = `max_tasks_per_run`.
4. Query `coc.worklist.next_worklist_items(phase, K)` — returns a list
   of subject ids in priority-then-domain-interleave (system phases) or
   maturity-level (metric phase) order. May return fewer than K if the
   worklist is shallower than K (or already drained).
5. For each subject id, call
   `coc.dispatch.emit_phase_task(phase, subject_id)`. The dispatcher
   is **idempotent on (skill, subject)** — if a task is already in flight
   for the same subject, it returns the existing task id instead of
   emitting a duplicate. Newly-emitted manifests land in `ops/tasks/inbox/`
   with `state: inbox`.
6. After all K dispatches, run `uv run coc advance` once more to
   promote the new manifests inbox → ready. Their per-type cap is
   effectively unlimited under the sweep model (the active phase's
   primary type drives the work; cap throttling applies only to side
   channels via `side_channels:` in `config/phase.yaml`).

Record in the first iteration's run report `notes`:
- Active phase
- Primary task type
- K subjects requested
- N tasks emitted (M idempotent skips)
- Worklist size remaining after dispatch

---

## Branches

### Branch A — Per-task iteration

Repeat the steps below until `max_tasks_per_run` is hit, or the queue
empties (in which case the invocation exits — there is no Branch B
under the sweep model), or a §Stop condition fires.

1. `uv run coc next` — prints the highest-priority ready task id, or
   exits 1 if the queue is empty. If exit 1: exit the invocation
   cleanly. (Empty queue post-resolver means worklist is fully drained
   for this phase; phase advance will be triggered in step 7.)
2. `uv run coc lease <task-id>` — claim it. Atomic move. If the lease
   fails, another agent got there first. Re-run `coc next` once; if
   still contended, abort **this iteration** with `run.aborted` and
   exit the invocation (do not start a new iteration on a contended
   queue).
3. Read [prompts/task-envelope.md](./task-envelope.md). Fill its
   placeholders from the leased task manifest and execute the
   envelope's procedure exactly as written. The envelope handles
   writing the task's outputs, `run.json`, and the terminal
   `coc complete` call.
4. Heartbeat at least once per `lease.ttl_minutes / 3` of wall-clock
   work.
5. On `coc complete`, capture the terminal state for use in the
   retrospective.
6. Proceed to §Retrospective for this iteration. Then commit (§Local
   commit) for this iteration.
7. After commit succeeds: increment iteration count. If iteration
   count < `max_tasks_per_run` and the queue has more ready tasks
   and no §Stop condition fires, return to step 1. Otherwise proceed
   to §Phase advance.

### (No Branch B)

Under the sweep model the worklist resolver runs in preflight and
seeds enough work for the iteration count, so the queue is never empty
at the start of Branch A unless the active phase is fully drained.
When the queue *is* empty post-resolver, the worklist size is zero
and §Phase advance fires.

The legacy plan-backlog skill's tier hierarchy is gone. plan-backlog
remains only for the source-debt sweep (Tier-0.75) embedded in
preflight, and as a periodic apply-retros trigger (see
[skills/plan-backlog/SKILL.md](../skills/plan-backlog/SKILL.md)).

---

## Phase advance

After the last Branch A iteration's commit, check whether the active
phase is now complete:

1. Call `coc.phase.phase_completion_check()`. Returns
   `(next_phase, reason)`:
   - `(None, ...)` — phase not yet complete, or auto-advance disabled,
     or phase is terminal. Exit invocation cleanly; no extra commit.
   - `(<next>, <why>)` — next phase exists and the completion
     predicate is satisfied (e.g. zero systems remain at
     bootstrap-stub).
2. If a next phase is returned:
   a. `coc.phase.advance_phase(next_phase)` — rewrites
      `config/phase.yaml::current`.
   b. Append a `phase.advance` event to `ops/events/run-events.jsonl`
      with payload `{"from": <prev>, "to": <next>, "reason": <why>}`.
   c. Stage `config/phase.yaml` and the appended event line.
   d. Commit with message
      `phase: advance <prev> → <next> (<reason>) [auto]`.
3. Exit the invocation. The next cron tick will pick up the new
   phase in preflight.

---

## Retrospective

After each iteration finishes, run the `retrospective` skill. Read
[skills/retrospective/SKILL.md](../skills/retrospective/SKILL.md) — it
is the authoritative procedure. Inputs:

- `task_id` — the task just completed.
- `run_id` — the run id you used in `run.json`.
- `skill` — the skill that was exercised.
- `outcome` — the terminal state returned by `coc complete`.

The retro writes one file to `ops/retrospectives/YYYY/MM/DD/retro-<ulid>.md`
and validates against `schemas/retrospective.schema.json`. It also
appends a `run.end` event referencing the retro's path.

### Retro cadence (per phase)

Default cadence: **every iteration** until retros stop producing
actionable improvements. Retros are tracked **per active phase** —
the "10 consecutive non-actionable → narrow cadence" rule resets when
the phase advances, since system-profiling retros differ from
matrix-fill retros and we want to learn separately.

After 10 consecutive `actionable: false` retros within the same phase,
narrow the cadence to `blocked`/`failed` outcomes only for that phase.
The transition is itself a reviewable change: record it as a
`review-records` task with a concrete edit to the skill's frontmatter.

---

## Local commit

When all artifacts for **the current iteration** are written and
validated:

1. `uv run coc validate` — must exit 0.
2. `git add` only the paths you actually wrote in this iteration. Never
   `git add -A` or `git add .`. The list is: task manifests moved by
   `coc lease/complete`, the run report, any registry edits the
   envelope produced, the retro file, and any new inbox manifests
   from a proposal.
3. `git commit -m "<task-type>(<task-id>): <terse summary> [auto]"` —
   the `[auto]` suffix marks the commit as agent-produced. **One
   commit per iteration**, plus optionally one trailing
   `phase: advance ...` commit per invocation.
4. Do not push. Do not force. Do not amend.

If the commit fails (pre-commit hook, signing, etc.), do not bypass.
Capture the failure in the iteration's retro `blockers` list, leave
the working tree as-is for human resolution, **and exit the invocation**
without starting a new iteration.

---

## Stop conditions

### Iteration-level (current iteration ends; loop may continue)

- The task's `coc complete` has returned a terminal state and the
  retrospective is written. Commit, then proceed to the next iteration.
- A "Block or fail when" clause in the active skill applies. Use
  `status: blocked` in `run.json` and still run the retrospective —
  blocks are exactly the iterations where retros are most valuable.
  Then commit and proceed.

Underspecified task manifests resolve to `blocked`, not to clarifying
questions.

### Invocation-level (whole invocation ends, no further iterations)

- Iteration count has reached `max_tasks_per_run`. Run §Phase advance,
  then exit cleanly.
- The per-invocation soft budget has been exceeded (§Budget). Finish
  the current iteration's commit, run §Phase advance, then exit.
- `coc next` returned exit 1 *after* the worklist resolver ran. Run
  §Phase advance, exit cleanly.
- Preflight failed. Write the abort event, do not touch the queue.
- A non-negotiable from AGENTS.md would be violated by the next action.
- The lease could not be reclaimed after one retry (contention). Write
  the abort event and exit. Do not start a new iteration.
- The current iteration's commit failed. Leave the dirty tree for
  human resolution and exit (per §Local commit).

---

## Budget and heartbeats

Two budgets: **per-iteration** and **per-invocation**.

**Per-iteration soft budget**: read from
`config/autorun.yaml::budgets.<phase>.soft_minutes`. Defaults: 30 for
system-profiling and metric-definition, 60 for matrix-fill. If a
single iteration crosses this, finish the current step, set
`status: blocked` with `budget_exceeded` in `notes`, run the
retrospective, commit, and exit the invocation.

**Per-invocation soft budget**: `max_tasks_per_run × 90` minutes
wall-clock total. Default 90 minutes for one iteration. If exceeded,
finish the current iteration's commit and exit, even if the iteration
count is below `max_tasks_per_run`.

Record both in `run.json`:

```json
{
  "heartbeats": 2,
  "budget": {
    "minutes_allotted": 60,
    "minutes_elapsed": 41.4,
    "exceeded": false
  }
}
```

When `exceeded: true`, add a short `reason` string. Populate
`heartbeats` from the number of `task.heartbeat` events appended.

### Watchdog contract

A separate scheduler periodically invokes `uv run coc requeue`. It
moves any task in `leased/` whose `lease.last_heartbeat` is older
than `lease.ttl_minutes` back to `ready/` (or to `failed/` once
`attempts >= max_attempts`). To avoid being reaped mid-run, heartbeat
at least once every `ttl_minutes / 3` wall-clock minutes.

---

## References

- [AGENTS.md](../AGENTS.md) — operating model and non-negotiables.
- [config/phase.yaml](../config/phase.yaml) — active phase + auto-advance
  triggers + side-channel caps.
- [config/autorun.yaml](../config/autorun.yaml) — master switch +
  per-phase budgets + max_tasks_per_run.
- [src/coc/phase.py](../src/coc/phase.py) — phase state machinery.
- [src/coc/worklist.py](../src/coc/worklist.py) — subject resolver.
- [src/coc/dispatch.py](../src/coc/dispatch.py) — task-manifest
  emitter per phase.
- [prompts/task-envelope.md](./task-envelope.md) — inner per-task
  contract.
- [skills/retrospective/SKILL.md](../skills/retrospective/SKILL.md) —
  post-iteration assessment procedure.
- [skills/plan-backlog/SKILL.md](../skills/plan-backlog/SKILL.md) —
  source-debt sweep (preflight) + apply-retros trigger.
- [schemas/run.schema.json](../schemas/run.schema.json) — run report
  shape.
- [schemas/retrospective.schema.json](../schemas/retrospective.schema.json)
  — retro frontmatter shape.
