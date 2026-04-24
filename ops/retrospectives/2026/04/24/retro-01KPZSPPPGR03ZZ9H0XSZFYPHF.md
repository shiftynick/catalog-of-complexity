---
retro_id: retro-01KPZSPPPGR03ZZ9H0XSZFYPHF
task_id: tsk-20260423-000019
run_id: run-01KPZSN28K5FZ47S81VX390RJ1
skill: profile-system
timestamp: '2026-04-24T13:09:00Z'
agent: claude-code/Shiftor/123964
actionable: true
confidence: medium
what_worked:
  - 'profile-system SKILL.md Block clause (source-not-acquired) gave the run an unambiguous terminal state the moment `registry/sources/` was checked — no improvisation, no fabricated `src-*` id, no speculative partial profile.'
  - 'system.schema.json `source_refs` pattern `^src-[0-9]{6}--[a-z0-9-]+$` is a hard backstop: even if an agent tried to bypass the skill block, the schema would refuse doi:/isbn: entries at validate time. Defence-in-depth held.'
  - 'Preflight `coc advance` cleanly promoted tsk-20260424-000001 (BZ profile-system) into ready/, so the next run has productive non-blocked work even though this run parked.'
blockers:
  - 'Task manifest carries three prefixed source_refs (isbn:9780582356924, isbn:9781107189638, doi:10.18434/T4W30F) but no corresponding acquire-source task exists in inbox/, ready/, or done/, and `coc complete --state blocked` does not accept a free-form reason string — the block rationale had to be carried in the run.json `notes` field alone. A reviewer scanning `ops/tasks/blocked/tsk-20260423-000019.yaml` will not see why it is blocked without cross-referencing the run report.'
  - 'The profile-system SKILL.md Block clause explicitly lists `doi:`, `arxiv:`, `url:` as prefixed forms but is silent on `isbn:`. Two of this task-list three source_refs are isbn: prefixes. The intent is clearly the same (unregistered external identifier), but the letter of the rule only catches the single doi:.'
proposed_improvements:
  - target: skills/profile-system/SKILL.md
    change: "In the Preconditions bullet about prefixed source_refs and in the matching Block-or-fail clause, add `isbn:` (and ideally `pmid:`, `handle:`) to the enumerated prefix list, or reword to 'any prefixed form (doi:/arxiv:/url:/isbn:/… — any scheme other than an `src-NNNNNN--<slug>` id)' so the rule is clearly closed under new prefix types."
    rationale: "Today the rule textually only catches `doi:`/`arxiv:`/`url:`, but scouts already emit `isbn:` refs (this task has two). An agent reading the skill narrowly could conclude isbn: is not covered and try to inline-cite books without acquisition. The schema backstop will still reject the system.yaml, but the block reason will then be a confusing schema failure instead of the intended source-not-acquired signal."
    severity: minor
  - target: ops/cli/coc/complete.py
    change: "Add an optional `--reason <slug>` flag to `coc complete` that, when `--state` is `blocked` or `failed`, persists the reason into the task manifest (e.g. `lease.block_reason: source-not-acquired`) and into the `task.complete` event payload."
    rationale: "Right now the only structured record of *why* a task blocked lives in the run.json notes field, which is not surfaced by `coc next`/`coc advance` or easily greppable. A normalized reason slug (source-not-acquired, taxonomy-slug-missing, boundary-circular, competing-classes, …) would let plan-backlog Tier 0.75 scan blocked/ to decide which acquire-source tasks to seed, and let future retros aggregate block-reason frequency."
    severity: moderate
  - target: skills/plan-backlog/SKILL.md
    change: "Explicitly state that Tier 0.75 (acquire-source seeding) should scan `ops/tasks/blocked/` for profile-system tasks with unregistered prefixed source_refs, and emit one acquire-source task per distinct external identifier (doi/isbn/arxiv/url). Reference `--unblock-on-task` so the blocked profile-system task can be wired to auto-resume once the final acquire-source task completes."
    rationale: "The profile-system skill already points at plan-backlog Tier 0.75 as the acquirer, but plan-backlog's own SKILL.md does not yet document scanning blocked/ for acquisition triggers. Closing that loop means a source-not-acquired block reliably produces acquire-source tasks on the next run instead of sitting in blocked/ indefinitely."
    severity: moderate
---

# Retrospective — run-01KPZSN28K5FZ47S81VX390RJ1 (profile-system)

Primary run, Branch A. Leased tsk-20260423-000019 (profile-system hydrogen-atom), immediately hit the `source-not-acquired` block clause: three prefixed source_refs (2× isbn:, 1× doi:), zero matching `registry/sources/src-*` entries. No canonical profile written; terminal state blocked; task now in `ops/tasks/blocked/`.

Preflight: `coc validate` clean, git clean, `coc advance` promoted tsk-20260424-000001 (BZ profile-system) from inbox → ready. `coc next` → tsk-20260423-000019. Lease acquired first try. No heartbeats (sub-cadence run, ~2 min).

The three proposals above are layered: the SKILL.md prefix-list tightening is cheap, the `coc complete --reason` flag is the structural fix, and wiring plan-backlog's blocked/ scan closes the acquisition feedback loop so hydrogen (and future profile-system tasks carrying book/paper refs) can actually progress without human hand-holding. None are severity: major, so no follow-up `review-records` manifest is emitted from this retro — a human can pick them up via the webUI prune workflow.
