---
description: Scaffold a new task manifest under ops/tasks/inbox/
argument-hint: "<skill> <one-line-description>"
---

Create a new task manifest for skill $1 describing: $2.

Use the schema at `schemas/task.schema.json` and the example under
`ops/tasks/ready/` as a template. Write the file to `ops/tasks/inbox/` with a
task ID of the form `tsk-YYYYMMDD-NNNNNN`. Fill in `system_id`, `metric_ids`,
`source_refs`, `output_targets`, and `acceptance_tests` explicitly. Leave
`state: inbox` — a human or reviewer promotes it to `ready`.
