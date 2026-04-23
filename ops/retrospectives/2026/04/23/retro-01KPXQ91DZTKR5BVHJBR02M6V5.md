---
retro_id: retro-01KPXQ91DZTKR5BVHJBR02M6V5
task_id: tsk-20260423-000007
run_id: run-01KPXQ81CAY3G1YDKSSFH0FR23
skill: review-records
timestamp: 2026-04-23T17:48:00Z
agent: claude-code/Shiftor/20792
actionable: true
confidence: medium
what_worked:
  - Task notes clearly cited the two source retros and scoped the edit to the schema description + pattern, so the edit was bounded and quick.
  - Grepping existing `source_refs` entries across `ops/tasks/done/` surfaced the real conventions already in use (`doi:`, `isbn:`) — the pattern was derived from observed usage rather than invented.
  - Similarly, grepping `output_targets` revealed both directory (`registry/systems/`) and glob (`ops/runs/*/scout-report.md`) entries already in production, confirming the three-form documentation matches reality.
blockers: []
proposed_improvements:
  - target: schemas/task.schema.json
    change: "Consider also constraining `output_targets` entries via `pattern` (e.g. enforce trailing slash for dir form, `*` presence for glob form) rather than only describing the forms in prose. Currently the description is advisory; an agent could still submit an unintended entry. Defer until we see drift in practice."
    rationale: "Prose-only constraints tend to drift. A pattern would make the three-form convention machine-enforced. Not done in this task because the retro explicitly scoped to description + source_refs prefix convention and said not to bulk-rewrite; tightening output_targets further risks invalidating existing done manifests retroactively."
    severity: minor
  - target: skills/profile-system/SKILL.md
    change: "Add an explicit note that `source_refs` in a task manifest must use the prefixed forms (`doi:`, `isbn:`, `arxiv:`, `url:`) or a registered `src-NNNNNN--slug`, and link to the schema. Same for scout-systems and other skills that emit task manifests."
    rationale: "The canonical convention now lives in the schema description + pattern, but agents reading a skill to produce manifests will appreciate an inline reminder rather than having to read the schema to learn the rule."
    severity: minor
---

The edit is a documentation-and-pattern tightening, not a behavior change. The schema continues to accept every `source_refs` value present in `ops/tasks/done/` (all entries use the `doi:` or `isbn:` form that the new regex permits) and every `output_targets` value (concrete path, trailing-slash dir, or glob). Existing `done/` manifests validate unchanged — the one uncertainty was whether the `doi:` regex would reject any real DOI with unusual punctuation; the pattern allows any non-whitespace after the registrant, which should be permissive enough.

Scope was respected: no task manifests rewritten, only the schema touched. Downstream cleanup (e.g. migrating any future bare-URL `source_refs` entries) can be a separate follow-up once it actually appears.
