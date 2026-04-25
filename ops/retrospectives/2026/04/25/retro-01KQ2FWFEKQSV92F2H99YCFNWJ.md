---
retro_id: retro-01KQ2FWFEKQSV92F2H99YCFNWJ
run_id: run-01KQ2FQ06WYWBDH1E37WHQJEER
task_id: tsk-20260424-000002
skill: scout-systems
timestamp: '2026-04-25T14:16:00Z'
agent: claude-code/Shiftor/scout-systems
actionable: true
confidence: medium
what_worked:
  - 'Mapping the priority-seed slug `autocatalytic-chemical-system` to the existing `system-class:chemical-reaction-network` was unambiguous because the taxonomy description for that class explicitly names the Belousov–Zhabotinsky oscillator as a canonical example. The leased task notes invited this kind of mapping ("let scout-systems map to an existing class or queue a taxonomy review task if needed"), which kept the scout from reflexively emitting a taxonomy proposal when the existing class already covered the system. No taxonomy gap, no auto-unblock plumbing.'
  - 'Following the hydrogen-atom precedent (run-01KPYJPT1VNKWSNTA6XNE82EMZ) of recording candidate metrics in the scout-report Follow-ups section instead of emitting `define-metrics` tasks inline kept this run inside its budget-1 envelope and respected the auto-promote per-type cap of 3 on `define-metrics`. The metrics list in the report gives the next plan-backlog Tier-4 sweep a concrete starting point.'
  - 'The five rejected candidates (Brusselator, iodate–arsenous-acid, Briggs–Rauscher, formose, CIMA) each have a *specific* tie-break rationale (model-not-system, non-oscillatory, BZ derivative, contested mechanism, pattern-specialist) rather than blanket "out of scope". This anchors what a future second-CRN scout should prefer.'
blockers: []
proposed_improvements:
  - target: skills/scout-systems/SKILL.md
    change: |
      Add a short note under Procedure step 4 documenting the
      "priority-seed-slug-without-same-named-class" pattern: when the
      priority-seed slug from config/priority-systems.yaml does not
      itself resolve as a `system-class:*` slug, but an existing
      class subsumes it (named in that class's taxonomy
      description), the correct move is to map the candidate to the
      existing class rather than emit a taxonomy-proposal — and to
      record the mapping rationale in the scout-report's "Taxonomy
      gaps" section as "None blocking; mapped to <existing-class>"
      so future readers can audit the choice.
    rationale: |
      The leased task's notes invited this mapping explicitly, but
      the SKILL.md procedure does not document the pattern. Today
      it relies on the agent reading the manifest's notes carefully
      and on the reviewer noticing the taxonomy description. A
      one-paragraph note would make the pattern reproducible
      without the manifest hint, and would prevent a future scout
      under similar circumstances from defaulting to a redundant
      taxonomy proposal. Severity minor — the current path works,
      but the institutional knowledge is fragile.
    severity: minor
  - target: config/priority-systems.yaml
    change: |
      Add an optional `class_hint` to the
      `autocatalytic-chemical-system` entry pointing at
      `chemical-reaction-network`, mirroring the pattern documented
      in skills/plan-backlog/SKILL.md for resolved hints. The hint
      would short-circuit any future re-emission of this seed (none
      is needed now that the BZ profile-system is queued, but the
      curation pattern matters).
    rationale: |
      The minor curation backlog item already noted in
      retro-01KQ2DKYEME1BXMBXS0KAZRR3D ("backfill `class_hint` on
      existing config/priority-systems.yaml entries") would also
      benefit from the case in hand: this entry is now provably
      mappable to chemical-reaction-network. Bundling this single
      additional row into the deferred class_hint backfill task
      keeps the change small. Severity minor — purely a curation
      improvement; no run was blocked by its absence.
    severity: minor
---

# Retrospective — run-01KQ2FQ06WYWBDH1E37WHQJEER (scout-systems)

Tier-0.5 priority-seed scout for `autocatalytic-chemical-system` in
the physical domain, budget 1. Outcome: one `profile-system` task
emitted for the Belousov–Zhabotinsky reaction
(tsk-20260425-000007), mapping cleanly to the existing
`system-class:chemical-reaction-network` slug. No taxonomy proposal
required.

The most interesting decision was the seed-slug-vs-class-slug
mapping. The priority-seed name "autocatalytic-chemical-system"
suggests a class slug of the same name might be expected, but the
existing `chemical-reaction-network` class explicitly names BZ as a
canonical example, so emitting a redundant taxonomy proposal would
have inflated the queue without payoff. The leased task notes
called this out ("let scout-systems map to an existing class or
queue a taxonomy review task if needed"), which is exactly the
forward-compatible hint the SKILL.md should also carry — see
proposed_improvements.

Both proposals are minor. The scout itself ran cleanly inside ~5
minutes wall-clock, no heartbeats needed (sub-cadence run). One
follow-on signal worth flagging for the next plan-backlog pass:
tsk-20260425-000007 carries 3 prefixed `source_refs` (1 doi, 2
isbn), exactly matching the Tier-0.75 acquire-source per-pass cap
of 3, so a single Tier-0.75 pass should fully resolve the source
debt before the profile-system task next runs. The pending
`sources-resolved` unblock kind (tsk-20260425-000006) would close
the loop one pass earlier when it lands.

`actionable: true` — both proposals name concrete files, both have
small surface area, and neither would block the run if deferred.
`confidence: medium` — the SKILL.md edit would generalize the
mapping pattern, but the test set is N=1 today; better to accept
that this is a "document-the-pattern-now" edit rather than a load-
bearing process change.
