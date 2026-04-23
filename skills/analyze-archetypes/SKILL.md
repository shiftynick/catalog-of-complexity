---
name: analyze-archetypes
description: Derive cross-system structural patterns from the system x metric matrix — similarity edges, clusters, and candidate archetypes. SCAFFOLDED ONLY; disabled until registry breadth justifies enabling.
status: disabled
inputs:
  - 'min_observations — integer. Minimum validated observations required to enable this skill. Default 200.'
  - 'min_system_classes — integer. Minimum distinct `system-class:*` slugs with >=3 validated observations. Default 5.'
  - 'feature_metrics — list of `mtr-*` ids used as features. Default is all active metrics with applicability satisfied by the candidate systems.'
outputs:
  - 'Rows in `warehouse/parquet/edges.parquet` (similarity edges between systems).'
  - 'A cluster-label column added to a derived table (method tbd at enable time).'
  - 'An analysis report under `ops/runs/YYYY/MM/DD/<run-id>/archetypes.md` with cluster summaries, feature importance, and candidate archetype labels.'
stop_conditions:
  - 'Prerequisites (see `inputs`) are met.'
  - 'Derived tables are produced and row counts are plausible.'
---

## Status: disabled

This skill is scaffolded to reserve its slot in the skill roster, but it must not be invoked until the registry has enough breadth for clustering to be meaningful. The `coc` CLI and `AGENTS.md` reference it so future work has a home; the actual procedure is deliberately unwritten.

## Preconditions for enabling

Flip `status: active` in this frontmatter only when **all** of the following hold:

1. `SELECT COUNT(*) FROM observations WHERE review_state IN ('validated', 'auto-validated')` >= `min_observations` (default 200). Both states count because auto-validated records are the default usable state under the current autonomous policy; strict human-only counts use `review_state = 'validated'`.
2. `SELECT COUNT(DISTINCT system_class) FROM ...` (joining systems and classes) shows at least `min_system_classes` classes each with >=3 usable (validated or auto-validated) observations.
3. At least one `metric-family:*` has coverage across 3+ distinct `system-domain:*` slugs.
4. A separate `setup-repo` task has landed the analysis dependencies (e.g. `scikit-learn`, `networkx`, `igraph`) in `pyproject.toml`. These are **not** bootstrap dependencies — adding them before this skill is enabled is premature.

## When enabled, the procedure will

(Placeholder — detailed procedure to be written at enable time. Expected shape:)

1. Build the feature matrix from `v_system_metric_matrix`, coercing heterogeneous `value_kind` values to a common numeric scale per metric.
2. Compute pairwise similarity (cosine, Euclidean with feature normalization, or mixed-type Gower — choice documented in the run report).
3. Threshold similarity into edges; write to `warehouse/parquet/edges.parquet` with columns `source_system, target_system, weight, method`.
4. Run clustering (hierarchical or community detection on the edge graph).
5. Inspect cluster composition; surface candidate archetype labels for reviewer approval.

## Why it is disabled now

Clustering over a sparse matrix of 1 system x 1 metric produces noise, not signal. Enabling this skill early would bake arbitrary archetype labels into the catalog before the evidence base supports them.

## References

- [warehouse/sql/similarity_edges.sql](../../warehouse/sql/similarity_edges.sql) — current passthrough; will become non-trivial when enabled.
- [BOOTSTRAP_PLAN.md](../../BOOTSTRAP_PLAN.md) — §2 "What this plan changes" row for archetypes.
