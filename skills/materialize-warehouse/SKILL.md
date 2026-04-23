---
name: materialize-warehouse
description: Rebuild the Parquet + DuckDB warehouse from the canonical registry. The warehouse is derivable; this skill is the canonical derivation path.
status: active
inputs:
  - 'full_rebuild — boolean. If true, delete `warehouse/parquet/` and `warehouse/duckdb/` before rebuilding. Default true (only false is meaningful if partial-rebuild is added later).'
  - 'post_checks — list of SQL sanity queries to run against the new DuckDB file. Default queries are in the Procedure section below.'
outputs:
  - '`warehouse/parquet/{systems,metrics,sources,observations,evidence,applicability,edges}.parquet`'
  - '`warehouse/duckdb/coc.duckdb` with all tables loaded and all views in `warehouse/sql/*.sql` created.'
  - 'Run report at `ops/runs/YYYY/MM/DD/<run-id>/run.json` with per-table row counts in `notes`.'
stop_conditions:
  - '`uv run coc materialize` returns zero exit code.'
  - 'Each post-check query returns the expected shape (non-empty where expected; correct coverage ratios).'
---

## When to use

Use this skill whenever the registry has changed and a fresh warehouse is required for analysis. Trigger:

- A batch of `extract-observations` or `profile-system` tasks has completed.
- A release task is about to run and needs a fresh warehouse as input.
- A similarity/archetype analysis task is queued behind this one.

Do **not** hand-edit anything under `warehouse/`. Do **not** commit `warehouse/parquet/` or `warehouse/duckdb/` — both are gitignored.

## Preconditions

- `uv run coc validate` passes on the entire registry. A warehouse built from invalid records is worse than no warehouse.
- Taxonomy exports are current (the warehouse does not consume exports directly but downstream consumers do).

## Procedure

1. Run `uv run coc validate` as a pre-flight. If it fails, block the task — do not materialize over invalid records.
2. Run `uv run coc materialize`. The CLI prints per-table row counts.
3. Run post-checks against the new `warehouse/duckdb/coc.duckdb`:
   - `SELECT systems_total, metrics_total, observations_total, usable_coverage, human_validated_coverage FROM v_coverage_summary;`
   - `SELECT COUNT(*) FROM v_system_metric_matrix WHERE value_numeric IS NOT NULL OR value_text IS NOT NULL;`
   - `SELECT metric_family, systems_with_observation, observations_validated, observations_auto_validated FROM v_coverage_by_family ORDER BY observations_validated DESC;`
4. If any post-check returns an unexpected shape (e.g. usable_coverage = 0.0 when the registry has validated or auto-validated observations), block the task and investigate.
5. Append a run report: per-table row counts, post-check results, any anomalies.

## Output shape

- `warehouse/parquet/*.parquet` — one file per logical table. Row counts match the registry's records across all `review_state` values.
- `warehouse/duckdb/coc.duckdb` — DuckDB file readable via `duckdb warehouse/duckdb/coc.duckdb` or via `coc.warehouse.query()`.

## Block or fail when

- Pre-flight `coc validate` fails — block. Fix registry first.
- Any post-check query errors (SQL syntax, missing view) — investigate `warehouse/sql/` for drift from `src/coc/warehouse.py`.
- Row counts are lower than the registry has records — investigate JSONL parsing or dedup logic before shipping.

## References

- [src/coc/warehouse.py](../../src/coc/warehouse.py)
- [warehouse/sql/](../../warehouse/sql/) — view definitions; must be compatible with the `coc.duckdb` loader.
