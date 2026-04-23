---
retro_id: retro-S33PETDP3NANVPKCXXRYN7JKKP
task_id: tsk-20260423-000010
run_id: run-993eb84a9d954aa5911f2be2e4
skill: review-records
timestamp: 2026-04-23T18:34:00Z
agent: claude-code/Shiftor/91532
actionable: false
confidence: high
what_worked:
  - The apply-retros cluster carried a clean, minimal scope (single file, prose only), which made the edit unambiguous.
  - The Watchdog contract section already specified the correct cadence, so the fix was a consistency alignment rather than a design decision.
blockers: []
proposed_improvements: []
---

Minimal prose edit to `prompts/autonomous-run.md` Branch A step 4:
relaxed the "every 15 minutes" rule to `lease.ttl_minutes / 3` (30 min
at default TTL) and documented that sub-cadence runs legitimately
emit `heartbeats: 0`. This brings Branch A into agreement with the
Watchdog contract section in the same file. No downstream artifacts
needed changes — the run report shape and `coc requeue` behaviour are
unchanged.
