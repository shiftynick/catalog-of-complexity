---
retro_id: retro-01KPXE59VNY48PC0CDNRR475B2
task_id: tsk-20260423-000003
run_id: run-01KPXE4DQ9G59106BCG4GS06CG
skill: profile-system
timestamp: '2026-04-23T15:08:35Z'
agent: Claude/Shiftor/111528
actionable: true
confidence: medium
what_worked:
  - >-
    The scout-provided boundary cue and the two anchor sources (Chaplin 2010,
    Janeway 9e) were sufficient to draft a grounded profile without broader
    literature exploration.
  - >-
    Using sys-000002 as a reference shape made links.yaml and notes.md
    structurally consistent with prior records on the first pass, keeping
    review surface low.
  - >-
    `coc complete --outputs` worked cleanly this run — the queue state moved to
    `done/` and the `task.complete` event appended without the order-of-operations
    bug that blocked the prior profile-system run (run-01KPXDCKSJF3Q7KKKQZW16EVVB).
    Either that path is less brittle than the prior retro suggested, or the
    output JSON shape I used (array of `{path: ...}` objects) avoided it.
blockers:
  - >-
    The `status: active` vs `status: profiled` mismatch between the
    profile-system skill, task acceptance text, and the system schema is now a
    second-time friction point. I made the same judgment call as the prior
    profile-system run, but the stale wording is still in the skill file.
proposed_improvements:
  - target: skills/profile-system/SKILL.md
    change: >-
      Replace `status: active` in the skill's procedure and stop_conditions
      with the schema-valid value `status: profiled`, so future profile-system
      tasks do not keep re-deriving the same judgment call. The prior retro
      (retro-01KPXDCKSJDNZQQMETHJD02J8D) already proposed this with severity
      `moderate`; this run confirms the issue recurs.
    rationale: >-
      Two consecutive profile-system runs have had to reconcile the skill's
      wording with the schema enum. The fix is a one-line documentation edit
      and removes a recurring ambiguity.
    severity: moderate
  - target: schemas/system.schema.json
    change: >-
      Consider adding an `organizational` field to the `scales` object, or
      remove the `organizational` reference from skills/profile-system/SKILL.md
      step 3. The skill currently lists `organizational` as a scales subfield
      but the schema's `additionalProperties: false` rejects it.
    rationale: >-
      Either direction closes a latent trap: profile-system authors who follow
      the skill literally would write an invalid record. Current behavior is
      "silent drop" because authors notice via schema error; better to align.
    severity: minor
---

# Retrospective

The vertebrate adaptive immune system profile landed cleanly on the schema and
cited the two scouted anchors plus pointers to IMGT and IEDB as downstream
datasets. The boundary used dependence on somatic receptor diversification plus
clonal selection as the membership criterion, which keeps innate-like
lymphocytes in scope and trained innate memory out.

Process-side, the only recurring friction is the `status: active` wording in
the skill file — flagged again. `coc complete` behaved correctly this time,
so the prior retro's `src/coc/queue.py` ordering concern may be narrower than
initially assumed or already patched; worth checking before acting on it.
