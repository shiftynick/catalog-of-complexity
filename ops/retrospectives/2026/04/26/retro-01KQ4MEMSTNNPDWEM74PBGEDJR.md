---
retro_id: retro-01KQ4MEMSTNNPDWEM74PBGEDJR
task_id: tsk-20260426-000005
run_id: run-01kq4magpv3m2qhc6pk8p4j627
skill: profile-system
timestamp: '2026-04-26T10:14:00Z'
agent: claude-code/auto
actionable: false
confidence: high
what_worked:
  - Tier-0.75 source-debt sweep idempotency check (notes-prefix grep across ops/tasks/) cleanly distinguished the 4 still-open prefixed refs from the 7 already covered by blocked acquire-source tasks; emitted 3 of 4 within the per-pass cap and deferred doi:10.1186/1745-6150-5-7 to the next pass.
  - sources-resolved unblock kind on tsk-20260426-000005 made the Branch-A pickup deterministic - both anchor sources (src-000010, src-000011) had landed in prior runs, so coc advance moved the task ready/ before this run.
  - profile-system stop_conditions plus the manifest's specific acceptance_tests (boundary/components/interaction_types/scales populated, canonical_examples >=3, links cite >=2 sources) gave a tight checklist; produced sys-000007--microbiome with 7 canonical_examples and link to two registered sources without judgment-call gaps.
blockers: []
proposed_improvements: []
---

Profiled the type-level microbiome archetype as sys-000007--microbiome with
status profiled, taxonomy_refs system-domain:biological + system-class:microbiome,
two registered source citations, and seven canonical examples spanning
host-associated and environmental microbiomes. The task's manifest captured
nearly all the structural fields verbatim from the scout output, so the run was
a transcription-and-validation exercise rather than a judgment-call exercise.
The Tier-0.75 sweep also emitted three acquire-source tasks for the
gene-regulatory-network anchor sources so the next ready/profile task
(tsk-20260426-000011) won't lease and immediately re-block on
source-not-acquired. One components entry initially used a YAML "cardinality:"
key that schema-rejected as a mapping rather than a string; reflowed to prose.
No skill or schema friction beyond that minor authoring slip.
