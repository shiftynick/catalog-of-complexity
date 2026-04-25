---
retro_id: retro-01KQ3B585V95C0EJ2VYFHX7XQY
run_id: run-01KQ3B3HQBM24V0NQDDHD5YAG0
task_id: tsk-20260425-000016
skill: review-records
timestamp: 2026-04-25T22:36:00Z
agent: claude-code/run-01KQ3B3HQBM24V0NQDDHD5YAG0
actionable: true
confidence: medium
what_worked:
  - "Task manifest's reviewer-steps block was specific enough (set status, bump updated_at, append Deprecation section, name replacement slugs) that the edit was unambiguous; no judgment calls about scope."
  - "no-delete policy explicit in the manifest notes — kept the entry on disk for audit, just flipped status and appended prose."
  - "Companion-deprecation list in the manifest let the notes.md Deprecation section cross-reference the rest of the batch (sys-000002/000004/000005/000006) without re-deriving them."
  - "Tier-0.75 sweep + `coc advance` ran cleanly; new acquire-source manifests validated first time."
blockers: []
proposed_improvements:
  - target: skills/plan-backlog/SKILL.md
    change: >
      In Tier 0.75's "Unblock wiring for blocked tasks" sub-section, qualify the
      wiring rule by block reason: only wire `unblock` on a blocked task whose
      block reason is `source-not-acquired` (or whose existing block-event
      payload references a missing source ref). Skip wiring when the block
      reason is semantic (`instance-not-type`, taxonomy-mismatch, etc.) — those
      tasks are not waiting on source acquisition and unblocking them creates
      a wasted lease/re-block round-trip. The current text reads as
      unconditional ("set the blocked task's `unblock` field to ..."), which
      drove a judgment call this run on tsk-20260425-000008 / 000009 (both
      blocked as instance-not-type but with prefixed source_refs).
    rationale: >
      Removes ambiguity for the next agent and prevents Tier-0.75 from
      generating spurious unblock chains on tasks that need re-scoping rather
      than source-acquisition. Forward-compatible — adds a precondition, does
      not invalidate existing wired tasks.
    severity: minor
  - target: skills/plan-backlog/SKILL.md
    change: >
      Update the Tier 0.75 multi-source caveat to mention `kind: sources-resolved`
      as a first-class option for blocked tasks with N>1 missing prefixed refs.
      The current text still says "can only carry one `unblock` condition under
      the current schema (`taxonomy-slug-exists` | `task-complete`)" and
      describes the multi-pass convergence loop as the only resolution. The
      `sources-resolved` kind landed via tsk-20260425-000006 and eliminates the
      loop when *all* of a task's source_refs have acquire-source tasks emitted
      (across passes). The skill should describe the new option and when to
      prefer it (covers all refs in one pass) vs. task-complete-to-last (still
      correct when only some refs covered this pass).
    rationale: >
      The schema and runtime already support sources-resolved; the skill text
      is stale and points readers at a workaround the codebase has outgrown.
      Stale instructions are a recurring friction source for autonomous runs.
    severity: moderate
---

## What happened

Leased the highest-priority ready task `tsk-20260425-000016` (review-records,
deprecate sys-000001 Amazon rainforest as instance-not-type per the AGENTS.md
type-level inclusion criterion). The manifest's reviewer steps were precise:
flip `status` to `deprecated`, bump `updated_at`, append a Deprecation section
to `notes.md` naming the replacement type slugs (`system-class:forest-biome`
already in taxonomy; `system-class:ecosystem` pending) and the no-delete audit
posture, with companion deprecations cross-referenced. Both edits validated
first time.

## Friction

The Tier-0.75 sweep this invocation surfaced 6 unmet prefixed source_refs
across two blocked tasks (`tsk-20260425-000008` E. coli K-12 metabolic network,
`tsk-20260425-000009` E. coli K-12 prokaryotic cell). Both are blocked as
`instance-not-type`, *not* `source-not-acquired`. The skill's Tier-0.75
"Unblock wiring" rule is unconditional in its current wording, but wiring
those tasks would have been wrong (sources won't address the semantic block).
Skipped the wiring — captured as the moderate-severity proposal above. The
skill's multi-source caveat is also stale w.r.t. the new `sources-resolved`
unblock kind; second proposal flags it.
