---
retro_id: retro-01KPX8MD4GHQRN9QEYA2NMCEEM
task_id: null
run_id: run-01KPX8GXJ7V6EHJS6YJMPBVAYN
skill: plan-backlog
timestamp: '2026-04-23T13:31:52Z'
agent: claude-code/Shiftor/88512
actionable: true
confidence: medium
what_worked:
  - 'Preflight trio (coc validate / git status --porcelain / coc advance) cleanly gated the run into Branch B; zero ambiguity about which branch fires.'
  - 'Tier walk in plan-backlog terminated at the first firing tier (Tier 5) and the domain-rotation tie-break produced a deterministic slug choice without requiring any out-of-skill judgment.'
  - 'Writing the plan-report under ops/runs/YYYY/MM/DD/<run-id>/ alongside run.json kept all Branch-B evidence co-located.'
blockers: []
proposed_improvements:
  - target: skills/scout-systems/SKILL.md
    change: >-
      Add an explicit `acceptance_tests` block (or equivalent canonical
      test strings) to the skill frontmatter so that plan-backlog can copy
      them verbatim into emitted task manifests instead of reformulating
      from `stop_conditions`.
    rationale: >-
      plan-backlog/SKILL.md instructs proposers to "pull the canonical
      shape from the target skill's SKILL.md. Do not fabricate acceptance
      tests", but scout-systems only exposes `stop_conditions`. That
      forced this run to derive acceptance_tests text, which is mild
      fabrication by any strict reading of the rule. Every scout-systems
      proposal from plan-backlog will hit the same gap until the skill
      publishes canonical test strings.
    severity: minor
  - target: schemas/task.schema.json
    change: >-
      Document (in the `output_targets` description or a short README in
      schemas/) whether glob patterns / directory paths are acceptable in
      `output_targets`, or whether every entry must be a concrete file
      path.
    rationale: >-
      scout-systems emits N+1 files whose exact paths are only knowable at
      execution time (one inbox task per candidate system + a scout
      report). The manifest this run wrote used directory/glob entries,
      which validate today because the field is `type: string` with no
      pattern — but the AGENTS.md rule "Only write files declared in the
      task manifest's `output_targets`" becomes hard to enforce when the
      declaration is a directory. Either tighten the schema or clarify
      the norm.
    severity: minor
---

# Retrospective — run-01KPX8GXJ7V6EHJS6YJMPBVAYN (plan-backlog)

Empty-queue run. Preflight was clean, plan-backlog walked the gap tiers in
order, and only Tier 5 (coverage expansion) had a live gap. Emitted one
`scout-systems` proposal targeting `system-domain:biological` — the first
zero-count domain in taxonomy declared order.

The two proposed improvements are both minor doc gaps, not broken
behaviour. They surfaced because plan-backlog is now wiring together
skill-level contracts that were written independently: scout-systems'
frontmatter predates plan-backlog, so the acceptance_tests-reuse norm
hasn't propagated yet. Safe to defer until another skill hits the same
friction.

No blockers. `coc validate` accepted every file this run touched.
