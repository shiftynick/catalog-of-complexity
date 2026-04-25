---
retro_id: retro-01KQ3ERM5DDKFHBX72B9JZ42HN
task_id: tsk-20260423-000020
run_id: run-01kq3en8b28gp9133k6z3c2d09
skill: profile-system
timestamp: '2026-04-25T23:18:30Z'
agent: claude-code/Shiftor/55488
actionable: true
confidence: high
what_worked:
  - 'AGENTS.md "What counts as a system worth cataloging" plus profile-system "Block or fail when" gave an unambiguous instance-not-type call for the H2 candidate — same pattern that retired sys-000001 (Amazon rainforest) and blocked tsk-20260424-000001 (BZ reaction). The criterion is doing real work in the autorun.'
  - 'Removing the stale `unblock: {kind: task-complete, task_id: tsk-20260425-000012}` field after re-blocking under a different reason prevented the next `coc advance` from re-promoting the task and oscillating in/out of ready/.'
blockers:
  - 'The task arrived in `ready/` because its prior block reason was source-not-acquired with a task-complete unblock pointing to tsk-20260425-000012; when that acquisition completed, the preflight unblock sweep auto-promoted it back to ready/ — even though the deeper instance-not-type problem had not been resolved. The unblock condition is too narrow: it tracks the source-debt block but is silent on the type-vs-instance block, so resolved source debt resurrects tasks that should remain blocked. Same condition applies to tsk-20260424-000001 (BZ reaction) which is also re-promoted to ready/ in this run despite an earlier instance-not-type block.'
proposed_improvements:
  - target: skills/profile-system/SKILL.md
    change: |-
      In the "Block or fail when" instance-not-type bullet, add a final
      sentence: "When this clause fires on a task that already carries an
      `unblock` field from a prior different-reason block, clear the
      `unblock` field after `coc complete --state blocked`. Otherwise the
      next `coc advance` will re-promote the task once the prior block's
      condition resolves, masking the unresolved instance-not-type issue."
    rationale: |-
      Unblock fields are tied to the *previous* block reason but are not
      cleared on subsequent re-blocks. tsk-20260423-000020 (H2) and
      tsk-20260424-000001 (BZ) both arrived in ready/ via a stale
      task-complete unblock that resolved source-debt, after the type-vs-
      instance issue was already known. The skill's procedure should
      explicitly call out the cleanup so future agents don't leave
      oscillation traps in blocked/.
    severity: moderate
  - target: prompts/autonomous-run.md
    change: |-
      In the Preflight section's `coc advance` bullet, after the existing
      "Satisfied tasks are moved blocked/ → ready/ with `lease.attempts`
      reset to 0" sentence, add: "Unblock conditions only verify the
      named taxonomy slug or upstream task; they do not re-evaluate the
      task's full block history. A task previously blocked for reason A
      with an unblock for A may carry a separate unresolved reason B,
      and re-promotion will resurrect the B issue. Skills that re-block
      a previously-blocked task under a different reason MUST clear the
      stale unblock field as part of the block step."
    rationale: |-
      Same root cause as the SKILL.md improvement above, surfaced at the
      autorun-prompt level so other skills (review-records,
      extract-observations) inherit the rule rather than each having to
      re-discover it. The autorun is the right place for this because
      the coupling is between coc advance's narrow unblock check and any
      skill that can multi-block a task.
    severity: moderate
---

Iteration 2 of a multi-task autonomous run. The dihydrogen molecule
(H2) candidate was blocked as instance-not-type — H2 is a specific
molecular species, not a type-level archetype; the type is
`molecular-system` and H2 belongs in its `canonical_examples`
alongside H2O, CO2, benzene, etc. Same call as recent commits 6ed3053
(BZ reaction) and d1ef626 (Amazon rainforest deprecation).

The actionable item is structural, not value-judgment: an unblock
field tied to a since-resolved source-debt block stayed on the task
through a subsequent instance-not-type block, and the preflight
`coc advance` resurrected it. Two follow-on tasks (tsk-20260424-000001
BZ, tsk-20260423-000020 H2) both demonstrate this. The fix is a one-
line addition to profile-system's "Block or fail when" instance-not-
type bullet plus an autorun-prompt clarification — clear stale unblock
fields when re-blocking under a different reason. I cleared the field
on this task before commit so it stays blocked until human review.
