---
retro_id: retro-01KQ38FKCYADQ782HQXPAB8Z1T
run_id: run-01KQ38EQYPM91T8SWTS8SRMCYM
task_id: tsk-20260425-000010
skill: acquire-source
timestamp: '2026-04-25T21:34:30Z'
agent: claude-code/scheduled-run
actionable: true
confidence: medium
what_worked:
  - 'Crossref + Unpaywall path on a 1972 ACS DOI succeeded end-to-end with no manual intervention. ~2 minutes wall-clock, two raw artifacts (metadata.json + unpaywall.json), SHA-256 hash auto-computed, schema validation green. The acquire-source skill is delivering on its contract — first ACS metadata fetch in this catalog, no API-specific brittleness.'
  - 'Metadata-only acquisition (no OA full-text for this paywalled paper) was correctly recognized as a non-block per acquire-source SKILL.md. Many of the priority-list anchor papers will be similarly OA-free (older DOIs, paywalled journals); the metadata-only path is load-bearing.'
blockers: []
proposed_improvements:
  - target: src/coc/sources/slugs.py
    change: 'Improve the slug truncation rule in `slugify()`. Currently the 60-char cap (MAX_SLUG_LEN) plus the `.rstrip(\"-\")` produces slugs like `oscillations-in-chemical-systems-ii-thorough-analysis-of-tem` — truncated mid-word at character 50-something with the trailing `-temporal` lost. Consider truncating on word boundaries (split on `-`, accumulate tokens until next would exceed cap, drop the partial), or appending a short hash of the full untruncated slug as a disambiguator, or both. The current behavior is functional (slugs are unique-by-construction via the src-NNNNNN prefix) but opaque to a human reader scanning registry/sources/.'
    rationale: 'Empirical: the 1972 FKN paper''s title-derived slug landed as `oscillations-in-chemical-systems-ii-thorough-analysis-of-tem` — the trailing `-tem` is the truncated head of `-temporal-oscillation-...`. The information density of the truncated form is low (a reader can''t tell from `-tem` what was lost), and longer titles will produce similar mid-word cuts. Word-boundary truncation costs nothing at runtime and produces readable stems. Severity minor: pure ergonomics; the slug is unique and validates, so no functional issue.'
    severity: minor
  - target: skills/acquire-source/SKILL.md
    change: 'Document the "metadata-only OA-free" acquisition shape under the Output shape section. Add a sub-bullet under the existing `raw/` description: "For paywalled sources with no Unpaywall OA hit (`license: null` in source.yaml), raw/ contains only metadata.json and unpaywall.json — no paper.<ext>. This is a successful terminal state, not a block, per the skill''s ''paywalled source with no OA full-text is not a block'' rule." Today''s acquisition is the first concrete instance of this path in the catalog; capturing the shape now prevents a future operator from second-guessing whether the absence of paper.pdf is a partial acquisition.'
    rationale: 'The skill''s "Block or fail when" already documents this case correctly, but the Output shape section describes the OA-hit case (raw/ contains metadata.json, unpaywall.json, optionally paper.<ext>). Making the OA-miss case explicit in Output shape — not just under Block-or-fail — makes the skill self-documenting for the metadata-only path. Severity minor: documentation clarity, no behavior change.'
    severity: minor
---

# Retrospective — run-01KQ38EQYPM91T8SWTS8SRMCYM (acquire-source, done)

Iteration 5 of the batched scheduled run. First catalog acquisition of an
ACS-published DOI. doi:10.1021/ja00780a001 (Field, Koros, Noyes 1972 —
the FKN-mechanism reference paper for the Belousov-Zhabotinsky reaction)
landed cleanly: Crossref metadata + Unpaywall OA lookup, no full-text
available (license: null), metadata-only source.yaml at
`registry/sources/src-000002--oscillations-in-chemical-systems-ii-
thorough-analysis-of-tem/`. Schema validates, hash recorded, no
human intervention.

Downstream effect: tsk-20260424-000001 (blocked profile-system BZ) has its
unblock wired to {kind: task-complete, task_id: tsk-20260425-000010}, so
the next `coc advance` sweep should move it back to ready/. It will then
re-block on the two remaining isbn refs (9780471893844, 9780195096705)
until acquire-source tasks for those land — the multi-source convergence
loop that the new `sources-resolved` unblock kind from iteration 1 is
designed to retire (once plan-backlog Tier 0.75 is updated to use it for
all-resolvable-class refs, per the deferred follow-up flagged in retro-
01KQ37XTTBYTNPH49V1VEVRY03).

Two minor proposals: (1) slugify truncation should respect word boundaries
to avoid mid-word cuts like the trailing `-tem` on this slug; (2)
acquire-source SKILL.md should document the metadata-only OA-miss shape in
its Output shape section, not just under Block-or-fail.
