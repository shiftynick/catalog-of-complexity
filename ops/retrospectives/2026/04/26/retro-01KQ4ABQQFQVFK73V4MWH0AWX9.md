---
retro_id: retro-01KQ4ABQQFQVFK73V4MWH0AWX9
task_id: tsk-20260426-000003
run_id: run-01KQ4A7MGC9YPPV4ED7HEPMZ5C
skill: scout-systems
timestamp: '2026-04-26T07:16:35Z'
agent: claude-code/Shiftor/54804
actionable: true
confidence: medium
what_worked:
  - "class_hint=unicellular-organism pre-check resolved cleanly; no taxonomy
    gap, no review-records pairing, no --unblock-on-taxonomy condition.
    Same friction-free path as iteration 1's microbiome scout."
  - "Skill SKILL.md procedure step 4 (boundary, components, interactions,
    scales, canonical_examples >=3) is concrete enough that a same-domain
    scout completes in 2-3 minutes once the type-vs-instance choice is
    made."
  - "Scout-report.md `Notes on the cell-type axis` section captured a
    catalog-level observation (the prior prokaryotic-cell scout produced
    instance-level output; the cell-type axis is asymmetric) that's worth
    surfacing for a future plan-backlog re-seed without blocking this
    iteration."
blockers: []
proposed_improvements:
  - target: config/priority-systems.yaml
    change: >
      Re-seed `prokaryotic-cell` at the type level. The current
      prokaryotic-cell entry (with class_hint: unicellular-organism)
      produced a scout (tsk-20260424-000004) that emitted an
      *instance*-level profile-system task (tsk-20260425-000009 for
      *E. coli* K-12 MG1655, status: blocked on source-acquisition). The
      paired eukaryotic-cell scout this iteration produced a *type*-level
      profile-system task (tsk-20260426-000006 for the eukaryotic-cell
      archetype with S. cerevisiae / Tetrahymena / Chlamydomonas as
      canonical_examples). Add a follow-up entry to priority-systems.yaml
      explicitly requesting a type-level prokaryotic-cell archetype to
      balance the cell-type axis (or update the existing prokaryotic-cell
      entry's `notes` to clarify the type-level intent so future re-runs
      converge on the same shape). Without this, downstream observation
      and metric extraction will compare an instance (E. coli MG1655) on
      the prokaryote side against a type (eukaryotic-cell) on the
      eukaryote side, breaking like-with-like comparison.
    rationale: >
      The catalog's stated framing (AGENTS.md "What counts as a system
      worth cataloging") is type-level; instances belong in
      canonical_examples. The asymmetry between the two cell-type
      priority seeds was caused by ambiguous priority-seed framing
      ("Prokaryotic cells" -> a class_hint of unicellular-organism but
      no explicit type-level instruction in the entry's notes), and the
      first scout interpreted the seed as a request for a canonical
      example. An explicit `notes` clarification or a parallel type-level
      seed would prevent this divergence.
    severity: minor
  - target: skills/scout-systems/SKILL.md
    change: >
      Add a one-line note under "Procedure" step 4 (or under "Do not use
      this skill to: Surface specific instances") that when a priority
      seed names a *class*-level slug (e.g. `prokaryotic-cell`,
      `eukaryotic-cell`, `metabolic-network`), the emitted profile-system
      task should be type-level — naming the archetype as the system,
      with ≥3 instances populating canonical_examples — rather than
      naming a single instance as the system. The existing AGENTS.md
      "What counts as a system worth cataloging" guidance is correct but
      lives one layer up; surfacing it inline in the scout SKILL would
      have prevented the prokaryotic-cell vs eukaryotic-cell asymmetry.
    rationale: >
      Two scouts working from the same priority-systems.yaml structure
      converged on different shapes (instance vs type). The remediation
      lives in the layer the scout reads most directly (its own SKILL.md)
      rather than expecting the scout to cross-reference AGENTS.md
      mid-procedure.
    severity: minor
---

# Retrospective — tsk-20260426-000003 (scout-systems eukaryotic-cell)

Same friction-free shape as iteration 1's microbiome scout: priority-seed
named the slug, class_hint resolved, ≥3 canonical examples chosen, two
foundational sources cited. Profile-system task `tsk-20260426-000006`
emitted; scout-report.md and run.json written; inbox validates.

The scout uncovered an asymmetry on the cell-type axis: the prior
`prokaryotic-cell` priority-seed produced an instance-level profile-system
task (E. coli K-12 MG1655), while this iteration produced a type-level
eukaryotic-cell archetype. Two minor proposals: (a) update
`config/priority-systems.yaml` to clarify type-level intent on the
prokaryotic-cell entry (or re-seed it explicitly type-level), and (b) add
an inline note in `skills/scout-systems/SKILL.md` that class-level
priority-seed slugs map to type-level profile-system emissions, not to
canonical-example instances. Severity minor — the catalog can absorb the
asymmetry, and the eventual instance-level prokaryotic-cell entry can be
re-categorized as a canonical_example of a future type-level
prokaryotic-cell entry without data loss.
