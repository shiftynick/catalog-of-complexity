# Autonomous Run

This is the master prompt fired on a schedule by Claude Code and OpenAI Codex.
It is the **outer** prompt — it selects a task, delegates execution via the
task envelope, and runs a retrospective afterward. One run completes one task
(or one explicit empty-queue branch) and then stops.

Do **not** chain multiple tasks in a single run. Parallelism across runs is
fine; parallelism within a run is not.

---

## Contract

You are beginning a scheduled autonomous run. You must:

1. Read and obey [AGENTS.md](../AGENTS.md). Its "Non-negotiables", "Quality
   bar", and "Sensitive actions" sections govern everything below.
2. Execute **exactly one** of the branches in §Branches below — "Primary
   task" or "Empty queue".
3. After the primary task's `coc complete` call returns, run the
   retrospective branch in §Retrospective. The retrospective runs for every
   terminal state (`done`, `review`, `blocked`, `failed`) until the cadence
   policy says otherwise.
4. Commit your changes locally only (`git commit`). Do not push, open PRs, or
   modify remotes. A human handles promotion.
5. Stop when §Stop conditions apply. Do not ask clarifying questions during
   the run — an underspecified task resolves to `status: blocked`.

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

Record all three checks, and the list of promoted task ids from `coc
advance`, as part of the run report `notes`.

---

## Branches

### Branch A — Primary task (queue non-empty)

1. `uv run coc next` — prints the highest-priority ready task id, or exits 1
   if the queue is empty. If exit 1, go to Branch B.
2. `uv run coc lease <task-id>` — claim it. Atomic move, no retry on
   contention; if the lease fails, another agent got there first. Re-run
   `coc next` once; if still contended, abort the run with `run.aborted`.
3. Read [prompts/task-envelope.md](./task-envelope.md). Fill its placeholders
   from the leased task manifest and execute the envelope's procedure exactly
   as written. The envelope handles writing the task's outputs, `run.json`,
   and the terminal `coc complete` call.
4. Heartbeat at least once per `lease.ttl_minutes / 3` of wall-clock work
   (so every 30 minutes at the default 90-min TTL):
   `uv run coc heartbeat <task-id>`. Runs that finish inside one cadence
   window may legitimately emit zero heartbeats — `heartbeats: 0` in
   `run.json` is expected for sub-cadence runs, not an anomaly.
5. On `coc complete`, capture the terminal state for use in the
   retrospective.
6. Proceed to §Retrospective.

### Branch B — Empty queue

The queue has no ready tasks. Spend this run on backlog upkeep so future
runs have productive work.

1. Invoke the `plan-backlog` skill directly (no queue manifest — it is a
   meta-skill, same status class as `retrospective`). Read
   [skills/plan-backlog/SKILL.md](../skills/plan-backlog/SKILL.md).
2. Its outputs: zero or more new task manifests written to
   `ops/tasks/inbox/`. Promotion to `ready/` is not part of this branch —
   the **next** run's preflight `coc advance` step picks up auto-eligible
   manifests. Types outside `AUTO_PROMOTE_TYPES` (e.g.
   `materialize-warehouse`, `build-release`) stay in `inbox/` until a
   human promotes them.
3. Write a `run.json` with `task_id: null` (Branch B runs have no owning
   task), `status: success`, and `outputs` listing any new manifests.
4. Proceed to §Retrospective with `task_id: null` and `skill: plan-backlog`.

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

When all artifacts are written and validated:

1. `uv run coc validate` — must exit 0.
2. `git add` only the paths you actually wrote. Never `git add -A` or
   `git add .`. The list is: task manifests moved by `coc lease/complete`,
   the run report, any registry edits the envelope produced, the retro
   file, and any new inbox manifests from a proposal.
3. `git commit -m "<task-type>(<task-id>): <terse summary> [auto]"` — the
   `[auto]` suffix marks the commit as agent-produced so a reviewer can
   filter.
4. Do not push. Do not force. Do not amend. Each run is one commit.

If the commit fails (pre-commit hook, signing, etc.), do not bypass. Capture
the failure in the retro `blockers` list and leave the working tree as-is
for human resolution.

---

## Stop conditions

Stop immediately — do not chain further work — when any of these hold:

- The task's `coc complete` has returned a terminal state and the
  retrospective is written. Commit and exit.
- A non-negotiable from AGENTS.md would be violated by the next action.
- Preflight failed. Write the abort event, do not touch the queue.
- The lease could not be reclaimed after one retry (contention). Write the
  abort event and exit.
- A "Block or fail when" clause in the active skill applies. Use
  `status: blocked` in `run.json` and still run the retrospective — blocks
  are exactly the runs where retros are most valuable.

Underspecified task manifests resolve to `blocked`, not to clarifying
questions. Ambiguity is a proposal for improvement, not a conversation.

---

## Budget and heartbeats

Soft budget per run: 30 minutes of wall-clock execution after the lease is
claimed, excluding the retrospective. If you cross this, finish the current
step, set `status: blocked` with a `budget_exceeded` reason in `notes`, and
let the next scheduled run resume.

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
