# Framework reference

These four documents are the **conceptual reference** for the Catalog of
Complexity project. They are not project state — they don't change as
the registry grows. They define what the catalog is *for* and supply
the source material for the v0.1 bootstrap seed.

| File | Purpose | Primary use |
|---|---|---|
| [01-discovery-framework.md](01-discovery-framework.md) | What discoveries the catalog is meant to enable: universality classes, tradeoff frontiers, failure-mode families, latent complexity coordinates. | Anchors the schema design and analysis goals. |
| [02-candidate-systems-catalog.md](02-candidate-systems-catalog.md) | ~600 candidate complex systems organized by domain, with priority tags (P0–P3, C). | Source manifest for `config/bootstrap_seed.yaml`. |
| [03-metric-ontology.md](03-metric-ontology.md) | 19 metric/attribute groups, core required set, maturity levels, candidate periodic-table axes. | Drives the metric-family taxonomy and per-metric schema fields. |
| [04-prior-art-sources.md](04-prior-art-sources.md) | 27 prior-art sources (Boulding, Simon, Lloyd, Bar-Yam, Atlas of Economic Complexity, etc.) with comparison rubric. | Pre-registered references for `define-metrics` and `analyze-archetypes`. |

These files are **read-only reference**. To act on them:

- Adjust the schema in `schemas/`.
- Edit the taxonomy under `taxonomy/source/`.
- Author or extend `config/bootstrap_seed.yaml`.
- Cite specific sections from skills (`skills/<name>/SKILL.md`).

Do not edit these files in place to capture project decisions — that
goes in `AGENTS.md`, the relevant `SKILL.md`, or the schema.
