---
retro_id: retro-01KQ3RX04ZZW1CPW73W2JGCRZZ
task_id: tsk-20260425-000029
run_id: run-01KQ3RX04ZZW1CPW73W2JGCRZY
skill: acquire-source
timestamp: '2026-04-26T02:11:50Z'
agent: claude-code/scheduled/coc-auto-run
actionable: false
confidence: high
what_worked:
  - "Block path was deterministic: SKILL.md `Block or fail when` clause names ISBN as unsupported, the manifest declared isbn:9780199541423, no resolver judgment needed."
  - "The retro-01KQ3EY1YNT5JKVQFVK0VHF4GT proposal (resolver-supports-prefix unblock + isbn_books.py module) is still the right structural fix; emitting another duplicate proposal here would just clutter apply-retros' clustering."
blockers: []
proposed_improvements: []
---

Iteration 2 — fourth ISBN unsupported-ref block in the recent
running cluster (Bransden & Joachain, Griffiths & Schroeter,
Szabo & Ostlund, now Atkins & Friedman). The pattern is a
consequence of plan-backlog Tier 0.75 fan-out: each unique ISBN
ref referenced by a blocked profile-system task spawns its own
acquire-source which then immediately re-blocks. The standing
proposal in retro-01KQ3EY1YNT5JKVQFVK0VHF4GT remains the load-bearing
fix; nothing new to add from this pass.
