---
retro_id: retro-01KQ3EHNZ1SRT89CYF5HK3042J
task_id: tsk-20260425-000017
run_id: run-01kq3efw1c77xkfceqxcmtr8qv
skill: review-records
timestamp: '2026-04-25T23:14:30Z'
agent: claude-code/Shiftor/55232
actionable: false
confidence: high
what_worked:
  - 'Task manifest spelled out the three reviewer steps (status flip, notes.md Deprecation section, no file deletion) explicitly, leaving zero ambiguity for the agent — small but high-leverage manifest pattern for retire-instance review-records tasks.'
  - 'The replacement type slug `microbiome` already resolved in `taxonomy/source/system-classes.yaml` *and* was already queued in `config/priority-systems.yaml`, so the deprecation needed no taxonomy or priority-seed coordination — pre-staging the type-level slug before deprecating its instances is the right ordering.'
  - 'Pairing this deprecation with the rhizosphere companion (sys-000006, tsk-20260425-000020) keeps both microbiome instances retired against the same replacement type in the same run cycle — avoids leaving the catalog in a half-deprecated state where one instance lingers as the archetype.'
blockers: []
proposed_improvements: []
---

Iteration 1 of a multi-task autonomous run. The task was a clean
type-vs-instance deprecation per the AGENTS.md inclusion criterion: the
human gut microbiome is one specific host's gut community, not the
type. The edit was mechanical because the manifest enumerated steps and
the replacement slug was already in place.

Preflight unblocked tsk-20260423-000020 and tsk-20260424-000001 (their
DOI source-acquisition tasks completed last invocation), and the
Tier-0.75 sweep emitted three more acquire-source tasks for the
remaining uncovered ISBN refs (000029, 000030, 000031), wiring the
two blocked profile-system tasks (000008, 000009) to their respective
new acquisitions. Source debt for active tasks is now fully covered:
every prefixed `source_refs` entry across inbox/ready/leased/running/
blocked has either a registered source or an open acquire-source task.

No blockers, no proposed edits — the review-records skill, the manifest
template used by apply-retros for instance-not-type retirements, and
the AGENTS.md criterion read as well-aligned for this kind of task.
