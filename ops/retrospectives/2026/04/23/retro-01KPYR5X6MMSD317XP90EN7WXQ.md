---
retro_id: retro-01KPYR5X6MMSD317XP90EN7WXQ
task_id: null
run_id: run-01KPYR5XAPPLYRETROS20260423A
skill: apply-retros
timestamp: '2026-04-23T17:55:00Z'
agent: claude-code/Shiftor/apply-retros
actionable: true
confidence: medium
what_worked:
  - >-
    Severity-floor + target-based clustering collapsed 7 moderate proposals
    from 5 different retros into a single review-records task against
    skills/profile-system/SKILL.md, exactly the de-duplication the skill is
    designed for. One cluster, one reviewer pass, instead of five.
  - >-
    The two independent themes against the same target (status enum
    mismatch, scales.organizational divergence) were kept as one cluster
    per the skill's "cluster by target" rule, which matches how a human
    reviewer will actually want to edit the file — a single touch.
blockers:
  - >-
    Emitted task manifests initially failed `coc validate` because
    acceptance_tests strings containing `` `status: active` `` were parsed
    as YAML mappings. Had to single-quote those list items. Low-cost to
    resolve but wastes a preflight cycle and could trip an agent without
    a quick feedback loop.
proposed_improvements:
  - target: skills/apply-retros/SKILL.md
    change: >-
      Add an explicit note in the Procedure (step 5) that when composing
      `notes` / `acceptance_tests` for the emitted review-records manifest,
      list items that embed YAML-ish colon pairs (e.g. `` `status: active` ``)
      must be single-quoted to avoid `mapping values are not allowed here`
      parse errors. Alternatively, recommend always quoting every
      acceptance_tests item as a defensive default.
    rationale: >-
      The first `coc validate` failed on a YAML-scanner-level error
      (retro-derived prose commonly contains `key: value` fragments as
      literal examples). A one-line warning in the skill would make this a
      zero-retry step for future apply-retros runs.
    severity: minor
---

Scheduled daily apply-retros run. Consumed 6 unconsumed in-window retros
(all 2026-04-23), emitted 2 review-records clusters (profile-system SKILL
cluster of 5 retros / 7 proposals, and queue.py single-proposal cluster),
skipped 5 minor proposals per `severity_floor=moderate`. No ghost targets.
Budget under 5 minutes vs. 10-minute allotment.
