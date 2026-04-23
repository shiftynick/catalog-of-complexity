---
description: Validate registry + taxonomy against JSON Schemas
argument-hint: "[path]"
---

Run the Catalog of Complexity validator against $ARGUMENTS (or the whole
repo if no path given).

```bash
uv run coc validate $ARGUMENTS
```

On failure, read the reported path, open the file, compare against the
relevant schema under `schemas/`, and fix the structural issue. Do not
suppress errors.
