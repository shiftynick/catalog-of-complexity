---
retro_id: retro-01KQ389KPKQEP48AHJ7MEKFFWV
run_id: run-01KQ388FHQEN52XBR86R7NSR4Q
task_id: tsk-20260425-000008
skill: profile-system
timestamp: '2026-04-25T21:25:30Z'
agent: claude-code/scheduled-run
actionable: true
confidence: high
what_worked:
  - 'Recognizing the instance-vs-type mismatch immediately on read of the candidate slug (`escherichia-coli-k12-metabolic-network` — strain-specific, not the type) and routing to `blocked` rather than burning a profile-system iteration on a soon-to-be-deprecated entry. The 1-minute wall-clock cost is the entire price of this triage. The b4b0de5 commit''s clarification of the type-level criterion in AGENTS.md and the skill SKILL.md was sufficient context to make the call without ambiguity.'
  - 'Pairing this block with the same observation about tsk-20260425-000009 (E. coli K-12 MG1655 whole prokaryotic cell — also an instance of `prokaryotic-cell`) lets a future review-records pass batch the recategorization. Two ready instance-shaped tasks that would each consume an iteration slot can collapse into one curatorial decision.'
blockers:
  - 'No automatic unblock condition wires cleanly here. Instance/type recategorization is a curatorial decision (does this become a canonical_example on the type entry, or is it discarded as already-covered?), not a wait-on-X gate. The task sits in blocked/ until a human review-records pass picks it up — the coc advance sweep cannot resolve it on its own. This is expected for type-level criterion enforcement; not all blocks reduce to wait-on-condition.'
proposed_improvements:
  - target: skills/scout-systems/SKILL.md
    change: 'Add a "Type-not-instance pre-check" step to the scout-systems Procedure, executed before emitting profile-system tasks. Reject any candidate whose proposed slug matches strain/cultivar/named-individual patterns (regex `(escherichia|saccharomyces|caenorhabditis|homo|amazon|nyse|mediterranean)`-?[a-z0-9-]*` or contains a strain identifier like `k12-`, `mg1655-`, `bl21-`). When rejected, propose the corresponding type-level scout instead (e.g. for `escherichia-coli-k12-metabolic-network` propose `metabolic-network` with E. coli K-12 as a canonical_example) and record the recategorization in the scout''s plan-report under a Recategorizations section. Block the original scout with reason `instance-not-type` rather than emit the rejected candidate.'
    rationale: 'Empirically demonstrated by this iteration AND tsk-20260425-000009 (E. coli K-12 whole-cell, identical issue). Both scouts ran before the b4b0de5 reframing; their outputs reflect the older case-study orientation. The post-b4b0de5 scout SKILL.md says "propose missing type-level archetypes against the priority list and existing taxonomy, not literature-search for case studies" but does not encode an automated check. Adding the regex-based pre-check (with the patterns expandable as new instance-shaped candidates emerge) makes the type-level criterion enforceable at scout emission rather than at profile-system block time, eliminating the iteration-slot waste. Severity moderate: the failure mode persists for as long as instance-shaped candidates can leak through, and several biological/organism scouts in the priority pipeline are likely to trigger it.'
    severity: moderate
  - target: skills/review-records/SKILL.md
    change: 'Document a new review-records sub-pattern: "instance-to-canonical-example recategorization." When a profile-system task is blocked with reason `instance-not-type` and the proposed slug is recognizable as a specific instance of an existing or proposed type, the review-records resolver should (a) move the blocked task to archive/ rather than rerunning it, (b) emit a follow-up profile-system task for the parent type if none is in flight, and (c) ensure the instance is included in the type entry''s `canonical_examples` field once the type entry is profiled. Add this as a bulleted sub-procedure under the existing review verdict rules.'
    rationale: 'The deprecation pattern landed in b4b0de5 covered already-on-disk system records (sys-000001/2/4/5/6 → review-records tasks 000016-000020) but does not have a documented analogue for in-flight scout outputs. Today''s block is the empirical case where the analogue is needed: the blocked task is not just "stuck" but conceptually mis-shaped, and the review-records resolver needs a clear rule for archiving + recategorizing rather than retrying. Severity minor: the resolver can derive the action from first principles, but explicit documentation prevents drift across operators.'
    severity: minor
---

# Retrospective — run-01KQ388FHQEN52XBR86R7NSR4Q (profile-system, blocked)

Iteration 3 of the batched scheduled run. Leased tsk-20260425-000008 (proposed
profile for `escherichia-coli-k12-metabolic-network`), recognized within
seconds that the candidate slug is an instance (E. coli K-12 MG1655's
metabolic network — strain-specific) rather than the type
(`metabolic-network`, an archetypal kind that E. coli K-12 exemplifies).
Per AGENTS.md "What counts as a system worth cataloging" and skills/profile-
system/SKILL.md "Block or fail when," the candidate fails the type-not-
instance criterion. Blocked rather than failed because the task may be
revived as a canonical_example on the eventual type-level metabolic-network
entry (a curatorial action), but no automatic unblock wires here — recat-
egorization is a human review-records decision.

The same shape applies to tsk-20260425-000009 (E. coli K-12 MG1655 whole
prokaryotic cell — an instance of the type `prokaryotic-cell`). Both scouts
predate the b4b0de5 type-level reframing of skills/scout-systems/SKILL.md.

Two follow-ups flagged: (1) skills/scout-systems/SKILL.md should gain a
type-not-instance pre-check at emission time, and (2) skills/review-records/
SKILL.md should document the instance-to-canonical-example recategorization
sub-pattern so the eventual review pass has a clear template.
