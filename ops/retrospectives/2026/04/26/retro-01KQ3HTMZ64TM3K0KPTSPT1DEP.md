---
retro_id: retro-01KQ3HTMZ64TM3K0KPTSPT1DEP
task_id: tsk-20260425-000018
run_id: run-01kq3hsg4wnmwfkts2jg6pw4n6
skill: review-records
timestamp: '2026-04-26T00:09:00Z'
agent: claude-code/Shiftor/55488
actionable: false
confidence: high
what_worked:
  - 'The deprecation pattern (status: deprecated + Deprecation section in notes.md naming the replacement type slug + retain prose for canonical_examples reuse) is now well-rehearsed: this is the fourth instance-not-type retirement (sys-000001 hydrogen molecule, sys-000002 BZ reaction, sys-000003 human gut microbiome via tsk-20260425-000017, sys-000004 C. elegans here). The acceptance-test pattern in the manifest was specific enough to execute mechanically — no judgment calls needed beyond filling the deprecation prose.'
  - 'Schema permits status: deprecated directly (schemas/system.schema.json enum); no taxonomy edits or schema migrations required for the retirement.'
blockers: []
proposed_improvements: []
---

Iteration 1 of this invocation. Mechanical deprecation of sys-000004
(C. elegans) per the type-not-instance criterion in AGENTS.md "What
counts as a system worth cataloging". The detailed prose (959 cells,
302-neuron connectome, invariant cell lineage, dauer diapause,
~3-day life cycle) is preserved in notes.md as the model contribution
to the eventual `multicellular-organism` type entry's canonical_examples
section, alongside *Drosophila*, mouse, and human.

Four bootstrap-era instance entries have now been retired across the
recent autorun lineage. The pattern is stable enough that future
review-records tasks of this shape don't need a retrospective to add
to the corpus — flagged actionable: false. If a fifth such retirement
appears, consider folding the procedure into the review-records SKILL.md
explicitly so the manifest can be terser; for now the acceptance-test
text in the manifest is doing that job adequately.
