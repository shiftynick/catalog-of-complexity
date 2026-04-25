---
retro_id: retro-01KQ2K10B77BHEVK8HPBQ54KN9
run_id: run-01KQ2JWGWT64SVHTGX7DKFH7EF
task_id: tsk-20260424-000003
skill: scout-systems
timestamp: '2026-04-25T15:09:46Z'
agent: claude-code/Shiftor/scout-systems
actionable: true
confidence: medium
what_worked:
  - 'Choosing E. coli K-12 MG1655 as the metabolic-network seed required no judgment beyond reading the taxonomy entry: `system-class:metabolic-network` already cites Jeong et al. 2000 (γ ≈ 2.2 across 43 organisms, E. coli among them) and Palsson 2015 (E. coli is the textbook''s primary case study). The taxonomy''s own references pre-grounded the scout decision, which made yeast/human/Mycoplasma deferrals defensible without a separate prioritisation framework. This is a generalisable pattern: a class with well-chosen reference citations *is* a built-in scout heuristic.'
  - 'The `unblock: {kind: taxonomy-slug-exists, taxonomy_ref: system-class:metabolic-network}` clause on the manifest was defensive — the slug had been added on 2026-04-23 (commit 69c6bf5), well before the manifest was created on 2026-04-24. The clause did no work this run, but its presence costs nothing and means a future plan-backlog seed for an as-yet-unrealized class slug can use the same shape and auto-resume the moment a `review-records` taxonomy edit lands. Defensive `unblock` on scout manifests is cheap and worth keeping by default.'
  - 'Followed the BZ scout retro''s pattern (retro-01KQ2FWFEKQSV92F2H99YCFNWJ) of recording candidate metrics in the scout-report''s `Follow-ups` section rather than emitting `define-metrics` tasks inline. Five metrics surfaced (γ, stoichiometric-matrix rank, FBA µ_max, reversibility fraction, gene-essentiality fraction); none was emitted as a task this run. This kept the run inside its budget-1 envelope and respected the auto-promote per-type cap of 3 on `define-metrics`. The list is concrete enough to be picked up by the next plan-backlog Tier-4 sweep without rediscovery.'
blockers: []
proposed_improvements:
  - target: skills/scout-systems/SKILL.md
    change: |
      Update Procedure step 4.4 and step 6 to codify the "defer
      define-metrics emission to scout-report Follow-ups" pattern.
      Concretely: replace step 6 ("Emit one `define-metrics` task per
      novel candidate metric into `ops/tasks/inbox/`") with a
      conditional — emit `define-metrics` tasks inline only when the
      manifest budget exceeds 1 *and* fewer than 3 `define-metrics`
      tasks currently sit in `ready/` (the auto-promote cap),
      otherwise record candidate metrics in the scout-report's
      `Follow-ups` section under a `Candidate metrics flagged for
      define-metrics tasks but not emitted this run` heading and let
      the next `plan-backlog` Tier-4 (metric-debt) sweep pick them
      up. Two consecutive scout retros (BZ on 2026-04-25 and this
      one) have independently chosen the deferral path; SKILL.md
      currently still reads as if inline emission is the default,
      which leaves the choice load-bearing on agent judgment.
    rationale: |
      The deferral pattern is now a documented two-shot precedent
      (BZ retro proposed it, this run followed it without rediscovery
      thanks to that retro's report being on disk). Codifying it
      removes the "did I read the prior retro?" dependency and makes
      the scout reproducible across agents who haven't seen the
      precedent. The conditional ("only emit inline when budget > 1
      and the cap has headroom") preserves the original step-6
      behaviour for genuinely-broad scouts. Severity moderate — not
      blocking, but every future scout makes the same micro-decision
      and the SKILL.md should resolve it once.
    severity: moderate
  - target: skills/scout-systems/SKILL.md
    change: |
      Add a one-paragraph note under "Preconditions" or as a new
      "Defensive unblock clauses" subsection under Procedure step 5
      recommending that every scout-systems task manifest emitted
      with a *targeted* `system-class:` slug carry a defensive
      `unblock: {kind: taxonomy-slug-exists, taxonomy_ref:
      system-class:<slug>}` clause, even when the slug already
      exists at manifest-creation time. Rationale to include in the
      note: the clause is a no-op in the common case, but if a
      taxonomy edit removes or renames the slug between manifest
      creation and lease, the scout would otherwise fail in a way
      that requires manual rescue rather than auto-resuming on the
      next `coc advance`.
    rationale: |
      The leased manifest for this run carried the clause and the
      pattern survived the run unchanged. plan-backlog already emits
      these by default for blocked-on-taxonomy seeds; SKILL.md should
      document the defensive variant explicitly so a non-plan-backlog
      author (e.g. a human writing a one-off scout manifest) reaches
      the same shape. Severity minor — purely a robustness/curation
      improvement.
    severity: minor
---

# Retrospective — run-01KQ2JWGWT64SVHTGX7DKFH7EF (scout-systems)

Tier-0.5 priority-seed scout for `system-class:metabolic-network` in
the biological domain, budget 1. Outcome: one `profile-system` task
emitted (`tsk-20260425-000008`) for the *Escherichia coli* K-12
MG1655 metabolic network, anchored in Orth et al. 2011 (iJO1366),
Jeong et al. 2000 (the scale-free analysis cited by the taxonomy
class itself), and Palsson 2015. No taxonomy proposal required.

The most useful observation from this run: the
`system-class:metabolic-network` taxonomy entry's own `references`
list is already a scout heuristic — the two papers it cites name E.
coli explicitly, so the alternatives (yeast Yeast8, human Recon3D,
Mycoplasma minimal genome, methanogen/cyanobacterial autotrophs,
cancer-cell-line variants) deferred themselves without needing a
separate prioritisation rubric. That is general: investing in the
`references` list when authoring a taxonomy class pays off later
because scouts under that class inherit the prioritisation.

The defensive `unblock: taxonomy-slug-exists` clause on the manifest
did no work this run (the slug existed on 2026-04-23, manifest was
written 2026-04-24), but its presence is cheap insurance and worth
documenting as the default pattern — see the second proposed
improvement.

The candidate-metrics deferral followed the BZ scout retro's
precedent: five metrics (degree exponent γ, stoichiometric-matrix
rank, FBA µ_max, reversibility fraction, gene-essentiality
fraction) were recorded in the scout-report's `Follow-ups` section
rather than emitted as `define-metrics` tasks. With two consecutive
scout retros independently choosing the same path, the proposed
SKILL.md edit (severity moderate) is to make this the documented
default with an explicit conditional for the inline-emission case.

`actionable: true` — both proposals name concrete files. Severity
moderate on the deferral codification (it shapes every future scout
run), minor on the defensive-unblock note (purely a curation
improvement). `confidence: medium` — the deferral pattern has a
two-shot history, which is enough to codify but worth marking as
"document the precedent" rather than "load-bearing process change".
