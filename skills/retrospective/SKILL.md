---
name: retrospective
description: Post-task reflection that produces a structured assessment of the run just completed. Invoked by the autonomous-run prompt after every task (not queue-driven). Emits a retrospective file under ops/retrospectives/ whose frontmatter validates against schemas/retrospective.schema.json. Flags actionable improvements to AGENTS.md, SKILL.md, prompts, schemas, or process so a reviewer can turn them into follow-up tasks.
status: postrun
inputs:
  - 'task_id — id of the task that was just completed (or blocked/failed).'
  - 'run_id — id of the run this retrospects. Optional on the first bootstrap pass.'
  - 'skill — name of the skill that was exercised.'
  - 'outcome — terminal state reported by coc complete (done, review, blocked, failed).'
outputs:
  - 'ops/retrospectives/YYYY/MM/DD/retro-<ulid>.md with YAML frontmatter per schemas/retrospective.schema.json.'
  - 'Zero or one proposal tasks in ops/tasks/inbox/ if an improvement is severe enough to warrant its own follow-up.'
stop_conditions:
  - 'A retrospective file exists and passes coc validate.'
  - 'The retro cadence policy for this task-type is satisfied (default: every task until retros stop producing actionable items).'
---

## When to use

This skill runs at the tail of every autonomous scheduled run. It is not
picked from the queue — it is invoked directly by
[`prompts/autonomous-run.md`](../../prompts/autonomous-run.md) after the
primary task's `coc complete` call. Do not create queue manifests of type
`retrospective`.

Use this skill to:

- Record what actually happened during the run, in the agent's own words.
- Flag anything that slowed the run, blocked it, or required judgment the
  skill/prompt/schemas did not help with.
- Propose concrete edits — not aspirational goals — to repo files that would
  have avoided the friction.

Do **not** use this skill to summarize the canonical records produced. Those
live in the run report (`ops/runs/.../run.json`) and are already event-logged.

## Preconditions

- `coc complete` has been called on the primary task (the task is in
  `review/`, `done/`, `blocked/`, or `failed/`).
- The run report (`ops/runs/YYYY/MM/DD/<run-id>/run.json`) has been written.
- AGENTS.md, the active SKILL.md, and the task manifest are readable — these
  are the three candidate targets for improvements.

## Procedure

1. Read the task manifest, the run report, the active SKILL.md, and any
   schemas referenced by the task's `acceptance_tests`.
2. Generate a ULID for `retro_id` (format `retro-<26-char-crockford-base32>`).
3. Assemble frontmatter fields:
   - `retro_id`, `task_id`, `run_id`, `skill`, `timestamp` (UTC ISO-8601 Z),
     `agent` (the `actor` value used in event-log entries).
   - `what_worked`: short bullet-like strings. Only include items that were
     non-obvious or worth preserving.
   - `blockers`: things that forced a judgment call the layered prompts did
     not cover. Empty list is fine and common.
   - `proposed_improvements`: zero or more objects with `target` (a
     repo-relative path), `change` (what to do), `rationale` (why), and
     optional `severity` (`minor`, `moderate`, `major`). Every proposal must
     reference a concrete file — no vague process wishes.
   - `actionable`: `true` iff `proposed_improvements` is non-empty OR
     `blockers` surface a process issue.
   - `confidence`: one of `low`, `medium`, `high` — how sure you are that
     adopting the proposals would actually improve future runs.
4. Write the retro to
   `ops/retrospectives/YYYY/MM/DD/retro-<ulid>.md` with the YAML frontmatter
   followed by a short markdown body (≤15 lines of prose is plenty).
5. Append an event to `ops/events/run-events.jsonl` of kind `run.end` with
   `payload.retro_path` set to the retro's repo-relative path.
6. If any proposal is `severity: major`, also write a follow-up task manifest
   to `ops/tasks/inbox/tsk-YYYYMMDD-NNNNNN.yaml` (type `review-records` or
   `setup-repo` as appropriate) that captures the change as a reviewable
   unit. Do not promote to `ready/`; the human reviewer decides.

## Output shape

- One markdown file with YAML frontmatter. The frontmatter must be the first
  block (`---` on line 1), followed by a `---` close line, followed by
  optional prose.
- `coc validate` must accept it.
- The retro references the task, run, and skill by id — a reader should be
  able to reconstruct the full context without opening the retro file.

## Block or fail when

- The run report is missing — retros are produced *from* evidence, not
  speculation. Block the retro and note the missing artifact.
- The task is still in `leased/` or `running/` (retro cadence is after
  `coc complete`, not before).
- A proposal cannot name a concrete `target` path — drop it rather than use
  a placeholder.

## Retiring this skill

Once retros stop producing actionable improvements across a sustained window
(default: ≥10 consecutive retros with `actionable: false`), flip `status` to
`postrun-onfailure` and only invoke the skill on `blocked`/`failed` terminal
states. Record the transition in a `review-records` task so the change is
observable in the git history.

## References

- [AGENTS.md](../../AGENTS.md) — operating model, quality bar, sensitive actions.
- [prompts/autonomous-run.md](../../prompts/autonomous-run.md) — the master prompt that invokes this skill.
- [schemas/retrospective.schema.json](../../schemas/retrospective.schema.json) — frontmatter contract.
