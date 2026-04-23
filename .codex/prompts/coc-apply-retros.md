# /coc-apply-retros

Execute one scheduled daily apply-retros pass of the Catalog of
Complexity.

Follow the master prompt at
[prompts/apply-retros-run.md](../../prompts/apply-retros-run.md)
exactly and completely.

Do not edit AGENTS.md, SKILL.md, schemas, or prompts directly — this run
only clusters proposals into `review-records` task manifests. Edits land
when those manifests are promoted and executed by subsequent autonomous
runs.

Before starting, verify preflight per the master prompt:

```bash
uv run coc validate
git status --porcelain
```

Then proceed as directed by the master prompt.
