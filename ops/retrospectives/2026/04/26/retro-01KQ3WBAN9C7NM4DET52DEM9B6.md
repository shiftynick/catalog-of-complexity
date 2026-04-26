---
retro_id: retro-01KQ3WBAN9C7NM4DET52DEM9B6
run_id: run-01KQ3W9C3XQA9W23FS1BB9NW01
task_id: tsk-20260425-000027
skill: review-records
timestamp: 2026-04-26T03:11:30Z
agent: claude-code/run-01KQ3W9C3XQA9W23FS1BB9NW01
actionable: true
confidence: high
what_worked:
  - "The retro from tsk-20260425-000011 already prescribed the exact pattern (Crossref-first → DataCite-fallback on 404, mirror crossref.py shape, no Unpaywall step for DataCite) so the implementation reduced to translation work; the task manifest's acceptance tests (kind=Dataset, publisher=NIST, landing url=http://www.nist.gov/pml/data/asd.cfm) gave a precise live oracle that confirmed correctness end-to-end on first run."
  - "DataCite's JSON:API returned every field needed (titles, creators with given/family, publicationYear, types.resourceTypeGeneral, url, rightsList) without auth; the publisher field even appears in the citation string already so the existing source.yaml shape covers DataCite cleanly without a schema bump."
  - "Wrapping only the doi: branch in dispatch.py (not the whole function) keeps NotFoundError semantics intact for arxiv:/url:/isbn: paths and propagates a single NotFoundError when both Crossref and DataCite miss — preserving the not-found block clause without a new error class."
blockers: []
proposed_improvements:
  - target: tests/test_sources.py
    change: >
      Add unit tests for the new datacite resolver mirroring the crossref
      tests: a happy-path test feeding a fake fetcher with a JSON:API
      response and asserting the ResolvedSource fields (kind=dataset,
      year, authors, license, slug, single artifact named
      metadata.json), plus a test for the dispatch fallback that returns
      NotFoundError from a stub Crossref fetcher and asserts DataCite is
      called and returns successfully. The current run skipped tests
      because tests/ was not in this task's output_targets — the live
      acquire against the real API is the only verification, which is
      slow and requires network. A follow-up review-records task with
      tests/ in output_targets is the cleanest home.
    rationale: >
      Without unit tests the resolver-level invariants (DataCite kind
      mapping, missing-field tolerance, dispatch fallback ordering)
      cannot be regressed by future edits without re-hitting the live
      DataCite API. The existing crossref tests demonstrate the pattern
      and the fake-fetcher infrastructure already exists in the test
      file.
    severity: minor
  - target: src/coc/sources/dispatch.py
    change: >
      Once tests for the DataCite path land, consider extracting the
      doi: try-Crossref-then-DataCite logic into a list-of-resolvers
      iteration (e.g. `for r in [crossref, datacite]: try: return
      r.resolve(...) except NotFoundError: continue`) so adding a third
      DOI registrar (mEDRA, ISTIC, JaLC, etc.) is a one-line change
      rather than another nested try/except. Premature today (only two
      resolvers) but worth flagging if a third lands.
    rationale: >
      Forward-looking refactor; defers complexity until justified by a
      third registrar but documents the cleanup so future plan-backlog
      Tier 0.75 sweeps for unhandled DOI prefixes have a clear hook.
    severity: minor
---

Implemented the DataCite resolver fallback prescribed by the prior retro.
Live acceptance test (`uv run coc acquire doi:10.18434/T4W30F`) wrote
`registry/sources/src-000008--nist-atomic-spectra-database-nist-standard-reference-databas/`
with the DataCite metadata payload and source.yaml fields matching the
acceptance-test predictions byte-for-byte. The 78-test pytest suite still
passes (no test added — output_targets discipline; flagged as a minor
follow-up).

The downstream chain is now unblocked: blocked acquire-source
tsk-20260425-000011 (same DOI) will return the existing src-000008 path
idempotently when the watchdog or a manual unblock re-leases it; that
in turn unblocks tsk-20260423-000019 (profile-system hydrogen atom). No
manual unblock written from this run — the unblock wiring already exists
on those tasks.

Both proposals are minor; no follow-up task emitted (severity threshold
is `major` per the skill's procedure step 6).
