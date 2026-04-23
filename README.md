# Catalog of Complexity

A comparative research operating system for complex systems.

The goal: build a provenance-rich, machine-queryable catalog of complex systems
across domains — biological, ecological, technological, social, physical,
computational, economic, cognitive — quantify them against a controlled
vocabulary of metric families, and surface cross-domain structural and dynamical
patterns.

## Status

Bootstrapping. See [BOOTSTRAP_PLAN.md](BOOTSTRAP_PLAN.md) for the current plan
and [AGENTS.md](AGENTS.md) for the operating model that both Claude Code and
OpenAI Codex follow when working in this repo.

## Quickstart

Requires Python 3.11+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync
uv run coc --help
uv run pytest
```

## Layout at a glance

- `registry/` — canonical systems, metrics, sources, observations (source of truth)
- `taxonomy/` — controlled vocabularies (domains, classes, metric families)
- `schemas/` — JSON Schema Draft 2020-12 definitions
- `ops/` — task queue, run reports, event logs
- `warehouse/` — derived Parquet + DuckDB (regenerable, not canonical)
- `releases/` — Data Package / RO-Crate snapshots
- `skills/` — reusable agent workflows (read by both Claude Code and Codex)
- `prompts/` — role prompts parameterized by the task envelope
- `qc/` — fixtures, evals, goldens, reports
- `scripts/` — thin CLI wrappers over `src/coc/*`

## License

Code: [MIT](LICENSE). Data and non-code content: [CC BY 4.0](LICENSE-DATA).
