---
description: Build a release snapshot with Data Package + RO-Crate metadata
argument-hint: "[YYYY-MM-DD]"
---

Build a release snapshot.

```bash
uv run coc release $ARGUMENTS
```

If no date is given, today's UTC date is used. The snapshot is written to
`releases/snapshot-<date>/` and contains `datapackage.json`,
`ro-crate-metadata.json`, `manifest.md`, and a copy of the current Parquet
warehouse.
