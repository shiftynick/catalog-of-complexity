---
retro_id: retro-01KPXS4SB1AXD47T60YTDG0SC9
task_id: tsk-20260423-000009
run_id: run-01KPXS1XPAFTJF4BFRVNAX73J0
skill: review-records
timestamp: 2026-04-23T18:20:26Z
agent: claude-code/Shiftor/114196
actionable: true
confidence: medium
what_worked:
  - "The retro-note embedded in the task manifest listed the three target slugs and their scope distinctions against existing classes, so the review had a pre-grounded starting point rather than having to re-derive candidates."
  - "Adding `references` as a free-form list worked transparently because `src/coc/taxonomy.py` consumes only known keys (`slug`/`label`/`description`/`aliases`/`broader`) and silently ignores the rest. `coc export-taxonomy` stayed consistent."
  - "Acceptance test #2 (`coc export-taxonomy` consistency) was cheap to verify: grep the two export files for the three new slugs."
blockers: []
proposed_improvements:
  - target: taxonomy/source/system-classes.yaml
    change: "Promote a convention: every new taxonomy entry SHOULD include a `references:` list with at least one authoritative source. Document this at the top of the file (or add a README) and consider adding an optional `references` property to a (future) taxonomy-item schema so the shape is discoverable."
    rationale: "This task required per-entry references but the file has no documented convention and no schema. Future authors won't know references are expected, and mid-term the field may drift in shape (string vs. object). Documenting now costs nothing; writing the schema can wait until 2–3 more entries adopt the shape."
    severity: minor
  - target: skills/review-records/SKILL.md
    change: "Add a short note under Preconditions (or Procedure step 1) that when `record_scope` is a taxonomy file, the relevant schema-level check is `uv run coc export-taxonomy` (not just `uv run coc validate`) — a SKOS export round-trip is the real consistency signal for taxonomy edits."
    rationale: "The current skill documents `coc validate <scope-path>` as the shape check. For taxonomy/, validate passes even when the loader silently ignores keys, so an agent reviewing a taxonomy change might skip the export round-trip. Codifying the export-taxonomy step keeps reviewers honest."
    severity: minor
---

Run summary. Added `unicellular-organism`, `metabolic-network`, and
`superorganism` to `taxonomy/source/system-classes.yaml`, each with a
scope-distinctness clause and two authoritative references. `coc
validate` and `coc export-taxonomy` both clean; the three new slugs
appear in `taxonomy/exports/labels.json` and `taxonomy/exports/taxonomy.ttl`.
No follow-up tasks emitted (output_targets scoped to the taxonomy file;
retro documented no deferred candidates).

Why two minor proposals. Neither blocked this run — both are
observations about latent conventions that worked by accident rather
than by design. The `references:` field was quietly accepted because
the loader ignores unknown keys; that's fine for one file but will
become ambiguous across three or four. The `coc export-taxonomy`
round-trip is the real safety net for taxonomy edits and deserves to
be named in the skill it backs.
