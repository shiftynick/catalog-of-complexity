---
retro_id: retro-01KPXRCPGKKWC5YH5NBPXPE4W2
task_id: tsk-20260423-000008
run_id: run-01KPXR9W1EF1KWNJ76YGWBMNAT
skill: review-records
timestamp: 2026-04-23T18:08:00Z
agent: claude-code/opus-4.7
actionable: true
confidence: medium
what_worked:
  - Grounding the new canonical block against an already-validated example (tsk-20260423-000001.yaml) gave a concrete round-trip check — every clause in the new YAML maps to an output the skill already declares.
  - lint_skills.py + coc validate caught nothing new because the edit was content-only, which is the right signal for a doc-shape fix.
blockers: []
proposed_improvements:
  - target: skills/plan-backlog/SKILL.md
    change: In step 4 of §Procedure, link directly to the "Acceptance tests (canonical)" section anchor of each surfaced skill's SKILL.md, so the "pull the canonical shape" instruction names the exact section rather than the whole file.
    rationale: Now that one skill (scout-systems) exposes a labelled canonical block, plan-backlog's instruction becomes precise — but only for that one skill. Anchoring the instruction makes the missing-canonical-block state easier for future runs to detect and propose filling.
    severity: minor
  - target: skills/profile-system/SKILL.md
    change: Add an "## Acceptance tests (canonical)" section mirroring the shape added to scout-systems — a verbatim-copyable `acceptance_tests:` YAML block grounded in the skill's Procedure/Output-shape clauses.
    rationale: profile-system is on plan-backlog's AUTO_PROMOTE list and will be proposed the same way scout-systems was; without a canonical block, plan-backlog has to reformulate acceptance tests every run — the exact issue the parent task fixed for scout-systems.
    severity: minor
  - target: skills/define-metrics/SKILL.md
    change: Same edit as profile-system — add a canonical acceptance_tests block.
    rationale: Same reasoning.
    severity: minor
  - target: skills/extract-observations/SKILL.md
    change: Same edit as profile-system — add a canonical acceptance_tests block.
    rationale: Same reasoning.
    severity: minor
  - target: skills/review-records/SKILL.md
    change: Same edit as profile-system — add a canonical acceptance_tests block (noting the record_scope variance — observations/systems/metrics/sources — may require a small set of templates rather than one).
    rationale: Same reasoning, with the caveat that review-records has polymorphic scope and may need 2-3 template variants.
    severity: minor
---

This run landed the canonical `acceptance_tests` block in
`skills/scout-systems/SKILL.md`, closing the retro cluster behind
tsk-20260423-000008. The main learning: the fix generalizes. Four
sibling skills (profile-system, define-metrics, extract-observations,
review-records) all sit on plan-backlog's AUTO_PROMOTE list and will
re-exhibit the same "fabricated acceptance tests" symptom on their
next proposal unless they also publish canonical blocks.

The parent task scoped itself to scout-systems only and forbade
bulk-editing in-task; `output_targets` enforced that. Proposals above
name concrete targets and are minor-severity each — no single follow-up
task is emitted from this retro. plan-backlog (or a human) can cluster
them into one `review-records` task on a later run.
