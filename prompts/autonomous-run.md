# Autonomous Run

This is the master prompt fired on a schedule by Claude Code and OpenAI Codex.
It is the **outer** prompt — it selects tasks, delegates execution via the
task envelope, and runs a retrospective after each task.

A single invocation of this prompt may execute up to
**`max_tasks_per_run`** consecutive Branch-A iterations. Read the value
from [config/autorun.yaml](../config/autorun.yaml) at the start of the
invocation:

```bash
uv run python -c "import yaml; from pathlib import Path; p = Path('config/autorun.yaml'); cfg = yaml.safe_load(p.read_text(encoding='utf-8')) if p.exists() else {}; n = int(cfg.get('max_tasks_per_run', 5) or 5); print(max(1, min(10, n)))"
```

Default 5 if the file is missing or the field is absent; clamp to
[1, 10]. The `COC_max_tasks_per_run` environment variable, if set,
takes precedence over the config-file value (useful for ad-hoc dev
runs); in scheduled production routines (Claude Desktop / Codex
desktop scheduler) the env var is unavailable and the config file is
the only knob.

The motivation for batching is amortization of fixed context-loading
cost: AGENTS.md, the active skill SKILL.md, schemas, and taxonomy are
loaded once into the agent's working context and reused across
iterations within the same invocation, so per-task token cost drops
sharply after the first.

Each iteration is a **complete unit**: lease one task, execute it via the
task envelope, write `run.json`, run the retrospective, and commit
locally. Iterations are sequential, not parallel — parallelism across
*invocations* is still fine; parallelism *within* an iteration is still
not. The only thing that changes versus the single-task model is that the
outer loop continues to the next iteration when one finishes cleanly,
rather than exiting.

---

## Contract

You are beginning a scheduled autonomous run. You must:

1. Read and obey [AGENTS.md](../AGENTS.md). Its "Non-negotiables", "Quality
   bar", and "Sensitive actions" sections govern everything below.
2. Run preflight (§Preflight) **once**. Then resolve `max_tasks_per_run`
   by reading [config/autorun.yaml](../config/autorun.yaml) (default 5,
   clamp [1, 10]). `$COC_max_tasks_per_run` overrides the config file
   when set.
3. Execute up to `max_tasks_per_run` Branch-A iterations (§Branches). Each
   iteration is one task: lease → execute via task envelope → write
   `run.json` → retrospective → commit. Move to the next iteration only
   if the previous one ended cleanly *and* the queue still has work *and*
   the per-invocation budget hasn't been exceeded (§Budget). The first
   iteration that hits an empty `coc next` triggers Branch B (at most
   once per invocation), after which the invocation exits.
4. Each iteration's retrospective runs for every terminal state
   (`done`, `review`, `blocked`, `failed`) until the cadence policy says
   otherwise.
5. Commit your changes locally only (`git commit`) **per iteration**. Do
   not push, open PRs, or modify remotes. A human handles promotion.
6. Stop when §Stop conditions apply. Do not ask clarifying questions
   during the run — an underspecified task resolves to `status: blocked`
   for that iteration only; the next iteration may still proceed.

---

## Preflight

Before picking a branch, confirm environment health and advance the queue:

- `uv run coc validate` exits 0 on the repo as-is. If it already fails, abort
  this run, write an event of kind `run.aborted` with the failure summary,
  and do not touch the queue.
- `git status --porcelain` is clean. If there are uncommitted changes from a
  previous run, abort with `run.aborted` and note the dirty state — a human
  must resolve before another autonomous run is safe.
