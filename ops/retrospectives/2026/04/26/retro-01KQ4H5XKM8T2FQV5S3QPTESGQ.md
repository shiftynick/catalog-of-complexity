---
retro_id: retro-01KQ4H5XKM8T2FQV5S3QPTESGQ
task_id: tsk-20260426-000009
run_id: run-01kq4h5xkm8t2fqv5s3qptesgp
skill: acquire-source
timestamp: 2026-04-26T09:17:45Z
agent: claude-code/Shiftor/auto
actionable: false
confidence: high
what_worked:
  - "Second consecutive `coc acquire` succeeded on the first Crossref + Unpaywall round-trip (Science DOI, no DataCite fallback). Two acquire-source iterations in this invocation each ran in well under one minute of wall-clock - the per-task batching savings the autonomous-run prompt anticipates are visible in practice."
  - "The pairing of acquire-source (this iteration + previous iteration 2) with `unblock: kind: sources-resolved` on the consumer profile-system task gives a clean, schema-enforced handoff: no manual coordination needed beyond emitting the right unblock kind at proposal time. The microbiome profile-system task (tsk-20260426-000005) is now satisfied and will be picked up by the next preflight `coc advance`."
blockers: []
proposed_improvements: []
---

## Summary

Acquired DOI 10.1126/science.1224203 (Costello et al. 2012,
"The Application of Ecological Theory Toward an Understanding of the
Human Microbiome" Science 336(6086):1255-1262). Crossref + Unpaywall
resolution succeeded; registered as src-000011. Combined with
src-000010 (this invocation's iteration 2), the sources-resolved
unblock on microbiome profile-system tsk-20260426-000005 is now
satisfied; next preflight `coc advance` will move it back to ready/.
