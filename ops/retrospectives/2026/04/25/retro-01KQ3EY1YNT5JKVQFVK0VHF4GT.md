---
retro_id: retro-01KQ3EY1YNT5JKVQFVK0VHF4GT
task_id: tsk-20260425-000014
run_id: run-01kq3ex9xembk92xt2fyk0ejzc
skill: acquire-source
timestamp: '2026-04-25T23:23:30Z'
agent: claude-code/Shiftor/55488
actionable: true
confidence: medium
what_worked:
  - 'The acquire-source SKILL.md spelled out the unsupported-ref block disposition explicitly, so the ISBN-prefix case resolved deterministically — same outcome as commit 55f227d (isbn:9780471893844). No judgment call required.'
  - 'The inbox already carries the corrective task: tsk-20260425-000019 proposes adding an isbn_books.py resolver module. The path from "ISBN debt accumulates" → "resolver lands" → "ISBN acquire-source tasks succeed" is fully scoped without needing a new proposal.'
blockers:
  - 'No unblock kind in the task schema captures "a new resolver module exists in src/coc/sources/". The available kinds (taxonomy-slug-exists, task-complete, sources-resolved) all probe registry/taxonomy state, not source-tree state. ISBN acquire-source tasks therefore stay in blocked/ as orphans until a human re-promotes after the resolver lands. Five ISBN acquire-source tasks in flight today (000013, 000014, 000022, 000023, 000029, 000030, 000031) — all silently blocked with no auto-recovery path.'
proposed_improvements:
  - target: schemas/task.schema.json
    change: |-
      Add a new unblock kind `resolver-supports-prefix` with required field
      `prefix` (e.g. `prefix: isbn`). It fires during `coc advance` when
      `src/coc/sources/<prefix>_*.py` exists and the dispatch table in
      `src/coc/sources/__init__.py` includes the prefix. Then ISBN
      acquire-source tasks can carry `unblock: {kind: resolver-supports-
      prefix, prefix: isbn}` and auto-resume once tsk-20260425-000019
      (the isbn_books.py review-records task) lands.
    rationale: |-
      Today, when an acquire-source task hits unsupported-ref, the only
      recovery path is human re-promotion. The schema's existing unblock
      kinds (taxonomy-slug-exists, task-complete, sources-resolved) all
      probe registry/taxonomy state, not source-tree state. With seven
      ISBN acquire-source tasks already accumulating in blocked/, the
      cost of a curator re-promoting each one is starting to outweigh
      the cost of a one-time schema extension. The dispatch-table check
      is cheap (single-file read) and the field is opt-in — existing
      tasks aren't affected.
    severity: minor
  - target: ops/tasks/inbox/tsk-20260425-000019.yaml
    change: |-
      Add a follow-up to the review-records task description: after the
      isbn_books.py resolver lands, a single `coc advance` run should
      auto-promote every blocked ISBN acquire-source task once the new
      `resolver-supports-prefix` unblock kind exists (paired proposal
      against schemas/task.schema.json). Without that pair, the resolver
      rollout still needs a manual re-promotion step.
    rationale: |-
      Couples the resolver-implementation review-records task to the
      schema-extension proposal so they land together. Otherwise the
      resolver lands and the curator still has to manually re-promote
      seven blocked tasks — the original problem the schema extension
      is meant to solve.
    severity: minor
---

Iteration 4 of a multi-task autonomous run. The ISBN acquire-source
task blocked as unsupported-ref — same disposition as commit 55f227d
and a recurring pattern: every ISBN acquire-source task emitted by the
Tier-0.75 sweep blocks here until a resolver exists.

The actionable item is small but real: there is no schema-supported
auto-recovery from unsupported-ref. Once the isbn_books.py resolver
lands (via tsk-20260425-000019), each ISBN acquire-source task in
blocked/ needs human re-promotion because no `unblock` kind probes the
source tree. Adding a `resolver-supports-prefix` kind to
schemas/task.schema.json would let those tasks self-resume on the next
`coc advance`. Severity: minor — a curator can always do bulk
re-promotion by hand when the resolver lands. Confidence: medium —
the proposal is small in code volume but has a small surface (one new
unblock kind) so the design is easy to get wrong; an extra round of
review-records review would be appropriate before applying.