- `uv run coc advance` — first sweep `blocked/` for any task whose
  `unblock` condition is now satisfied (`taxonomy-slug-exists` — the
  named qualified slug resolves in `taxonomy/source/*.yaml`;
  `task-complete` — the named task is in `done/`). Satisfied tasks are
  moved `blocked/` → `ready/` with `lease.attempts` reset to 0 and a
  `task.unblock` event appended. Then auto-promote any eligible `inbox/`
  tasks to `ready/`. Eligible types: `scout-systems`, `profile-system`,
  `define-metrics`, `extract-observations`, `review-records`,
  `apply-retros`, `analyze-archetypes`, `acquire-source`. The command
  enforces a per-type cap
  (3 of any one type in `ready/`, with `review-records` tightened to 1
  so the self-improvement loop can't starve catalog-growth types) so
  runaway seeding is bounded. Types
  that stay in `inbox/` awaiting human review: `materialize-warehouse`
  and `build-release` — these publish artifacts (`warehouse/`,
  `releases/`) a webUI prune can't easily retract. Everything else —
  including `review-records` tasks that edit `taxonomy/` or `schemas/` —
  auto-promotes. The autonomous policy treats the webUI prune workflow
  plus `coc validate` as the post-hoc review mechanism.
- **Tier-0.75 source-debt sweep** — execute only the Tier 0.75
  procedure of [skills/plan-backlog/SKILL.md](../skills/plan-backlog/SKILL.md):
  scan `ops/tasks/{inbox,ready,leased,running,blocked}/` for prefixed
  `source_refs` (`doi:`, `arxiv:`, `url:`, `isbn:`) with no matching
  `registry/sources/src-*/source.yaml`, emit up to 3 `acquire-source`
  tasks into `ops/tasks/inbox/` per the skill's idempotency rule
  (`"Source debt: <ref>."` note prefix) and `unblock` wiring for
  blocked tasks, then `uv run coc validate ops/tasks/inbox/`. Skip the
  pass when `len(ops/tasks/inbox/) >= 20` (the skill's default
  `inbox_cap`). Do not write the skill's per-pass `plan-report` —
  this run's report carries the summary. A validation failure here
  aborts the run with `run.aborted` (per the validate-failure rule
  above); no lease is taken. Running this in preflight (rather than
  only in Branch B) keeps source-debt remediation cadence independent
  of queue depth, so blocked profile-system / extract-observations
  tasks are not stranded while Branch A drains other ready work.

Preflight runs **once per invocation**, before any iteration begins. It
is not re-run between iterations — `coc validate`/`git status` cleanliness
between iterations is enforced by each iteration's own commit step, and
`coc advance`/Tier-0.75 sweep at the start of every invocation is
sufficient to keep the queue groomed across iterations within the same
invocation (subsequent iterations consume the freshly-promoted ready/
queue without re-running advance).

Record all four preflight steps' outputs in the **first iteration's**
run report `notes`: the `coc validate` result, the `git status`
cleanliness, the list of promoted task ids from `coc advance`, and the
list of acquire-source task ids emitted by the Tier-0.75 sweep (or
`none`). Subsequent iterations' run reports note `"preflight inherited
from invocation start"` rather than repeating the four checks.

---

## Branches

### Branch A — Per-task iteration (queue non-empty)

Repeat the steps below until `max_tasks_per_run` is hit, or the queue
empties (in which case Branch B fires once and the invocation exits),
or a §Stop condition fires.

1. `uv run coc next` — prints the highest-priority ready task id, or
   exits 1 if the queue is empty. If exit 1: if no Branch-A iteration
   has run in this invocation, fall through to Branch B; otherwise
   (already produced ≥1 iteration's worth of work) exit cleanly.
2. `uv run coc lease <task-id>` — claim it. Atomic move, no retry on
   contention; if the lease fails, another agent got there first. Re-run
   `coc next` once; if still contended, abort **this iteration** with
   `run.aborted` and exit the invocation (do not start a new iteration
   on a contended queue).
3. Read [prompts/task-envelope.md](./task-envelope.md). Fill its
   placeholders from the leased task manifest and execute the envelope's
   procedure exactly as written. The envelope handles writing the task's
   outputs, `run.json`, and the terminal `coc complete` call.
4. Heartbeat at least once per `lease.ttl_minutes / 3` of wall-clock
   work (so every 30 minutes at the default 90-min TTL):
   `uv run coc heartbeat <task-id>`. Iterations that finish inside one
   cadence window may legitimately emit zero heartbeats — `heartbeats:
   0` in `run.json` is expected for sub-cadence iterations, not an
   anomaly.
5. On `coc complete`, capture the terminal state for use in the
   retrospective.
6. Proceed to §Retrospective for this iteration. Then commit (§Local
   commit) for this iteration.
7. After commit succeeds: increment iteration count. If iteration count
   < `max_tasks_per_run` and no §Stop condition fires, return to step 1.
   Otherwise exit the invocation.

### Branch B — Empty queue (one-shot per invocation)

The queue has no ready tasks. Run this branch at most **once per
invocation**, regardless of how many Branch-A iterations preceded it.

1. Invoke the `plan-backlog` skill directly (no queue manifest — it is a
   meta-skill, same status class as `retrospective`). Read
   [skills/plan-backlog/SKILL.md](../skills/plan-backlog/SKILL.md).
2. Its outputs: zero or more new task manifests written to
   `ops/tasks/inbox/`. Promotion to `ready/` is not part of this branch —
   the **next invocation's** preflight `coc advance` step picks up
   auto-eligible manifests. (The current invocation does not loop back
   to Branch A even if plan-backlog produced eligible manifests; that
   would re-cross the preflight that already ran.) Types outside
   `AUTO_PROMOTE_TYPES` (e.g. `materialize-warehouse`, `build-release`)
   stay in `inbox/` until a human promotes them.
3. Write a `run.json` with `task_id: null` (Branch B has no owning task),
   `status: success`, and `outputs` listing any new manifests.
4. Proceed to §Retrospective with `task_id: null` and
   `skill: plan-backlog`. Then commit. Then exit the invocation.

---

## Retrospective

After the primary branch finishes, run the `retrospective` skill. Read
[skills/retrospective/SKILL.md](../skills/retrospective/SKILL.md) — it is the
authoritative procedure. Summary of inputs:

- `task_id` — the task just completed (or `null` for Branch B).
- `run_id` — the run id you used in `run.json`.
- `skill` — the skill that was exercised (`plan-backlog` for Branch B).
- `outcome` — the terminal state returned by `coc complete`.

The retro writes one file to `ops/retrospectives/YYYY/MM/DD/retro-<ulid>.md`
and validates against `schemas/retrospective.schema.json`. It also appends a
`run.end` event referencing the retro's path.

### Retro cadence

Default cadence: **every run** until retros stop producing actionable
improvements. Specifically, retros run on every terminal state until a
sustained window of ≥10 consecutive retros with `actionable: false`. After
that, the cadence narrows to `blocked`/`failed` outcomes only — see
"Retiring this skill" in `skills/retrospective/SKILL.md`.

The cadence transition is itself a reviewable change: record it as a
`review-records` task with a concrete edit to the skill's frontmatter.

---

## Local commit

When all artifacts for **the current iteration** are written and
validated:

1. `uv run coc validate` — must exit 0.
2. `git add` only the paths you actually wrote in this iteration. Never
   `git add -A` or `git add .`. The list is: task manifests moved by
   `coc lease/complete`, the run report, any registry edits the envelope
   produced, the retro file, and any new inbox manifests from a proposal.
3. `git commit -m "<task-type>(<task-id>): <terse summary> [auto]"` — the
   `[auto]` suffix marks the commit as agent-produced so a reviewer can
   filter. **One commit per iteration**, not one commit per invocation.
4. Do not push. Do not force. Do not amend.

If the commit fails (pre-commit hook, signing, etc.), do not bypass.
Capture the failure in the iteration's retro `blockers` list, leave the
working tree as-is for human resolution, **and exit the invocation**
without starting a new iteration. A dirty working tree fails the next
invocation's preflight, so chaining further iterations on top of an
uncommitted failure would compound the damage.

---

## Stop conditions

Two layers: **iteration-level** stop conditions only end the current
iteration (the loop may continue to the next), and **invocation-level**
stop conditions end the whole batch.

### Iteration-level (current iteration ends; loop may continue)

- The task's `coc complete` has returned a terminal state and the
  retrospective is written. Commit, then proceed to the next iteration
  (§Branches Branch A step 7) if budget and counts allow.
- A "Block or fail when" clause in the active skill applies. Use
  `status: blocked` in `run.json` and still run the retrospective —
  blocks are exactly the iterations where retros are most valuable.
  Then commit and proceed.

Underspecified task manifests resolve to `blocked`, not to clarifying
questions. Ambiguity is a proposal for improvement, not a conversation.

### Invocation-level (whole invocation ends, no further iterations)

- Iteration count has reached `max_tasks_per_run`. Exit cleanly.
- The per-invocation soft budget has been exceeded (§Budget). Finish
  the current iteration's commit, then exit.
- `coc next` returned exit 1 *and* Branch B has run this invocation.
  Exit cleanly.
- Preflight failed. Write the abort event, do not touch the queue.
- A non-negotiable from AGENTS.md would be violated by the next action
  in any iteration.
- The lease could not be reclaimed after one retry (contention). Write
  the abort event and exit. Do not start a new iteration.
- The current iteration's commit failed. Leave the dirty tree for human
  resolution and exit (per §Local commit).

---

## Budget and heartbeats

Two budgets: **per-iteration** and **per-invocation**.

**Per-iteration soft budget**: 30 minutes of wall-clock execution after
the lease is claimed, excluding the retrospective. If a single iteration
crosses this, finish the current step, set `status: blocked` with a
`budget_exceeded` reason in `notes`, run the retrospective, commit, and
exit the invocation (do not start a new iteration on top of a
budget-exceeded one — the failure mode is usually structural and will
recur).

**Per-invocation soft budget**: `max_tasks_per_run × 15` minutes of
wall-clock total (default 75 minutes for the default of 5 iterations).
If the cumulative wall-clock across iterations crosses this, finish the
current iteration's commit and exit the invocation, even if the
iteration count is below `max_tasks_per_run`. The 15-min/iteration
average reflects the expectation that batched iterations are faster
than single-task runs because skills/schemas/taxonomy are cached in
agent context — pure-task wall-clock for a typical iteration runs 2–10
minutes once the fixed load cost is amortized.

Record both in `run.json` so the watchdog and retrospectives have evidence:

```json
{
  "heartbeats": 2,
  "budget": {
    "minutes_allotted": 30,
    "minutes_elapsed": 18.4,
    "exceeded": false
  }
}
```

When `exceeded: true`, add a short `reason` string (e.g.
`"slow-literature-fetch"`, `"external-api-rate-limit"`). Populate
`heartbeats` from the number of `task.heartbeat` events you appended
during this run — the watchdog (`uv run coc requeue`) uses them to
distinguish live-but-slow runs from crashed ones when deciding whether to
reap a stale lease.

### Watchdog contract

A separate scheduler (not this run) periodically invokes
`uv run coc requeue`. It moves any task in `leased/` whose
`lease.last_heartbeat` is older than `lease.ttl_minutes` back to `ready/`
(or to `failed/` once `attempts >= max_attempts`). To avoid being reaped
mid-run, heartbeat at least once every `ttl_minutes / 3` wall-clock
minutes. With the default 90-minute TTL, that means at least every 30
minutes.

---

## References

- [AGENTS.md](../AGENTS.md) — operating model and non-negotiables.
- [prompts/task-envelope.md](./task-envelope.md) — inner per-task contract.
- [skills/retrospective/SKILL.md](../skills/retrospective/SKILL.md) —
  post-run assessment procedure.
- [schemas/run.schema.json](../schemas/run.schema.json) — run report shape.
- [schemas/retrospective.schema.json](../schemas/retrospective.schema.json) —
  retro frontmatter shape.
