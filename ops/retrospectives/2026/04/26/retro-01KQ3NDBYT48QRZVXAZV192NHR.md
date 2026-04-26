---
retro_id: retro-01KQ3NDBYT48QRZVXAZV192NHR
task_id: tsk-20260425-000025
run_id: run-01KQ3NDBYT48QRZVXAZV192NHQ
skill: acquire-source
timestamp: '2026-04-26T01:11:20Z'
agent: claude-code/scheduled/coc-auto-run
actionable: false
confidence: high
what_worked:
  - "Metadata-only fallback path worked cleanly: Unpaywall reported no OA, the resolver wrote source.yaml + metadata.json + unpaywall.json without raw PDF, and coc validate accepted the record."
  - "Idempotent slug derivation produced a sensible directory name from Crossref title even when the cited paper context (E. coli MSB anchor) differs from the reannotation paper's actual scope; the src-id remains the canonical handle, so downstream tasks aren't affected."
blockers: []
proposed_improvements: []
---

Routine acquire-source for an MSB DOI that resolved to a paywalled
genome-reannotation paper rather than a flux-balance modeling paper —
the resolver doesn't disambiguate between the cited context and the
actual record. Acceptable: src-id is the durable handle, and downstream
review-records / extract-observations passes will surface any mismatch.
No friction worth flagging.
