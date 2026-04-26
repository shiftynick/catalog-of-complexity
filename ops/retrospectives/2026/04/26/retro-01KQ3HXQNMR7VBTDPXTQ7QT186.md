---
retro_id: retro-01KQ3HXQNMR7VBTDPXTQ7QT186
task_id: tsk-20260425-000021
run_id: run-01kq3hx4n49ajtbpwrax87t48h
skill: acquire-source
timestamp: '2026-04-26T00:12:30Z'
agent: claude-code/Shiftor/55488
actionable: false
confidence: high
what_worked:
  - 'Determinism: `uv run coc acquire isbn:9780582356924` exits 1 with the same `unsupported-ref` failure the SKILL.md predicts, so the disposition was mechanical (status: blocked, no judgment). This is the third ISBN-only block in the autorun lineage (after tsk-20260425-000013 isbn:9780471893844 and tsk-20260425-000014 isbn:9780195096705).'
  - 'No proposal duplication: the prior retro retro-01KQ3EY1YNT5JKVQFVK0VHF4GT (iter 4 of the previous invocation) already proposed both schemas/task.schema.json `resolver-supports-prefix` unblock kind and the paired isbn_books.py resolver follow-up. Adding the same proposal here would just bloat the apply-retros cluster.'
blockers: []
proposed_improvements: []
---

Iteration 2 of this invocation. ISBN acquire-source task hit the
documented `unsupported-ref` block path. The recurrent ISBN-block
pattern (now ≥6 blocked acquire-source tasks across the lineage:
9780471893844, 9780195096705, 9780486691862, 9780582356924,
9780199541423, 9781107189638, plus 9781107038851 / 9781555810849
still in inbox/) has standing actionable proposals on file from a
prior retro — no new proposals warranted. When apply-retros runs,
this retro contributes evidence to that earlier cluster but no new
target. Flagged actionable: false to avoid double-counting.
