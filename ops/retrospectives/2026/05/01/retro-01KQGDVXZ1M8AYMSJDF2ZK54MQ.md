---
retro_id: retro-01KQGDVXZ1M8AYMSJDF2ZK54MQ
task_id: tsk-20260501-000001
run_id: run-01KQGDTD5TQNKSM02J6G8C7R0E
skill: profile-system
timestamp: 2026-05-01T00:09:30Z
agent: claude-code/host/auto
actionable: false
confidence: medium
what_worked:
  - "Hutchinsonian hypervolume framing translated directly into a `boundary.type: functional` profile, sidestepping the spatial/temporal default that fits poorly for niche."
  - "Drawing canonical_examples from four very different mechanistic case studies (Darwin's finches resource axis, Anolis structural-habitat, intertidal zonation fundamental-vs-realized, Tilman R*) keeps the type entry useful as a cross-reference for downstream analyses without expanding scope."
  - "Worklist resolver, dispatch, advance, lease, complete all worked single-shot; preflight + emit + promote took <1 minute of wall-clock."
  - "Pre-existing main_feedbacks reference text in sibling stubs let me adopt the em-dash convention from the start, so no ruamel.yaml flow-mapping snag this run (the cryosphere retro's proposed pitfall note is what cued me to avoid it)."
blockers: []
proposed_improvements: []
---

P0 stub-upgrade for ecological-niche, an unusually concept-heavy archetype
because the niche has three legitimately-distinct framings (Grinnellian
habitat, Eltonian role, Hutchinsonian hypervolume) that the archetype
must accommodate without picking a winner. Resolved by writing the
boundary as the Hutchinson hypervolume (the modern synthesis) while
flagging the framings as `boundary_clarity: contested` and naming all
three in notes.md.

Population of v0.2 facets was generous (10 of 11 — primary_resources
included; only `aliases` omitted). main_feedbacks intentionally mixes
positive (niche construction) and negative (density dependence,
character displacement) loops. failure_modes use the existing failure
vocabulary (capture, lock-in, runaway-feedback) plus niche-specific
modes (competitive exclusion, niche truncation under climate change).

No proposed improvements: the prior cryosphere retro's YAML-pitfall
note already covers the only friction this skill has produced lately,
and re-proposing it would just inflate the actionable count. Marking
this retro `actionable: false` and counting it toward the per-phase
non-actionable streak.
