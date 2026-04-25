---
retro_id: retro-01KQ3EVM3QP9F18DRV9EHQFC7Z
task_id: tsk-20260424-000001
run_id: run-01kq3etpms8jk6hjqapeczjgt5
skill: profile-system
timestamp: '2026-04-25T23:21:30Z'
agent: claude-code/Shiftor/55488
actionable: false
confidence: high
what_worked:
  - 'Second block on the same task using the same instance-not-type criterion converged in <3 minutes — the previous iteration''s retro proposal (clearing the stale unblock on re-block) was applied here and stopped the oscillation: tsk-20260424-000001 will not return to ready/ on the next `coc advance` because its task-complete unblock pointing at done tsk-20260425-000010 is gone.'
blockers: []
proposed_improvements: []
---

Iteration 3 of a multi-task autonomous run. The Belousov-Zhabotinsky
reaction task came back to ready/ via the preflight unblock sweep
(its source-debt acquire-source task tsk-20260425-000010 had landed
in done/), even though commit 6ed3053 had already blocked it as
instance-not-type. Same pattern as iteration 2's H2 task. I re-blocked
it under the same instance-not-type criterion and cleared the stale
`unblock: {kind: task-complete, task_id: tsk-20260425-000010}` field
to prevent another oscillation cycle.

No new actionable items: the previous iteration's retro
(retro-01KQ3ERM5DDKFHBX72B9JZ42HN) already proposed the SKILL.md and
prompts/autonomous-run.md edits that would codify this cleanup as a
rule. Adding a duplicate proposal would inflate the apply-retros
clustering signal without new information. Confidence: high — the
pattern is now seen on two tasks (H2, BZ) within minutes of each
other, both with the same root cause (source-debt unblock resolves
after a different-reason block was applied to the task).
