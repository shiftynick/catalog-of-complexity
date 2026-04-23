# Rubric — Network modularity

## What to capture

- The **graph construction** (nodes, edges, weight rule). Modularity is
  defined on a specific graph, not on "the system" in the abstract.
- The **community detection algorithm** (e.g. Louvain, Leiden, Infomap).
  Different algorithms can produce materially different values on the same
  graph.
- The **number of communities** found, where the source reports it.

## Acceptance bar

- Reject numeric claims that don't name a graph construction.
- Prefer values reported with error bars or multiple-run statistics over
  point estimates.

## Downgrade to proxy

When the source reports "modular structure" or "community organization"
without a numeric Q, record the observation with `value: null`, an explicit
`value_kind: proxy`, and a `method` string summarizing the qualitative
claim.
