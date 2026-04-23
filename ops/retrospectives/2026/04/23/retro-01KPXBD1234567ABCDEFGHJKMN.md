---
retro_id: retro-01KPXBD1234567ABCDEFGHJKMN
task_id: tsk-20260423-000001
run_id: run-01KPXBD00000A1B2C3D4E5F6G7
skill: scout-systems
timestamp: '2026-04-23T14:32:30Z'
agent: claude-code/Shiftor/108016
actionable: true
confidence: medium
what_worked:
  - 'Preflight (coc validate / git status --porcelain / coc advance) promoted tsk-20260423-000001 cleanly; Branch A fired without contention.'
  - 'The scout-systems stop_conditions plus profile-system SKILL preconditions together specified enough that five biological candidates fit existing taxonomy slugs without any invention pressure — two microbiome instances (gut and rhizosphere) were justifiable without forcing a new class.'
  - 'Recording deferred taxonomy gaps in the scout report (rather than filing speculative taxonomy-proposal tasks) preserved the budget (5 candidates) and respected the "do not invent slugs" block-condition, while leaving a clear trail for a future plan-backlog or human pass.'
blockers: []
proposed_improvements:
  - target: schemas/task.schema.json
    change: >-
      Document and (eventually) constrain the `source_refs` field. Define a
      small set of accepted prefixes for unregistered sources (e.g.
      `doi:`, `isbn:`, `url:`, `arxiv:`) and keep `src-NNNNNN--slug` for
      registered sources. Today the field is an unconstrained string, so
      this run picked a convention that seems right but isn't canonical.
    rationale: >-
      scout-systems emits proposals whose sources are not yet in
      registry/sources/. profile-system/SKILL.md says "At least one source
      is either already in registry/sources/ or listed in the task
      manifest for acquisition", which implies DOIs in manifests are
      acceptable, but the format isn't specified anywhere. Without a
      canonical prefix set, different agents will drift (doi:10.x vs
      https://doi.org/10.x vs bare 10.x) and the downstream matcher that
      eventually resolves these into registered sources will need
      per-case cleanup.
    severity: minor
  - target: taxonomy/source/system-classes.yaml
    change: >-
      Consider adding three classes surfaced as gaps during the biological
      domain scout: `unicellular-organism` (prokaryotes and single-celled
      eukaryotes, distinct from `multicellular-organism`),
      `metabolic-network` (biochemical reaction graphs inside a single
      cell), and `superorganism` (eusocial colonies and clonal colonies
      treated as the unit of selection). Each is a review-records /
      taxonomy-proposal task, not an inline edit — filing here as a
      heads-up rather than invoking the severity-major follow-up path.
    rationale: >-
      The biological domain is taxonomically rich; four existing classes
      (microbiome, immune-system, multicellular-organism,
      central-nervous-system) left three of the eight shortlisted
      candidates this run un-slottable. Future biological-domain scouts
      will keep hitting the same gaps. Queuing the proposals eventually
      unblocks unicellular-organism (e.g. E. coli) and superorganism
      (e.g. ant colonies) candidates that are otherwise well-supported
      in the literature.
    severity: moderate
  - target: prompts/autonomous-run.md
    change: >-
      Clarify in Branch A step 4 ("Heartbeat every 15 minutes") whether a
      sub-15-minute run should emit any heartbeats at all, or whether the
      first heartbeat can be skipped when wall-clock elapsed is under
      the interval. This run completed in ~16 minutes and emitted zero
      heartbeats, which is consistent with a strict reading of the rule
      but leaves the `heartbeats: 0` field in run.json looking anaemic
      against the 90-min TTL budget.
    rationale: >-
      The watchdog contract ties heartbeats to `ttl_minutes / 3` (30 min
      for the default 90-min TTL). A fast scout run has no liveness
      signal problem, but "every 15 minutes of wall-clock work" is
      tighter than the watchdog needs. Either relax the cadence in the
      prompt to match the watchdog, or add a sentence clarifying that
      runs shorter than the cadence can omit heartbeats. Minor because
      it has no reliability impact today.
    severity: minor
---

# Retrospective — run-01KPXBD00000A1B2C3D4E5F6G7 (scout-systems)

First Branch A run for this repo: scout-systems against the
biological-domain coverage gap. Preflight was clean, the skill's stop
condition (five candidates with ≥1 source_ref each, all slugs resolving)
fit the existing taxonomy exactly, and validation passed on the emitted
inbox manifests plus the run report.

The only non-trivial judgment calls were (a) deciding that two
`system-class:microbiome` instances are legitimate when the specific
systems differ in host / scales / selective pressures, and (b) deferring
three taxonomy gaps (unicellular-organism, metabolic-network,
superorganism) as notes-only rather than filing speculative
taxonomy-proposal tasks. Both decisions are recorded in the scout report
so a reviewer can re-examine them.

Two of the three proposals (source_refs convention; taxonomy class
additions) will affect every future scout of a biological domain; the
heartbeat-cadence proposal is cosmetic. Confidence medium: the
source_refs proposal is clearly right, but the taxonomy-class proposals
deserve a human pass before landing in `taxonomy/source/`.
