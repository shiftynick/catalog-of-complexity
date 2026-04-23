---
description: Execute one autonomous run (pick a task, execute, retrospect, commit locally)
---

You are beginning a scheduled autonomous run of the Catalog of Complexity.
Follow the master prompt at [prompts/autonomous-run.md](../../prompts/autonomous-run.md)
exactly and completely.

Do not chain multiple tasks. One run = one task (Branch A) or one empty-queue
branch (Branch B), followed by the retrospective, followed by one local
commit. Do not push.

Before starting, verify preflight per the master prompt:

```bash
uv run coc validate
git status --porcelain
```

Then proceed as directed by the master prompt.
