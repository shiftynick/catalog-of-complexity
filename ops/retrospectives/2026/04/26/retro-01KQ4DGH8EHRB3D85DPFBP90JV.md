---
retro_id: retro-01KQ4DGH8EHRB3D85DPFBP90JV
task_id: tsk-20260426-000005
run_id: run-01KQ4DDRTQHHNYZW8NVGKPJVXJ
skill: profile-system
timestamp: '2026-04-26T08:14:00Z'
agent: claude-code/Shiftor/22079
actionable: true
confidence: medium
what_worked:
  - 'Tier-0.75 source-debt sweep at preflight correctly flagged all 4 unfulfilled prefixed refs across the freshly-promoted profile-system pair (microbiome, eukaryotic-cell), emitted 3 acquire-source tasks under the per-pass cap, and validated cleanly. The cap-3 design held: the 4th ref (doi:10.1186/1745-6150-5-7 for Cavalier-Smith 2010) defers naturally to the next plan-backlog pass without requiring special-case logic here.'
  - 'The schema-supported `unblock.kind: sources-resolved` collapses the multi-source unblock loop documented in plan-backlog Tier 0.75 (multi-source caveat) into one condition. Manually setting it on the leased manifest before `coc complete --state blocked` was clean and survived the rename — `complete_task` preserves arbitrary top-level fields.'
  - 'Identifying the block point was mechanical: acceptance test 2 explicitly named the two prefixed-form anchor DOIs and required them in links.yaml, so the source-not-acquired clause in profile-system SKILL.md `Block or fail when` fired without judgment.'
blockers: []
proposed_improvements:
  - target: src/coc/cli.py
    change: 'Add `--unblock-on-sources` flag (no value required) to `coc complete`, mirroring the existing `--unblock-on-taxonomy` and `--unblock-on-task` flags. When set with `--state blocked`, write `unblock: {kind: sources-resolved}` onto the leased manifest before the terminal move. Also update the mutually-exclusive check at cli.py:84 to a three-way ladder.'
    rationale: 'The schema (schemas/task.schema.json) and runtime (`_all_sources_resolved` in src/coc/queue.py:362) both support `kind: sources-resolved`, but the CLI does not surface it. Agents wanting this kind today must edit the leased manifest manually with a yaml round-trip — the workaround used in this run. For profile-system / extract-observations tasks with multiple prefixed source_refs, sources-resolved is strictly cleaner than the per-task `--unblock-on-task` loop documented in plan-backlog Tier 0.75 multi-source caveat (which converges in ⌈N/3⌉ plan-backlog passes vs. 1 sweep). Surfacing the flag closes the gap and removes the documented multi-pass loop as the typical path.'
    severity: moderate
  - target: skills/plan-backlog/SKILL.md
    change: 'Tier 0.75 step "Unblock wiring for blocked tasks": when a blocked task has N>1 missing prefixed refs, prefer `unblock: {kind: sources-resolved}` over the documented "wire to the last acquire-source task emitted in this pass + multi-pass loop" approach. The `sources-resolved` kind covers all listed source_refs in one condition. Keep the per-task `task-complete` wiring as the fallback when only one ref is missing (where it is equivalent and matches the existing convention used by tsk-20260425-000011..000031).'
    rationale: 'The Tier 0.75 procedure was authored before the `sources-resolved` unblock kind was added to the schema (visible in queue.py:393 and the existing schema enum). The documented multi-pass loop is no longer the simplest converging path. Updating the skill keeps the documentation aligned with the schema/runtime capability and preempts future agents reaching for the older pattern out of habit.'
    severity: minor
---

Iteration 1 of this invocation. Preflight ran cleanly: validate OK, tree
clean, `coc advance` promoted three freshly-seeded tasks
(tsk-20260426-000005/000006/000007), and the Tier-0.75 sweep emitted three
new `acquire-source` tasks (tsk-20260426-000008/000009/000010) for the
prefixed DOIs/ISBN backing the two ready profile-system tasks. The 4th
unfulfilled ref (Cavalier-Smith 2010) was deferred under the 3-per-run
cap as designed.

Branch A leased tsk-20260426-000005 (profile-system, microbiome). The
acceptance tests explicitly require links.yaml to cite both McFall-Ngai
2013 and Costello 2012 as anchor sources, and both DOIs are still
prefixed-form in the manifest with no matching `registry/sources/src-*/`
— exactly the source-not-acquired condition profile-system SKILL.md
`Block or fail when` documents. Blocked with `unblock: {kind:
sources-resolved}` so the task auto-resumes once both DOIs land.

Two improvement proposals: a moderate one to add a `--unblock-on-sources`
CLI flag (the schema and runtime already support the kind, only the CLI
surface is missing — manually editing the manifest worked but is
friction), and a minor one to update plan-backlog Tier 0.75 docs to
prefer `sources-resolved` over the multi-pass `task-complete` loop for
multi-source blocks.
