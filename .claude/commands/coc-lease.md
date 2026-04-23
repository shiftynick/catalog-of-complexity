---
description: Lease a task from the ready queue
argument-hint: "<task-id>"
---

Atomically claim task $ARGUMENTS (moves it from `ops/tasks/ready/` to
`ops/tasks/leased/` and writes a lease record).

```bash
uv run coc lease $ARGUMENTS
```

After leasing, read the task manifest at `ops/tasks/leased/$ARGUMENTS.yaml`
and the active skill it references. Do not begin writing outputs until both
are read.
