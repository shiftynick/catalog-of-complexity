---
retro_id: retro-01KQ4MKYW49E1JK6VREZ5N3B72
task_id: tsk-20260426-000011
run_id: run-01kq4mk908a0d3taw95gsddz09
skill: profile-system
timestamp: '2026-04-26T10:15:45Z'
agent: claude-code/auto
actionable: true
confidence: medium
what_worked:
  - profile-system "Block or fail when" clause for source-not-acquired triggered cleanly; the three prefixed refs (isbn:9780120885633, isbn:9781439837177, doi:10.1016/0022-5193(69)90015-0) had no matching registry/sources/src-*/ entry, so the block was deterministic.
  - Setting unblock.kind:sources-resolved on the manifest closes the loop with the three acquire-source tasks emitted in iteration 1's Tier-0.75 sweep; once all three sources land, coc advance moves this task back to ready/ without manual intervention.
blockers:
  - This profile-system task was promoted to ready/ in the same invocation that emitted the acquire-source tasks for its sources; the auto-promotion fired before plan-backlog Tier-0.75 had a chance to acquire the sources, so iteration 2 had no choice but to lease a known-blockable task. Net work was wasted (lease + immediate block + retro + commit) on a task whose dependency was visible at preflight time.
proposed_improvements:
  - target: skills/plan-backlog/SKILL.md
    change: 'Have the Tier-0.75 source-debt sweep also write unblock.kind:sources-resolved onto any task in `ready/` whose prefixed source_refs have at least one acquire-source task emitted in the same pass, and move that ready task to `blocked/`. This converts the ``ready task with un-acquired sources'''' state into ``blocked-on-sources-resolved'''' eagerly, before the Branch-A loop leases it.'
    rationale: Iteration 2 of this invocation leased tsk-20260426-000011 only to immediately block on source-not-acquired, despite iteration 1's Tier-0.75 sweep already having emitted acquire-source tasks for exactly its three prefixed refs. A pre-block in plan-backlog would have skipped the wasted lease/heartbeat/run/retro/commit cycle. Currently the skill only wires unblock for tasks already in `blocked/`, not for tasks in `ready/` with the same dependency shape.
    severity: minor
  - target: prompts/autonomous-run.md
    change: After Tier-0.75 emits acquire-source tasks for refs cited by ready/* tasks, optionally re-run a localized check that moves any such ready/* task into blocked/ with sources-resolved unblock wiring, before Branch A's first lease.
    rationale: Same defect framed at the orchestration layer instead of the skill layer. Either fix prevents the wasted iteration; the skill-layer fix is more localized.
    severity: minor
---

The profile-system skill's source-not-acquired block clause did its job, but
the orchestration leaked one wasted iteration: tsk-20260426-000011 was already
in ready/ when this invocation's preflight ran. The Tier-0.75 sweep emitted
three acquire-source tasks covering its prefixed refs, but did not also
demote the ready task to blocked/. Branch A then leased it, immediately
hit the source-not-acquired clause, and produced this iteration of pure
overhead. Setting unblock.kind:sources-resolved on the now-blocked task
closes the loop for the next invocation. The proposed plan-backlog edit
would prevent the same pattern from recurring whenever Tier-0.75 covers a
ready (not just blocked) task's refs.
