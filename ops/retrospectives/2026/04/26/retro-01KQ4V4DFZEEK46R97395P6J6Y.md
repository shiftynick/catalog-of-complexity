---
retro_id: retro-01KQ4V4DFZEEK46R97395P6J6Y
task_id: tsk-20260426-000015
run_id: run-01KQ4V34FK2XBB5SFCK9WZATWK
skill: acquire-source
timestamp: '2026-04-26T12:09:30Z'
agent: claude-code/Shiftor/local
actionable: false
confidence: high
what_worked:
  - "Crossref + Unpaywall path resolved doi:10.1186/1745-6150-5-7 cleanly and pulled paper.pdf as well as metadata. Biology Direct (BMC) is a known fully-OA venue, so paper.pdf was retrievable; the resolver still wrote license=null because Unpaywall didn't return a license URL on this DOI — a fixable upstream metadata gap, not a resolver bug."
  - "Tier-0.75 preflight sweep correctly emitted zero new acquire-source tasks: all unmet prefixed refs across the queues are already covered by existing acquire-source tasks (one in ready/, the rest by the 'Source debt: <ref>.' notes idempotency rule). The expected next state is that this iteration's completion lets `coc advance` flip blocked tsk-20260426-000006 (profile-system eukaryotic-cell, unblock kind=task-complete tied to tsk-20260426-000015) back to ready/."
blockers: []
proposed_improvements: []
---

Routine DOI acquisition for Cavalier-Smith 2010 (Origin of the cell nucleus,
mitosis and sex). Fourth consecutive acquire-source iteration for type-level
biological sources in this micro-cycle, and the unblock-anchor for the
eukaryotic-cell profile-system task. The skill's stop conditions were met on
the first try: source.yaml validates, raw/ contains metadata.json,
unpaywall.json, and paper.pdf, and the SHA-256 hash is set. With src-000016
registered, the next invocation's preflight `coc advance` should move
tsk-20260426-000006 back to ready/ and the eukaryotic-cell profile can run.
No friction in the prompt stack, schemas, or skill — keeping the retro
non-actionable consistent with the recent run of low-noise acquire-source
retros (retro-01KQ4QMYH7..., retro-01KQ4QS81M..., retro-01KQ4QTE2W...).
