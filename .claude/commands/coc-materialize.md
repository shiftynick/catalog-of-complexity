---
description: Rebuild Parquet + DuckDB warehouse from the registry
---

Rebuild the warehouse from canonical registry records.

```bash
uv run coc materialize
```

This writes Parquet tables to `warehouse/parquet/` and loads them into
`warehouse/duckdb/coc.duckdb`. The warehouse directory is git-ignored; it is
fully regenerable from `registry/`.
