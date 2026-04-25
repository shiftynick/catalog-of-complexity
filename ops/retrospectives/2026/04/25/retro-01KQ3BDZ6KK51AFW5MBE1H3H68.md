---
retro_id: retro-01KQ3BDZ6KK51AFW5MBE1H3H68
run_id: run-01KQ3BDZ6KJJFKFHBADG6F0J83
task_id: tsk-20260425-000011
skill: acquire-source
timestamp: 2026-04-25T22:48:30Z
agent: claude-code/run-01KQ3BDZ6KJJFKFHBADG6F0J83
actionable: true
confidence: high
what_worked:
  - "`uv run coc acquire` failed fast with a clear upstream error (`FAIL 404 Not Found: https://api.crossref.org/works/...`) and pointed at the exact API endpoint that returned 404, which made the diagnosis (Crossref-vs-DataCite mismatch) immediate."
  - "DataCite's public metadata API (https://api.datacite.org/dois/<doi>) is unauthenticated and returned full record (publisher, title, year, type, landing url) — which makes the resolver fix straightforward: same pattern as the Crossref resolver, different endpoint."
  - "Skill's `not-found` block clause is the correct terminal state here: the run has no record to write, so blocked-not-failed is appropriate. Watchdog won't reap and retry."
blockers:
  - "Resolver coverage gap — `doi:` prefix routes only to Crossref. NIST (10.18434/*), Zenodo (most), figshare, and most dataset-issuing publishers register through DataCite. Any catalog work that wants to cite a NIST standard reference database, a Zenodo dataset, or similar will hit this same wall until a DataCite fallback lands."
proposed_improvements:
  - target: src/coc/sources/dispatch.py
    change: >
      In `resolve()`, when the ref starts with `doi:`, try Crossref first and
      fall back to DataCite on 404. Add a new resolver module
      `src/coc/sources/datacite.py` mirroring `crossref.py`'s shape: fetch
      `https://api.datacite.org/dois/<doi>`, map the JSON:API response to
      `ResolvedSource` (title, publisher, publicationYear, type from
      `attributes.types.resourceTypeGeneral`, landing url from
      `attributes.url`), and write `metadata.json` (raw API body) to `raw/`.
      No OA-fulltext step needed for DataCite — most DataCite DOIs are
      datasets where the landing url is the access point.
    rationale: >
      Closes a recurring resolver gap. NIST standard reference databases (the
      hydrogen-atom profile needs the Atomic Spectra Database, doi
      10.18434/T4W30F), most Zenodo dataset DOIs, and a sizeable fraction of
      the methods/data papers the catalog will want to cite are DataCite-
      registered. Without this fallback, every such reference produces a
      blocked acquire-source task that no autoremediation can resolve.
    severity: major
  - target: skills/acquire-source/SKILL.md
    change: >
      In the "Block or fail when" section, refine the `not-found` clause to
      distinguish "DOI is not minted anywhere" from "DOI is minted at a
      registrar the resolver doesn't query." Until a DataCite resolver lands,
      add a note that a Crossref 404 on a DOI in a known DataCite namespace
      (10.5281/Zenodo, 10.6084/figshare, 10.18434/NIST, etc.) should be
      treated as a resolver-coverage gap and the retro should propose closing
      it, rather than treated as a genuine not-found.
    rationale: >
      The `not-found` reason as currently worded ("the DOI is not minted")
      misclassifies DataCite DOIs that Crossref returns 404 on. A retro
      reader looking only at the block reason would assume the DOI is bad,
      not that the resolver is missing.
    severity: minor
---

## What happened

Leased `tsk-20260425-000011` to acquire `doi:10.18434/T4W30F` (NIST Atomic
Spectra Database, blocking the hydrogen-atom profile). `coc acquire`
returned `FAIL 404 Not Found: https://api.crossref.org/works/10.18434/T4W30F`.
Verified out-of-band that the DOI is minted — `https://api.datacite.org/dois/
10.18434/T4W30F` returns a complete record (publisher: NIST; type: Dataset;
url: http://www.nist.gov/pml/data/asd.cfm). The resolver dispatch
(`src/coc/sources/dispatch.py`) routes `doi:` exclusively to Crossref, so
DataCite-registered DOIs cannot resolve. Blocked the task as `not-found` per
the skill (correct given the current resolver), but flagged the underlying
resolver-coverage gap as a major-severity proposal with a follow-up
`setup-repo` task in inbox/.

## Friction

The skill's `not-found` block reason conflates "DOI is not minted" with
"DOI is minted at a registrar the resolver doesn't query." That ambiguity
made it tempting to fail the task, which would have been wrong (the DOI
exists; the library doesn't see it). Captured as a minor proposal alongside
the major resolver-coverage proposal.

## Follow-up

Per the retrospective skill's contract for `severity: major`, emitted
`tsk-20260425-000027` (setup-repo) to inbox/ describing the DataCite
fallback. setup-repo is gated by human review (not in
AUTO_PROMOTE_TYPES — actually wait, let me re-check) — leaving promotion
to the next pass / reviewer per AGENTS.md autonomy policy.
