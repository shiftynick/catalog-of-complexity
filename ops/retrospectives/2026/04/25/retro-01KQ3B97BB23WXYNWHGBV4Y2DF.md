---
retro_id: retro-01KQ3B97BB23WXYNWHGBV4Y2DF
run_id: run-01KQ3B97BA6QT8KHX7E6R1NSNG
task_id: tsk-20260424-000001
skill: profile-system
timestamp: 2026-04-25T22:42:30Z
agent: claude-code/run-01KQ3B97BA6QT8KHX7E6R1NSNG
actionable: true
confidence: high
what_worked:
  - "AGENTS.md \"What counts as a system worth cataloging\" + profile-system SKILL.md \"Block or fail when\" together gave an unambiguous diagnosis (instance-not-type) with no judgment call — slug names a specific named reaction, taxonomy already lists BZ as a canonical example of chemical-reaction-network."
  - "Precedent from tsk-20260425-000008 / 000009 (same shape, blocked earlier in the day) made the resolution mechanical: block, no auto-unblock, leave the rich prose for lifting into the eventual type-level profile's canonical_examples."
  - "The acquire-source unblock chain worked end-to-end — the FKN paper acquisition (tsk-20260425-000010) satisfied the task-complete unblock condition and `coc advance` moved this task to ready/. The unblock fired correctly; the instance-not-type issue is just orthogonal."
blockers: []
proposed_improvements:
  - target: skills/scout-systems/SKILL.md
    change: >
      Add an emission-time pre-check that rejects candidate slugs which name a
      specific instance (genus+species, person-named reactions, geography-named
      systems) when the proposed `system-class:*` slug already lists that
      instance as a canonical example in its taxonomy entry. The retro for
      tsk-20260425-000008 (E. coli metabolic network) already flagged this;
      this iteration is the third repeat (BZ-reaction = Belousov + Zhabotinsky
      proper names; BZ is explicitly listed as a canonical example under
      `system-class:chemical-reaction-network`). The check is cheap — string
      match the proposed slug against the description text of the proposed
      class — and would have stopped this task from reaching profile-system.
    rationale: >
      Repeat of a known retro proposal. Three downstream profile-system tasks
      (000008 / 000009 / this one) all blocked instance-not-type and consumed
      a lease cycle each because scout-systems didn't filter at emission. The
      cost of fixing scout-systems is one heuristic; the cost of repeating
      this mistake is one wasted lease per misidentified candidate.
    severity: moderate
  - target: skills/review-records/SKILL.md
    change: >
      Add a sub-procedure for the "instance-to-canonical-example
      recategorization" pattern: given a sys-* record (or a blocked
      profile-system task) whose candidate is an instance of an existing
      type-level system-class, the recategorization workflow is
      (1) identify the type-level slug, (2) when the type-level sys-* entry
      exists, append the instance to its `canonical_examples` array with the
      block reason's rationale as the example's `note`; (3) when the
      type-level entry does not exist yet, emit a profile-system task
      against the type-level slug and reference the blocked task in its
      notes for prose-lifting. Three blocked tasks (000008 / 000009 / this
      iteration) are now waiting for this recategorization pattern to
      exist.
    rationale: >
      Without a documented recategorization sub-pattern, each blocked
      instance-not-type task accumulates as long-lived state in `blocked/`
      with no defined resolution path. Documenting the pattern lets a
      reviewer (or a future review-records task) drain the backlog
      mechanically.
    severity: moderate
---

## What happened

Leased the next ready task `tsk-20260424-000001` (profile-system,
Belousov-Zhabotinsky reaction). Diagnosed it as instance-not-type per the
AGENTS.md inclusion criterion and the profile-system SKILL.md "Block or
fail when" clause: the candidate slug names a specific oscillating chemical
reaction discovered by Belousov and Zhabotinsky, while the type it
exemplifies (`system-class:chemical-reaction-network`) already exists in
`taxonomy/source/system-classes.yaml` and explicitly lists "Belousov-
Zhabotinsky oscillator" among its canonical examples in the class
description prose. Same shape as `tsk-20260425-000008` (E. coli K-12
metabolic network) and `tsk-20260425-000009` (E. coli K-12 prokaryotic
cell), both blocked earlier today.

## Friction

The acquire-source pipeline (Tier 0.75 + the new `task-complete` unblock
kind) successfully moved this task back from `blocked/` to `ready/` once
the FKN paper (`tsk-20260425-000010`, src-000005) was acquired. That part
of the system worked. But the move to ready/ surfaced a separate problem
that's now hit three times in two days: scout-systems is emitting
candidate slugs that are clearly instances rather than types, and
profile-system has to catch them at lease time. The check belongs at
emission time. Captured as a moderate proposal against
`skills/scout-systems/SKILL.md` plus a companion proposal documenting the
review-records recategorization sub-pattern that would let an agent
mechanically drain the backlog of three blocked tasks.
