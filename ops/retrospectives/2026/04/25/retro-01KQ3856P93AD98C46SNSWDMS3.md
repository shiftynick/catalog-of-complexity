---
retro_id: retro-01KQ3856P93AD98C46SNSWDMS3
run_id: run-01KQ384DB1ZZMREM72HA7NS97P
task_id: tsk-20260425-000007
skill: profile-system
timestamp: '2026-04-25T21:20:30Z'
agent: claude-code/scheduled-run
actionable: true
confidence: high
what_worked:
  - 'Ahead-of-execution duplicate detection via cross-reference between the leased task''s acceptance test (slug `belousov-zhabotinsky-reaction`, class `chemical-reaction-network`, identical source_refs triple) and the already-blocked tsk-20260424-000001 was decisive — failing fast on structural identity rather than re-running the profile prevents a slug clash and a wasted source-not-acquired re-block. The 2-minute wall-clock cost on this iteration is the entire price of the redundancy.'
  - 'Marking `failed` rather than `blocked` was the right terminal here. There is no waitable condition: the duplicate is already in flight, and the in-flight one will produce the canonical entry. blocked/ implies "could resume"; this task should not resume because re-running it would clash with the canonical entry. failed/ + a clear duplicate-of pointer in run.json gives a human reviewer the right context to archive.'
blockers:
  - 'Two independent Tier 0.5 priority-seed scouts (`chemical-reaction-network` and `autocatalytic-chemical-system`) converged on Belousov-Zhabotinsky as the canonical example. The second scout (tsk-20260424-000002) emitted a profile-system task whose acceptance test pinned the existing `chemical-reaction-network` class slug rather than the still-missing `autocatalytic-chemical-system` slug, producing a structural duplicate of tsk-20260424-000001 instead of a distinct profile. The convergence is not a bug in the scouts'' individual judgments — BZ is genuinely both a chemical-reaction-network and an autocatalytic chemical system — but it surfaces a scout-systems gap: nothing in Tier 0.5 checks whether a freshly-proposed candidate slug is already pinned by an in-flight task.'
proposed_improvements:
  - target: skills/scout-systems/SKILL.md
    change: 'Add a "Cross-task duplicate check" step to the scout-systems Procedure, executed after candidate selection and before emitting the profile-system task. Specifically: scan ops/tasks/{inbox,ready,leased,running,blocked}/*.yaml for any profile-system task whose acceptance_tests reference the same `sys-NNNNNN--<slug>` slug (or an equivalent slug under a different system-class taxonomy_ref). If a sibling task exists, do not emit a duplicate; instead, append a one-line note to the in-flight task''s `notes` ("Also priority-seeded by `<this-seed>` scout `<tsk-id>`") and record the convergence in the scout''s plan-report under a Convergences section. Block this scout with reason `candidate-already-pinned` rather than emit the duplicate.'
    rationale: 'Empirically demonstrated by today''s convergence: tsk-20260424-000002 (priority-seed `autocatalytic-chemical-system`) and tsk-20260423-000015 (priority-seed `chemical-reaction-network`) both selected BZ. The acceptance-test pin on the same class slug means the second scout''s output is structurally identical to the first scout''s, even though the priority seeds were different. Without a duplicate check, this convergence will recur for any system that legitimately fits multiple priority-seed entries (e.g. the priority list lists both `metabolic-network` and `microbiome` as biological seeds — many candidate biological systems fit both). The fix is a cheap pre-emission scan; the alternative is the current "fail fast at execution time" path which spends an iteration slot per duplicate. Severity moderate: the convergence rate scales with overlap in the priority list, and several upcoming biological/social seeds have similar overlap.'
    severity: moderate
  - target: skills/profile-system/SKILL.md
    change: 'Make the skill''s "Block or fail when" duplicate clause explicit about in-flight (not just on-disk) duplicates. Add a bullet under the existing "An existing non-deprecated sys-* record covers the same type" item: "...or a profile-system task currently in {inbox,ready,leased,running,blocked}/ targets the same canonical slug — block this task with status `failed` and note the duplicate in run.json. Do not wire an unblock condition; in-flight duplicates are not waitable."'
    rationale: 'Today''s task hit this case but the skill''s SKILL.md only enumerates on-disk duplicate records, not in-flight task duplicates. The correct action — fail with a duplicate-of pointer — was derivable from first principles, but explicit documentation prevents the next executor from speculating. Severity minor: this is documentation alignment to actual practice, not a behavior change.'
    severity: minor
---

# Retrospective — run-01KQ384DB1ZZMREM72HA7NS97P (profile-system, failed)

Iteration 2 of the batched scheduled run. Leased tsk-20260425-000007 (BZ
profile under priority-seed `autocatalytic-chemical-system`), discovered
within the first read pass that the acceptance test pins
`system-class:chemical-reaction-network` — exactly matching the already-
blocked tsk-20260424-000001's acceptance test, with identical source_refs
(doi:10.1021/ja00780a001, isbn:9780471893844, isbn:9780195096705).
Marked `failed` with reason `duplicate-task` and pointer to the canonical
in-flight task. tsk-20260424-000001 will produce the BZ entry once its
source_refs land via the acquire-source chain (tsk-20260425-000010, 000013,
000014).

The convergence surfaces a scout-systems Tier 0.5 gap: two priority seeds
that legitimately overlap on a candidate produce structurally identical
profile-system tasks. Flagged as a moderate proposal against
skills/scout-systems/SKILL.md (add cross-task duplicate check before
emission) and a minor doc-alignment proposal against
skills/profile-system/SKILL.md (clarify in-flight-duplicate handling).
