---
retro_id: retro-01KPXTDFBXK7S0W2DFK5ZQ829V
task_id: tsk-20260423-000012
run_id: run-01KPXTCHWXYWB5APZY4H0G02FY
skill: review-records
timestamp: '2026-04-23T18:43:00Z'
agent: claude-code/Shiftor/89048
actionable: true
confidence: medium
what_worked:
  - >-
    Apply-retros' clustering had already isolated this to a single,
    target-scoped fix in src/coc/queue.py with a clear acceptance test
    (malformed --outputs leaves the task in leased/ with no orphan
    task.complete event). Implementation was a four-line reorder plus one
    targeted regression test — exactly the right grain for a review-records
    cluster of size 1.
  - >-
    The existing tests/test_queue.py fake_ops fixture and _event_kinds helper
    made asserting "only task.lease appended, no task.complete" trivial. No
    new fixtures were needed.
blockers: []
proposed_improvements:
  - target: src/coc/queue.py
    change: >-
      Audit lease_task / heartbeat_task / requeue_stale for the same
      "rename-then-validate" ordering and apply the parse-before-mutate fix
      where applicable. requeue_stale in particular dump_yaml's then renames;
      a partial failure between the dump and the rename leaves an inconsistent
      `state` field. Emit one follow-up review-records task per offender if
      the audit finds anything.
    rationale: >-
      The leased task notes explicitly scoped this fix to complete_task and
      asked for follow-up tasks rather than bundling. The same atomicity
      gap likely exists elsewhere; auditing now is cheaper than reacting to
      another retro for the same class of bug.
    severity: minor
---

Tight, low-friction run. Preflight clean (coc validate OK, git clean,
coc advance promoted tsk-20260423-000012). Reordered complete_task() to
parse outputs_json before any state mutation, raising QueueError on
JSONDecodeError. Added test_complete_rejects_malformed_outputs_json_atomically
asserting leased/ persistence, no done/ file, and only task.lease in the
event log. All 17 queue tests pass; coc validate exits 0. Heartbeats: 0
(sub-cadence run, well under 30-minute window). Severity-minor follow-up
filed via the proposal above rather than a queued task — apply-retros
will cluster it if peers surface.
