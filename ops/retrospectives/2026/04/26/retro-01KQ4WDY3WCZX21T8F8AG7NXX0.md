---
retro_id: retro-01KQ4WDY3WCZX21T8F8AG7NXX0
task_id: tsk-20260425-000011
run_id: run-01kq4wc0t1j63wv59e29exjma3
skill: acquire-source
timestamp: '2026-04-26T12:33:30Z'
agent: claude-code/Shiftor/local
actionable: false
confidence: high
what_worked:
  - "`coc acquire doi:10.18434/T4W30F` correctly reported an idempotent match against the pre-existing src-000008 (NIST Atomic Spectra Database) registered on 2026-04-26T03:10:13Z; no new directory was created and no raw/ artifact was clobbered. The skill's idempotency contract held cleanly even though the queued acquire-source task pre-dated the actual acquisition by ~9 hours."
  - "Tier-0.75 preflight sweep again emitted zero new acquire-source tasks: all 7 unique missing prefixed refs across ready/ and blocked/ are already covered by existing 'Source debt: <ref>.' notes (six in ready/, this one which was just resolved). Idempotency rule prevented duplicate emission as designed."
blockers: []
proposed_improvements: []
---

Routine idempotent acquire-source iteration. The DOI was already registered as
src-000008 from an earlier pass on the same date; the queued task remained in
ready/ because the pre-existing acquisition was performed out-of-band rather
than by leasing this manifest. Stop conditions met on the first try (existing
src match, source.yaml validates, raw/ non-empty with metadata.json,
retrieved_at + hash + kind=dataset all consistent with the dataset-DOI
DataCite-fallback resolver path described in the SKILL.md). Note: completing
this acquire-source does *not* unblock the only blocked task that referenced
this DOI (tsk-20260423-000019 hydrogen-atom profile), because that task lists
two additional unregistered isbn refs (9780582356924, 9781107189638) covered
by separate ready acquire-source tasks; only the last-emitted unblock anchor
will fire. No friction in prompt stack, schemas, or skill — extends the
recent low-noise streak of acquire-source retros (retro-01KQ4V4DFZ...,
retro-01KQ4QTE2W..., retro-01KQ4QS81M..., retro-01KQ4QMYH7...).
