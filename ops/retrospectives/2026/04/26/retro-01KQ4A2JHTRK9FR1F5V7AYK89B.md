---
retro_id: retro-01KQ4A2JHTRK9FR1F5V7AYK89B
task_id: tsk-20260426-000002
run_id: run-01KQ49XWW2YBVD0DB59ZF00HQ8
skill: scout-systems
timestamp: '2026-04-26T07:11:40Z'
agent: claude-code/Shiftor/55252
actionable: true
confidence: medium
what_worked:
  - "class_hint=microbiome pre-check (Tier 0.5 of plan-backlog) made the
    scout cost-free: no taxonomy gap, no review-records pairing, no
    --unblock-on-taxonomy condition. The scout could go straight from lease
    to profile-system emission."
  - "Existing deprecated instance-level entries (sys-000002 human-gut,
    sys-000006 rhizosphere) gave a clear roster signal that the type-level
    archetype was missing — the scout did not have to discover this."
  - "scouts-systems SKILL.md canonical acceptance_tests block (lines 78-87)
    pasted directly into the leased manifest matched the emitted
    profile-system task's shape; no rephrasing or improvisation needed."
blockers: []
proposed_improvements:
  - target: skills/scout-systems/SKILL.md
    change: >
      Clarify the apparent contradiction between SKILL.md's "source_refs is
      optional for the scout's profile-system proposal" guidance (line 60)
      and the canonical acceptance_tests block which requires ">=1
      source_ref" on every emitted profile-system task (line 81). Either
      relax the canonical acceptance test to "0 or more source_refs (>=1
      when the profile-system entry will assert specific quantitative or
      contested claims)", or strengthen the SKILL guidance to "always
      include >=1 foundational ref to satisfy the canonical scout
      acceptance test, even when the eventual profile-system entry will
      not assert quantitative claims". The current state forces scouts to
      pick foundational refs they may not strictly need, which adds
      source-debt downstream (Tier 0.75 acquire-source emissions for refs
      a bare type-level profile would not have to cite per AGENTS.md).
    rationale: >
      The microbiome scout pulled in two foundational doi: refs
      (10.1073/pnas.1218525110, 10.1126/science.1224203) to satisfy the
      acceptance test even though the type-level entry could exist
      source-free per AGENTS.md "What counts as a system worth
      cataloging" → "Source policy under this framing." This will
      generate two new acquire-source tasks via Tier 0.75 next plan-
      backlog pass (one per ref), consuming the per-type cap of 3 for
      acquire-source and pushing other source-debt items further down
      the queue. The same friction will recur on every type-level
      scout. Resolving the contradiction one way or the other lets
      scouts honestly emit source_refs only when they're load-bearing
      for the profile, not as test-padding.
    severity: minor
---

# Retrospective — tsk-20260426-000002 (scout-systems microbiome)

The scout found the type-level archetype on the first pass: priority-seed
hint named the slug, class_hint pre-check confirmed taxonomy resolution,
and existing deprecated instance-level entries (gut, rhizosphere)
confirmed the type-vs-instance gap was real. One profile-system task
emitted (`tsk-20260426-000005`); scout-report.md and run.json written;
inbox validates.

The one friction point: the canonical acceptance_tests block in
`skills/scout-systems/SKILL.md:78-87` requires `>=1 source_ref` on every
emitted profile-system task, but `skills/scout-systems/SKILL.md:60` and
AGENTS.md "Source policy under this framing" both say type-level entries
don't need sources for bare existence. The scout cited two foundational
refs (McFall-Ngai 2013, Costello 2012) to satisfy the test, but those
refs will now generate downstream source-debt acquire-source tasks even
though the eventual profile may not assert quantitative claims requiring
them. Proposed: pick one rule and align both passages — see the
proposed_improvement above. Severity: minor (the workaround works; the
cost is one to two extra acquire-source tasks per type-level scout, and
those are themselves cheap once the resolvers exist).
