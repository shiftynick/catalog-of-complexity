---
retro_id: retro-01KQ3ZS6CF7M9HEX0N746NRH48
run_id: run-01KQ3ZQZBRAJCC6RRPSQDPCRCW
task_id: tsk-20260425-000028
skill: review-records
timestamp: 2026-04-26T04:13:00Z
agent: claude-code/run-01KQ3ZQZBRAJCC6RRPSQDPCRCW
actionable: true
confidence: high
what_worked:
  - "Mirroring the crossref.py / datacite.py shape end-to-end made the new resolver mechanical: same Fetcher injection pattern, same ResolvedArtifact list, same writer.write_source idempotency hook. The Google Books primary returned every field the source schema needs (title, authors[], publishedDate → year, publisher) for isbn:9780471893844 on the first try, so the Open Library fallback was never exercised live — wiring it as a strict fallback (only when items is missing/empty) keeps the primary path simple."
  - "Choosing url=urn:isbn:<isbn> as the canonical idempotency key for isbn-resolved sources avoided touching slugs.py at all: writer._existing_for already calls find_existing_by_url, and the urn:isbn: form is provider-agnostic (so a Google Books hit and an Open Library hit for the same ISBN collapse into the same src-* dir on re-fetch). The schema's url field is plain string|null with no format URI constraint, so the urn: form passes validation."
  - "Live acceptance test (uv run coc acquire isbn:9780471893844) registered src-000009--oscillations-and-traveling-waves-in-chemical-systems/ with title=Oscillations and traveling waves in chemical systems, authors=[Richard J. Field, Mária Burger], year=1985, kind=book, license=null, hash present — every field the task's acceptance test #4 enumerated. coc validate exits 0 across the repo. This single registration also unblocks tsk-20260425-000013 (the in-flight acquire-source for the same isbn) idempotently when it re-leases."
blockers: []
proposed_improvements:
  - target: tests/test_sources.py
    change: >
      Update test_dispatch_rejects_isbn_for_now (currently asserts
      resolve('isbn:9780815345053') raises UnsupportedRefError) — after
      this run the assertion fails because the dispatch now routes isbn:
      to isbn_books.resolve. Replace it with (a) a happy-path unit test
      for isbn_books.resolve using a fake fetcher with a Google Books
      response (asserting kind=book, license=null, url=urn:isbn:..., one
      metadata.json artifact, slug from title), (b) a fallback test
      where the Google Books fetcher returns totalItems:0 and the Open
      Library fetcher returns a populated ISBN:<isbn> entry, and (c) a
      not-found test where both providers return empty and NotFoundError
      is raised. Same fake-fetcher infra the crossref/arxiv/web tests
      already use. Couldn't fix in this run because tests/ was not in
      this task's output_targets — same scoping pattern as the DataCite
      retro flagged. The breakage is currently the only failing test
      (1 fail / 13 pass on tests/test_sources.py).
    rationale: >
      The test now reads as a stale invariant rather than a check; CI
      and local pytest will be red on the next pull. Fixing it inline
      would have been one edit, but output_targets discipline forced
      deferral. A follow-up review-records task is the right vehicle.
    severity: major
  - target: src/coc/queue.py
    change: >
      Teach _source_ref_resolves to recognize registered isbn sources.
      Today line 357-358 unconditionally returns False for isbn: refs
      (the comment cites "no resolver today" — now stale). Two viable
      shapes: (a) add find_existing_by_isbn in slugs.py that scans for
      url == 'urn:isbn:<isbn>' and call it from queue.py, or (b) reuse
      find_existing_by_url with the urn:isbn: form composed inline. The
      same-file test test_sweep_blocked_sources_resolved_isbn_refs_never_resolve
      will need to flip its expectation (registered isbn sources should
      resolve via sources-resolved unblocks, not stay blocked forever).
    rationale: >
      Without this, the sources-resolved unblock kind silently
      misclassifies isbn refs as unresolved even after their src-* dir
      lands, so blocked profile-system / extract-observations tasks
      with isbn source_refs cannot use the sources-resolved unblock
      shape — they must rely on task-complete chained off the
      acquire-source task instead. That works for the current 5
      blocked acquire-source tasks (whose unblock fields point at
      task-complete already), but the queue's resolution-truth
      function is now inconsistent with the resolver surface.
    severity: moderate
  - target: skills/plan-backlog/SKILL.md
    change: >
      The Tier-0.75 source-debt sweep currently picks the *last*
      acquire-source task as the unblock target when N>1 missing refs
      exist on a blocked task (multi-source caveat, lines ~155-164).
      Now that isbn: is a real resolver, more profile-system tasks
      will accumulate ISBNs alongside DOIs (the four blocked
      profile-system tasks already in queue all carry mixed
      doi:+isbn: refs). Consider noting in the skill that the
      multi-source convergence cost (⌈N/3⌉ plan-backlog passes) is
      now hit more often, and recommend the future sources-resolved
      unblock kind as the proper fix once queue.py recognizes
      registered isbn sources (paired with the queue.py improvement
      above).
    rationale: >
      Documentation-only nudge to keep the convergence story honest
      now that isbn: refs are first-class. No code change needed in
      this skill — just a sentence to align the multi-source caveat
      with the broader resolver coverage.
    severity: minor
---

Implemented the isbn resolver prescribed by the task notes (which
themselves recapped retro-01KQ3BSE00BN3Q0Q4GAYK26PAB on
tsk-20260425-000013). New module
[src/coc/sources/isbn_books.py](../../../../src/coc/sources/isbn_books.py)
mirrors the crossref/datacite resolver shape: pure (no filesystem
writes), Fetcher-injectable, returns ResolvedSource. Google Books primary,
Open Library fallback only on empty items. dispatch.py now routes
isbn: to it instead of raising UnsupportedRefError. Live acquire of
isbn:9780471893844 wrote src-000009 with the correct bibliographic
metadata for the Field & Burger (1985) BZ-reaction handbook — exactly
the source that tsk-20260423-000019 / tsk-20260424-000001 need to
unblock the BZ profile-system work.

Five other blocked acquire-source tasks (000013, 000014, 000021,
000022, 000023) for distinct ISBNs are now functionally executable,
but their state remains `blocked` until a human or sweep moves them
back to ready/. They were marked `blocked` with reason
`unsupported-ref` and have no `unblock` field, so coc advance won't
auto-unblock them. A follow-up `review-records` task could either
(a) flip their state to ready/ directly, or (b) extend coc advance
with an "unsupported-ref + resolver-now-exists" sweep. Either is out
of scope here.

The major-severity test proposal is the only true follow-up needed
to keep CI green; emitting a paired review-records task per the
skill's step 6 procedure.
