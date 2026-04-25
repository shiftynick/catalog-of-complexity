---
retro_id: retro-01KQYXNH13BR4RFR438HE455Y9
task_id: tsk-20260425-000005
run_id: run-01KQY56KVNMTCKAJYZ2RYTKD7F
skill: review-records
timestamp: '2026-04-25T20:11:06Z'
agent: claude-code/Shiftor/48604
actionable: false
confidence: high
what_worked:
  - The task's reviewer guidance named the empirical example
    (tsk-20260425-000002 against taxonomy/source/system-classes.yaml whose
    proposals re-asked for atomic-system / molecular-system /
    chemical-reaction-network slugs already present) and called for a
    "narrow slug/key lookup, not a free-form judgement." That
    framing collapsed the ambiguity in "what counts as already-satisfied"
    — the edit became a small enumeration of two recognised forms (YAML
    items[].slug, JSON Schema named property/enum at indicated path) plus
    a defeat clause. No code path changed, only the apply-retros
    procedure prose.
  - Tier-0.75 source-debt sweep in preflight emitted three more
    acquire-source manifests for the highest-cross-task-count refs
    (isbn:9780471893844 ref-count 2, isbn:9780195096705 ref-count 2,
    doi:10.1038/msb.2011.65 ref-count 1). All three blocked
    profile-system tasks already carried unblock wiring of kind
    task-complete from the prior preflight, so the "leave existing
    unblock alone" idempotency rule fired exactly once each — no
    orphaned wiring, no multi-pass loop concerns this run.
blockers: []
proposed_improvements: []
---

# review-records: apply-retros already-satisfied skip rule

The task asked apply-retros to skip clusters whose every proposal asks
for a slug/key/value addition that already resolves in the target,
analogous to the existing ghost-target skip. The motivating evidence
(tsk-20260425-000002 against system-classes.yaml) was concrete enough
that the right shape was a narrow check, not a heuristic: enumerate
exactly two recognised forms (taxonomy `items[].slug`, JSON Schema
named property/enum at an indicated path) and require *every* proposal
in the cluster to match — any non-matching proposal defeats the skip.
That keeps the audit trail intact (contributing retros still get
`retro.consumed` per step 6) while freeing a max_clusters slot for
unsatisfied work. The narrow-form requirement also forecloses the
specific failure mode the manifest warned against: false-positive skips
on substantive content edits that happen to share a target file with a
trivial slug addition. Nothing surfaced that the existing layered
prompts didn't already cover. `actionable: false`.
