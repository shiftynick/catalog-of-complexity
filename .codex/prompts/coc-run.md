# /coc-run — Autonomous Run (Codex)

Execute one autonomous run of the Catalog of Complexity. Follow the master
prompt at [prompts/autonomous-run.md](../../prompts/autonomous-run.md)
exactly and completely.

One run = one task (Branch A) or one empty-queue branch (Branch B), followed
by the retrospective, followed by one local commit. Do not push. Do not
chain further work.

## Preflight

```bash
uv run coc validate
git status --porcelain
```

Both must be clean. If either fails, abort per the master prompt's Preflight
section and write a `run.aborted` event.

## Invoke

Read [prompts/autonomous-run.md](../../prompts/autonomous-run.md) and execute
it. Respect [AGENTS.md](../../AGENTS.md) non-negotiables at every step.
