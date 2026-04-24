---
retro_id: retro-01KPZX4T48DMS9B65PDQ2PEHHY
task_id: tsk-20260423-000020
run_id: run-01KPZX2RY7ND1K7RBFP7SYHGQC
skill: profile-system
timestamp: '2026-04-24T14:09:30Z'
agent: claude-code/Shiftor/91844
actionable: true
confidence: high
what_worked:
  - 'profile-system SKILL.md Block clause fired cleanly for the second consecutive run (dihydrogen after hydrogen), confirming the rule is reproducible and the run loop does not drift into fabricating src-* ids or inlining book citations as a workaround.'
  - 'Preflight short-circuits worked: `coc validate` clean, git clean, `coc advance` correctly reported `no auto-eligible tasks` (everything already promoted), `coc next` returned tsk-20260423-000020, lease claimed first try.'
  - 'The prior retro (retro-01KPZSPPPGR03ZZ9H0XSZFYPHF) remains accurate — re-reading it substituted for re-deriving the block rationale from scratch, showing the retro artifact is already functioning as institutional memory across identical-shape runs.'
blockers:
  - 'Same block as tsk-20260423-000019: source_refs (isbn:9780486691862, isbn:9780199541423, doi:10.1063/1.1669836) are all prefixed forms with no matching registry/sources/src-* entries, and no acquire-source tasks have been seeded since the prior run.'
  - 'Structural feedback-loop gap: plan-backlog (Tier 0.75 source-debt seeding) only runs in autonomous-run Branch B (empty queue). Because scout-systems keeps producing profile-system tasks that promote into ready/, `coc next` never exits 1, so Branch B never fires, so acquire-source tasks never get seeded, so every subsequent profile-system run re-hits the same block. tsk-20260424-000001 (belousov-zhabotinsky-reaction) is already in ready/ with the same three unregistered prefixed refs — the next autonomous run will block on it for identical reasons. Three consecutive source-not-acquired blocks are the likely outcome before the queue drains enough to let Branch B fire.'
proposed_improvements:
  - target: prompts/autonomous-run.md
    change: "Add a preflight step between `coc advance` and `coc next` that invokes a `plan-backlog --tier 0.75` (source-debt only) pass unconditionally — not gated on empty queue — capped at the existing 3-per-run acquire-source emission. Alternately: in Branch A, if the leased task has any prefixed source_ref not resolving to src-*, emit the acquire-source tasks inline before the skill Block fires, so a source-not-acquired block always comes with a matching acquisition task in inbox/."
    rationale: "Today Tier 0.75 is only reachable through Branch B, and Branch B is gated on `coc next` returning empty. With a steady supply of scout-systems output promoting into ready/, the queue will not drain, so Tier 0.75 never fires and the same source-not-acquired block repeats deterministically. Two consecutive blocks (hydrogen-atom, dihydrogen-molecule) and a third in-flight (belousov-zhabotinsky-reaction) confirm the loop is closed in the wrong direction. Moving Tier 0.75 into preflight — or running it as a side-effect of Branch A's lease when the task has debt — breaks the deadlock without waiting for the queue to empty."
    severity: major
  - target: skills/plan-backlog/SKILL.md
    change: "Expand Tier 0.75's scan set from `{inbox,ready,leased,running}/` to include `blocked/`, and adopt the prior retro's proposal (retro-01KPZSPPPGR03ZZ9H0XSZFYPHF §proposed_improvements[2]) to emit acquire-source tasks with `--unblock-on-task` wiring so blocked profile-system tasks auto-resume once their source debt clears."
    rationale: "This is a severity bump of the prior retro's moderate proposal: the second identical block in 24 hours is empirical evidence that Tier 0.75 missing blocked/ is not a theoretical gap. Even once the autonomous-run change above lets Tier 0.75 fire, it must actually see tasks sitting in blocked/ to close the loop for already-parked work."
    severity: moderate
  - target: skills/profile-system/SKILL.md
    change: "Adopt the prior retro's (retro-01KPZSPPPGR03ZZ9H0XSZFYPHF §proposed_improvements[0]) prefix-list widening: either enumerate `isbn:` (and `pmid:`, `handle:`) alongside `doi:/arxiv:/url:` in the Preconditions and Block clauses, or reword to 'any prefix other than src-NNNNNN--<slug>' so the rule is closed under new external-identifier schemes. Unchanged rationale from prior retro; restated here only so a sweep of unactioned retro proposals can pick it up on the second occurrence rather than the first."
    rationale: "The task at hand has two isbn: refs and one doi: ref. The doi: alone triggers the Block clause textually, so the run was unambiguous — but a future agent could read the skill narrowly and decide isbn: is out of scope. Re-raising because the proposal is still unactioned and the underlying exposure is now confirmed in live data."
    severity: minor
---

# Retrospective — run-01KPZX2RY7ND1K7RBFP7SYHGQC (profile-system)

Primary run, Branch A. Leased tsk-20260423-000020 (profile-system dihydrogen-molecule), blocked immediately on `source-not-acquired` — three prefixed `source_refs` (2× `isbn:`, 1× `doi:`), zero matching `registry/sources/src-*` entries. No canonical profile written; terminal state `blocked`; task now in `ops/tasks/blocked/`.

Preflight: `coc validate` OK, git clean, `coc advance` reported no auto-eligible tasks (inbox empty, blocked/ holds only tsk-20260423-000019 which has no `unblock` condition recorded). `coc next` → tsk-20260423-000020. Lease acquired first try. No heartbeats (sub-cadence run, ~3 min wall-clock).

This is the second consecutive profile-system run to hit the identical block, and tsk-20260424-000001 (BZ) is next in ready/ with the same three-unregistered-refs shape — a third identical block is deterministic unless autonomous-run or plan-backlog changes. The prior retro (retro-01KPZSPPPGR03ZZ9H0XSZFYPHF) proposed the correct fix set at severity minor/moderate; this retro re-raises the plan-backlog scheduling issue as the root cause and bumps the autonomous-run preflight change to severity: major since the loop is now empirically deadlocked in the wrong direction. No follow-up `review-records` manifest is emitted from this retro; the severity-major proposal targets `prompts/autonomous-run.md` (a prompts edit, not a registry/taxonomy edit) and the webUI/prune workflow plus the severity-major flag are sufficient signalling for a reviewer.
