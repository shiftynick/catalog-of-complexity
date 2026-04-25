---
retro_id: retro-01KQ3BMJZBMEMXP1A5RHWZ9FJS
run_id: run-01KQ3BMJZBPRXZ5HSQYEBYXM5A
task_id: tsk-20260425-000012
skill: acquire-source
timestamp: 2026-04-25T22:53:30Z
agent: claude-code/run-01KQ3BMJZBPRXZ5HSQYEBYXM5A
actionable: true
confidence: medium
what_worked:
  - "Crossref + Unpaywall pipeline succeeded first try on a 1968 AIP paper. The metadata-only outcome (paywalled, no OA full-text) wrote a clean source.yaml with non-null hash and `license: null`, exactly per the skill's \"paywalled is not a block\" rule."
  - "Schema validation accepted the metadata-only shape — the previously raised proposal (commit 9961bca, retro on src-000005) to document the OA-miss shape in the SKILL's Output section is the only remaining gap, and it's about documentation not behavior."
  - "Tier-0.75 sweep + task-complete unblock chain functioning end-to-end: this acquire-source completing now satisfies the unblock condition on tsk-20260423-000020 (blocked profile-system dihydrogen molecule), which the next coc advance sweep will move back to ready/."
blockers: []
proposed_improvements:
  - target: src/coc/sources/slugs.py
    change: >
      Make the title-slug truncation respect word boundaries. The current
      output for this paper is `improved-theoretical-ground-state-energy-of-
      the-hydrogen-mol`, mid-word. Truncate at the last hyphen position
      before the byte/char limit instead of slicing in the middle of the
      final word; if the resulting slug would be too short, drop one
      stop-word from the front instead of mid-word truncation. Same
      proposal already raised in the retro for src-000005 (commit 9961bca);
      this iteration is a recurrence and bumps the priority of acting on
      it from minor to moderate.
    rationale: >
      Mid-word truncation produces ugly canonical ids and degrades both
      grep-ability and human readability across the registry. The fix is
      local to one helper and idempotent (existing src-* dirs are not
      renamed; new ones come out cleaner).
    severity: moderate
---

## What happened

Leased `tsk-20260425-000012` (acquire-source, doi:10.1063/1.1669836 = Kolos
& Wolniewicz 1968 H2 ground-state benchmark paper). `coc acquire` resolved
via Crossref + Unpaywall, registered as
`src-000003--improved-theoretical-ground-state-energy-of-the-hydrogen-mol`.
Paper is paywalled at AIP with no Unpaywall hit, so the source is
metadata-only (license: null, raw/ contains metadata.json + unpaywall.json
only). Schema validates; hash recorded.

## Friction

The slug truncates mid-word to `...hydrogen-mol`. This is the second
occurrence (first was on src-000005 from commit 9961bca, where the slug
ended `-tem` mid-word). Bumped severity on the existing
`src/coc/sources/slugs.py` proposal from minor to moderate; otherwise
nothing new.
