---
retro_id: retro-01KQ37XTTBYTNPH49V1VEVRY03
run_id: run-01KQ37WJZTNX4PDEEAW7HR6Z1S
task_id: tsk-20260425-000006
skill: review-records
timestamp: '2026-04-25T21:14:30Z'
agent: claude-code/scheduled-run
actionable: true
confidence: high
what_worked:
  - 'The cluster-against-schema pattern delivered a clean implementation: schema enum addition + queue.py dispatch branch + 5 unit tests landed in one pass with the full pytest suite (78 tests) green and coc validate clean. The new `sources-resolved` kind reuses existing `find_existing_by_*` slug helpers verbatim, so the runtime addition is genuinely a dispatch-table extension rather than new infrastructure.'
  - 'Reading `REG_SOURCES` from the module namespace inside the resolver function (rather than capturing it as a default arg) makes monkeypatching trivial in tests. First test draft failed exactly because of the default-arg capture; the fix was a 2-line refactor and all 5 new tests passed on the next run. Worth remembering: any global-derived path that tests will swap should be looked up at call time, not at function definition time.'
  - 'Tier-0.75 preflight sweep continues to bear out the 0425-000001 thesis. This invocation found three previously-uncovered isbn refs from blocked/19 and blocked/20 (Bransden & Joachain, Griffiths & Schroeter, Szabo & Ostlund) and emitted three acquire-source tasks (000021/000022/000023). The skill''s idempotency rule ("Source debt: <ref>." note prefix) cleanly skipped the six refs already covered by 000010-000015.'
blockers:
  - 'Cluster output_targets vs. reviewer-guidance scope mismatch: the apply-retros cluster put `schemas/task.schema.json` as the single output_target, but the reviewer guidance in the same task notes explicitly authorized "schema + queue.py + tests." The autonomous executor honored the guidance to keep schema and runtime in sync — an enum-only change would have silently no-op''d for the new kind, and apply-retros'' "already-satisfied" skip would consume the cluster on a future pass without ever delivering the queue impl. Strict envelope reading would have blocked. The webUI prune review mechanism plus this retro''s explicit flag is the autonomous-policy''s post-hoc safety net here.'
proposed_improvements:
  - target: skills/apply-retros/SKILL.md
    change: 'When clustering by target, scan each clustered proposal''s `change` text for explicit references to other repo paths beyond the cluster target (regex `(schemas/|src/|skills/|tests/|prompts/)\S+`). When the clustered changes name N >= 2 distinct paths, expand the emitted review-records task''s `output_targets` to include all of them rather than only the cluster key. Document this as the "scope-honest output_targets" rule under Procedure step 5, between the cluster composition and the acceptance_tests step.'
    rationale: 'The cluster-by-target pattern picks one canonical target as the cluster key, but proposals frequently authorize work across multiple files (schema + impl + tests is the canonical tri-tuple). Today''s task is the empirical failure: output_targets listed only `schemas/task.schema.json`, but the reviewer guidance — and the proposal''s own change text — named queue.py and tests as part of the same deliverable. Expanding output_targets at apply-retros emission time keeps the envelope''s authorization boundary in sync with the actual scope of work, eliminating the recurring tension between "stop and report rather than expand scope" and "the cluster proposal cannot land without the impl edits." Severity moderate: today''s autonomous reading honored the broader scope, but the discipline-vs-deliverable tension will recur on every schema-with-impl cluster, and the stop-and-report path discards the apply-retros signal (the retro is already consumed) which is a real loss.'
    severity: moderate
  - target: skills/plan-backlog/SKILL.md
    change: 'Update Tier 0.75 blocked-task `unblock` wiring: when a blocked task''s `source_refs` are entirely composed of resolvable-class prefixes (`doi:`, `arxiv:`, `url:`, `src-*`), set `unblock: {kind: sources-resolved}` (no extra fields) instead of `{kind: task-complete, task_id: <last>}`. When any ref is `isbn:`, fall back to the existing task-complete-on-last wiring with a comment that sources-resolved isn''t yet usable for isbn-bearing tasks. Update the "Multi-source caveat" subsection to reflect that the loop now applies only to isbn-mixed tasks.'
    rationale: 'This is the explicit "after landing" follow-up flagged in retro-01KQ2DKYEME1BXMBXS0KAZRR3D''s rationale. The `sources-resolved` kind is now in the schema enum and queue.py implements it; plan-backlog Tier 0.75 should switch wiring on the all-resolvable-class case to eliminate the ⌈N/3⌉-pass convergence loop. The isbn caveat is real because acquire-source still blocks on isbn (per its SKILL.md "Block or fail when") and source.yaml has no isbn field — sources-resolved would never fire on an isbn-bearing task. Severity moderate: a latency win for the resolvable-class case; not a correctness fix.'
    severity: moderate
---

# Retrospective — run-01KQ37WJZTNX4PDEEAW7HR6Z1S (review-records)

Scheduled autonomous run. Iteration 1 of the new batched outer-loop. Preflight
ran cleanly (validate OK, git clean, advance promoted tsk-20260425-000006,
Tier-0.75 sweep emitted three acquire-source tasks for blocked/19+20 isbn
refs). Branch A leased tsk-20260425-000006 — a `review-records` cluster
targeting `schemas/task.schema.json` whose reviewer guidance explicitly named
`src/coc/queue.py` and `tests/test_queue.py` as part of the same deliverable.

The schema gains `sources-resolved` as a third unblock kind that introspects
the task's own `source_refs` (no extra subfield needed), dispatches by prefix
to `find_existing_by_doi/arxiv/url` for the prefixed forms and to
directory-existence for `src-*` ids, treats `isbn:` as unresolved (acquire-
source still blocks on isbn), and treats empty/missing `source_refs` as the
explicit-guard variant per the task's "vacuously true vs explicit guard"
acceptance test. queue.py's `_unblock_condition_met` signature now takes
`(spec, task_data)` and `sweep_blocked` passes the task dict through. Five
new tests in `tests/test_queue.py` cover all-resolved, some-resolved unresolved,
mixed `src-*`/prefixed forms, the empty-refs guard, and the isbn-never-resolves
case. Full pytest suite green (78 tests).

Two follow-ups flagged: apply-retros should learn to expand `output_targets`
when clustered proposals name multiple repo paths in their change text; and
plan-backlog Tier 0.75 should switch its blocked-task wiring to
`sources-resolved` for all-resolvable-class refs while keeping task-complete
fallback for isbn-bearing tasks until isbn resolution lands.
