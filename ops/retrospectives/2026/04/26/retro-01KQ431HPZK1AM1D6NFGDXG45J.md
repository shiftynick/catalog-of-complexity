---
retro_id: retro-01KQ431HPZK1AM1D6NFGDXG45J
task_id: tsk-20260426-000001
run_id: run-01KQ430E3XVAX9TZJ9A02YS27S
skill: review-records
timestamp: 2026-04-26T05:09:00Z
agent: claude-code
actionable: true
confidence: medium
what_worked:
  - "Three new tests landed cleanly using the existing _fetcher_from_map helper — same pattern as the Crossref/arXiv happy-path tests, no new fixtures or mocks needed."
  - "Acceptance test wording was specific enough (Google Books volumes shape, `{kind: books#volumes, totalItems: 0}` for empty, `ISBN:<isbn>` keyed entry for Open Library) that no schema reading was needed mid-implementation."
  - "Tier-0.75 idempotency rule held: 8 unregistered ISBN refs detected, all already covered by prior `Source debt:` tasks → no duplicate acquire-source emission."
blockers: []
proposed_improvements:
  - target: skills/acquire-source/SKILL.md
    change: "Document a follow-up cycle for `Source debt:` tasks that previously blocked as `unsupported-ref` (no resolver) but whose ref-kind now has a resolver. Either (a) define an `unblock` condition that fires when a new resolver lands so prior unsupported-ref blocks auto-retry, or (b) extend Tier-0.75 idempotency to allow re-emission when the existing source-debt task terminated as `unsupported-ref` and a resolver has since been added."
    rationale: "Current state: 8 ISBN refs are stranded — they have prior `Source debt:` tasks that blocked as `unsupported-ref` before the isbn_books resolver landed (commit bd0cf57). Tier-0.75 idempotency now skips them forever, but the resolver can handle them. Without an automatic re-trigger, those refs stay unregistered until a human re-emits acquire-source tasks. The same trap will spring on every future resolver addition (e.g. handle/, hdl:, future preprint servers)."
    severity: moderate
  - target: skills/review-records/SKILL.md
    change: "Add a short note that review-records tasks may be used to fix stale tests in `tests/` when a prior task's `output_targets` did not include the test file — call out the pattern so the next agent does not need to re-derive that this is in scope."
    rationale: "This task and the DataCite-resolver retro both flagged the same scoping pattern: a resolver task could not touch tests because tests/ was outside its output_targets, requiring a follow-up review-records task. Documenting this makes the pattern visible and reduces the chance of repeated retros surfacing the same friction."
    severity: minor
---

Single-iteration review-records follow-up. The acceptance tests in the manifest were precise (specific URL shapes, payload keys, expected ResolvedSource fields), so the implementation reduced to: add the `isbn_books` import, replace one stale test with three new ones using the existing fake-fetcher pattern, run pytest. All 16 tests passed on the first run.

The Tier-0.75 sweep finding — 8 ISBN refs newly resolvable but stuck behind idempotency — is the more interesting signal. The autonomous loop introduced an asymmetry: the source-debt mechanism is one-shot per ref, but resolver capability is monotonic. The skill needs a way to retry when the capability surface grows.
