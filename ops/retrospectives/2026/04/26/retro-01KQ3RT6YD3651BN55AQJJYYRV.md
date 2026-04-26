---
retro_id: retro-01KQ3RT6YD3651BN55AQJJYYRV
task_id: tsk-20260425-000020
run_id: run-01KQ3RRHQ1CFBDQ5SRP7XZK5P2
skill: review-records
timestamp: '2026-04-26T02:09:50Z'
agent: claude-code/scheduled/coc-auto-run
actionable: false
confidence: high
what_worked:
  - "Companion-task convention: tsk-20260425-000017 (gut microbiome deprecation) ran one iteration earlier and left a near-identical Deprecation section in sys-000002/notes.md. Mirroring that structure for sys-000006 took seconds and keeps the two paired entries narratively symmetric for the future type-level `microbiome` entry."
  - "Tier-0.75 source-debt sweep was a no-op this run (all 9 unique prefixed refs across the active task pool already had open or done acquire-source tasks). Idempotency on the `Source debt: <ref>.` notes prefix prevented double-emission with zero false negatives."
  - "Manifest's acceptance_tests named the replacement slug (`microbiome`) and the canonical-examples reuse plan up front, so the only judgment call was prose phrasing — schema/validation path was deterministic."
blockers: []
proposed_improvements: []
---

Second of the two paired microbiome-instance retirements (gut + rhizosphere
→ future type-level `microbiome` entry). Identical shape to the
sys-000005 cortical microcircuit deprecation one iteration earlier:
status flip, updated_at bump, append Deprecation section naming the
replacement archetype, validate. No friction worth recording. The
deprecation pattern is now well-rehearsed across three consecutive
review-records passes — if a fourth instance-retirement task appears it
should run on the same template without further skill changes.
