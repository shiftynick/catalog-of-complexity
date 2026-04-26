---
retro_id: retro-01KQ4H3TRYSWBDDYG17WTABA1M
task_id: tsk-20260426-000008
run_id: run-01kq4h37fgx33fph2kjexheepe
skill: acquire-source
timestamp: 2026-04-26T09:15:45Z
agent: claude-code/Shiftor/auto
actionable: false
confidence: high
what_worked:
  - "`coc acquire doi:10.1073/pnas.1218525110` succeeded on the first Crossref + Unpaywall round-trip. Source registered as src-000010 in one shot, no fallback to DataCite needed."
  - "The acquire-source task was fully decoupled from the upstream microbiome profile-system task: this run did not have to read or reason about how the registered source will be consumed; the sources-resolved unblock kind on tsk-20260426-000005 will fire on a future preflight `coc advance` once the second ref (doi:10.1126/science.1224203) also lands."
blockers: []
proposed_improvements: []
---

## Summary

Acquired DOI 10.1073/pnas.1218525110 (McFall-Ngai et al. 2013,
"Animals in a bacterial world, a new imperative for the life
sciences" PNAS 110(9):3229-3236). Crossref + Unpaywall resolution
succeeded; registered as src-000010. One of the two refs blocking
microbiome profile-system tsk-20260426-000005 (the other,
doi:10.1126/science.1224203, is the next ready acquire-source task
tsk-20260426-000009 — likely Iteration 3 of this invocation).
