<!--
Thank you for contributing to the Catalog of Complexity.

Before opening: read AGENTS.md. The quality bar there is not optional.
-->

## Summary

<!-- What does this PR change? One to three sentences. -->

## Scope

- [ ] Registry records (systems, metrics, sources, observations)
- [ ] Taxonomy (domains, classes, families, evidence types)
- [ ] Schemas
- [ ] CLI / `src/coc/*`
- [ ] Skills / prompts
- [ ] QC (fixtures, evals, goldens)
- [ ] CI / workflows / repo tooling
- [ ] Docs

## Linked task manifests / issues

<!-- e.g. ops/tasks/done/tsk-20260422-000042.yaml, fixes #123 -->

## Quality bar (from AGENTS.md)

- [ ] `uv run coc validate` passes on everything changed.
- [ ] `uv run pytest` passes locally.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] Every new observation carries `value_kind`, `confidence`, and at least one resolvable `evidence_ref`.
- [ ] Every new or edited metric declares applicability conditions.
- [ ] Every new system has `boundary`, `components`, `interaction_types`, and `scales`.
- [ ] All taxonomy references resolve against `taxonomy/source/*.yaml`; no ad-hoc slugs.
- [ ] No uncited numeric claims in canonical records.
- [ ] No files written under `registry/sources/*/raw/` or `warehouse/`.
- [ ] If a task was executed, a run report exists under `ops/runs/YYYY/MM/DD/` and an event was appended.

## Release / warehouse impact

- [ ] No changes that require re-materializing the warehouse, OR
- [ ] Re-materialize verified locally via `uv run coc materialize` (warehouse diff reviewed).

## Notes for reviewer

<!-- Anything non-obvious, tradeoffs considered, or follow-up tasks proposed. -->
