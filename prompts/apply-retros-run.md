# Apply-Retros Run

Daily scheduled prompt that consumes unprocessed retrospectives, clusters
their `proposed_improvements` by target, and emits one `review-records`
task per cluster into `ops/tasks/inbox/`. Sibling of
[prompts/autonomous-run.md](autonomous-run.md), scoped to the
`apply-retros` skill.

This run does **not** execute edits. Edits land when the emitted
`review-records` manifests are picked up by a subsequent autonomous run
(`review-records` is auto-promote-eligible per the autonomy policy).

---

## Contract

You are beginning a scheduled daily apply-retros run. You must:

1. Read and obey [AGENTS.md](../AGENTS.md). Its "Non-negotiables",
   "Quality bar", and "Sensitive actions" sections govern everything
   below.
2. Execute exactly one apply-retros pass per the Procedure section.
3. Run the `retrospective` skill after the pass finishes, regardless of
   whether any clusters were emitted.
4. Commit locally only (`git commit`). Do not push.
5. Stop when the Procedure's stop conditions apply. Do not ask
   clarifying questions — an underspecified state resolves to a blocked
   run, not a dialogue.

---

## Preflight

- `uv run coc validate` exits 0. If it fails, abort this run, append a
  `run.aborted` event to `ops/events/run-events.jsonl`, and exit.
- `git status --porcelain` is clean. If there are uncommitted changes
  from a previous run, abort with `run.aborted` and leave the working
  tree for a human to resolve.

Record both checks in the run report `notes` field.

---

## Procedure

1. Read [skills/apply-retros/SKILL.md](../skills/apply-retros/SKILL.md).
   Its procedure is authoritative. The inputs below are the scheduled
   defaults — override only if the skill's "Block or fail when" clauses
   apply.
2. Invoke apply-retros with:
   - `window_days: 7` — process retros from the past week.
   - `severity_floor: moderate` — daily-cadence default. Minor proposals
     aren't dropped: they remain in the retro file and will be picked up
     if a human lowers the floor in an ad-hoc invocation, or if they
     reappear in a future retro.
   - `max_clusters: 5` — cap per run so inbox doesn't spike.
3. Follow the skill's procedure steps 1–7 exactly:
   - Load consumed-retro set from `ops/events/run-events.jsonl`.
   - Walk `ops/retrospectives/YYYY/MM/DD/` within the window.
   - Cluster surviving proposals by `target` path.
   - Emit one `review-records` manifest per cluster (up to
     `max_clusters`), priority `high` if any proposal is `severity:
     major`, else `normal`.
   - Append one `retro.consumed` event per retro touched (including
     retros whose proposals didn't survive the filter).
   - Write the consumption report to
     `ops/runs/YYYY/MM/DD/<run-id>/retro-consumption.md`.
4. Validate every manifest emitted:
   `uv run coc validate ops/tasks/inbox/`. On failure, delete the
   offending manifest, record the failure in the consumption report's
   **Errors** section, and set the run's `status: blocked`.
5. Write the run report to
   `ops/runs/YYYY/MM/DD/<run-id>/run.json` conforming to
   [schemas/run.schema.json](../schemas/run.schema.json):
   - `task_id: null` (this run has no owning task).
   - `status: success` unless a "Block or fail when" clause fired.
   - `outputs`: the emitted manifests + the consumption report, in the
     order written.
   - `events_appended`: count of `retro.consumed` lines appended.
   - `heartbeats: 0`, `budget.minutes_allotted: 10`.

---

## Retrospective

After the procedure finishes, run the `retrospective` skill. Read
[skills/retrospective/SKILL.md](../skills/retrospective/SKILL.md). Inputs:

- `task_id: null`
- `run_id`: the run id you used in `run.json`.
- `skill: apply-retros`
- `outcome`: the terminal status from step 5.

The retro cadence narrows to `blocked`/`failed`-only once ≥10
consecutive retros report `actionable: false`. Until then, run it every
pass. A no-op apply-retros run (zero clusters because nothing's in
window) is the cheapest retro possible — it should report
`actionable: false` and contribute toward the narrowing threshold.

---

## Local commit

1. `uv run coc validate` — must exit 0.
2. `git add` only the paths you actually wrote: the 0+ new inbox
   manifests, the run report, the consumption report (if it's under
   `ops/runs/` it's gitignored — skip; the report lives with the rest
   of the run artifacts), the retro file, and the appended
   `ops/events/run-events.jsonl`.
3. `git commit -m "apply-retros(<run-id>): <N> clusters emitted [auto]"`
   where `<N>` is the cluster count (0 if nothing was in window).
4. Do not push. Do not force. Do not amend.

If the commit fails (pre-commit hook, signing, etc.), do not bypass.
Capture the failure in the retro `blockers` list and leave the working
tree for human resolution.

---

## Stop conditions

Stop immediately — do not chain further work — when any of these hold:

- The procedure and retrospective are written, the commit is made. Exit.
- Preflight failed. Write the abort event, do not touch the queue.
- A "Block or fail when" clause in apply-retros applies (ghost target,
  retro schema drift). Use `status: blocked` in `run.json` and still
  run the retrospective — blocks are exactly the runs where retros are
  most valuable.

Zero clusters emitted is **not** a block — it's the healthy idle state
for apply-retros. Record it as `status: success` with a note in
`run.json`.

---

## Budget

Soft budget per run: 10 minutes of wall-clock execution. apply-retros is
a lightweight clustering pass — crossing this budget means something is
wrong (retro file parse failures, event log corruption). If you cross
it, finish the current step, set `status: blocked` with a
`budget_exceeded` reason, and let the next scheduled run resume.

---

## References

- [AGENTS.md](../AGENTS.md) — operating model.
- [skills/apply-retros/SKILL.md](../skills/apply-retros/SKILL.md) —
  authoritative procedure.
- [skills/retrospective/SKILL.md](../skills/retrospective/SKILL.md) —
  post-run assessment.
- [prompts/autonomous-run.md](autonomous-run.md) — sibling prompt for
  hourly task execution.
- [schemas/run.schema.json](../schemas/run.schema.json),
  [schemas/event.schema.json](../schemas/event.schema.json),
  [schemas/retrospective.schema.json](../schemas/retrospective.schema.json)
  — shape contracts for outputs.
