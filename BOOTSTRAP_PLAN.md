# Catalog of Complexity — Bootstrap Plan

Concrete, executable plan for standing up the repository described in the second proposal
(`~/Downloads/deep-research-report.md`). This plan pins the runtime, strips research-report
artifacts, and wires in dual support for **Claude Code** and **OpenAI Codex** with GitHub
as the collaboration substrate.

This document is the charter for the `setup-repo` skill. The first bootstrap task
(`tsk-bootstrap-000001`) will execute Phases 0–12 in order.

---

## 1. Runtime & dependencies

- **Language:** Python 3.11+
- **Package manager:** [`uv`](https://docs.astral.sh/uv/) (Astral)
- **Source of truth:** `pyproject.toml`
- **Virtual env:** `.venv/` managed by `uv`

### `pyproject.toml` (pinned set)

```toml
[project]
name = "catalog-of-complexity"
version = "0.1.0"
description = "Catalog of Complexity: comparative research operating system for complex systems."
requires-python = ">=3.11"
dependencies = [
  "jsonschema>=4.21",       # Draft 2020-12 validation
  "ruamel.yaml>=0.18",      # YAML round-trip with comment preservation
  "pydantic>=2.6",          # typed data contracts mirroring JSON Schemas
  "duckdb>=1.0",            # warehouse engine
  "pyarrow>=15.0",          # Parquet I/O
  "click>=8.1",             # CLI
  "rich>=13.7",             # human-readable CLI output
  "rdflib>=7.0",            # SKOS/Turtle export
  "frictionless>=5.16",     # Data Package build + validation
  "rocrate>=0.11",          # RO-Crate packaging
  "python-dateutil>=2.9",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0",
  "pytest-cov>=5.0",
  "ruff>=0.3",
  "mypy>=1.8",
  "pre-commit>=3.7",
]

[project.scripts]
coc = "coc.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/coc"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### CLI surface (`coc …`)

| Subcommand | Purpose |
|------------|---------|
| `coc validate [path]` | Validate registry records + taxonomies against schemas |
| `coc lease <task>` | Atomically move a task from `ready/` → `leased/` |
| `coc heartbeat <task>` | Update lease liveness timestamp |
| `coc complete <task>` | Validate outputs, append event, move to `review/` or `done/` |
| `coc requeue` | Requeue stale leases past their TTL |
| `coc materialize` | Rebuild Parquet + DuckDB from registry |
| `coc release [--date]` | Build a `releases/snapshot-*` with Data Package + RO-Crate |
| `coc export-taxonomy` | Emit SKOS Turtle + JSON labels to `taxonomy/exports/` |
| `coc eval [skill]` | Run QC evals / goldens |

### Deferred to later

- **DVC** — skipped at bootstrap. Large raw sources go through **Git LFS** (`.gitattributes`).
  Revisit when corpus exceeds ~5 GB or when we need cache-backed pipelines.
- **Firecrawl / web-fetch tooling** — not a bootstrap dependency. Agents use their
  native web-fetch tools. Add a dedicated scraper later if repeated patterns emerge.
- **OpenTelemetry / AgentTrace** — out of scope for bootstrap. Event JSONL + run reports
  are the initial audit surface.

---

## 2. Dual-agent support (Claude Code + OpenAI Codex)

Canonical instructions live in `AGENTS.md`. Tool-specific config lives under `.codex/`
and `.claude/`. The generic `skills/` directory is framework-agnostic: both agents are
instructed by `AGENTS.md` to read `skills/<name>/SKILL.md` before performing tasks of
that type. No native skill registration is required at bootstrap.

| File | Purpose | Consumer |
|------|---------|----------|
| `AGENTS.md` | Canonical agent rules and operating model | Both |
| `CLAUDE.md` | One-liner: "See [AGENTS.md](AGENTS.md)" | Claude Code |
| `.codex/config.toml` | Codex approval mode, model, allowed shells | Codex |
| `.claude/settings.json` | Claude Code permissions + hooks | Claude Code |
| `.claude/commands/*.md` | Slash commands wrapping the CLI | Claude Code |
| `skills/*/SKILL.md` | Generic workflow skills referenced from AGENTS.md | Both |
| `prompts/*.md` | Role/task prompts parameterized by the task envelope | Both |
| `.env.example` | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` placeholders | Both |

### `.codex/config.toml` (initial)

```toml
[project]
name = "catalog-of-complexity"

[approval]
# Require approval for anything that mutates registry/, releases/, or pushes git state.
mode = "auto-for-safe-read-only"

[[approval.write_paths]]
path = "workspace/**"
auto = true

[[approval.write_paths]]
path = "ops/**"
auto = true

[[approval.write_paths]]
path = "registry/**"
auto = false  # require explicit approval

[[approval.write_paths]]
path = "warehouse/**"
auto = false

[model]
default = "gpt-5"  # adjust to whatever the current Codex-supported ID is
```

### `.claude/settings.json` (initial)

```json
{
  "permissions": {
    "allow": [
      "Bash(uv run coc:*)",
      "Bash(uv sync)",
      "Bash(uv run pytest*)",
      "Bash(uv run python scripts/*)",
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log*)"
    ],
    "ask": [
      "Bash(git push*)",
      "Bash(gh pr create*)"
    ]
  },
  "model": "claude-opus-4-7"
}
```

### `.claude/commands/` (slash commands)

- `coc-validate.md` — `uv run coc validate`
- `coc-lease.md` — `uv run coc lease $ARG`
- `coc-materialize.md` — `uv run coc materialize`
- `coc-release.md` — `uv run coc release`
- `coc-new-task.md` — scaffolds a task manifest from template

---

## 3. Repository layout

Final layout matches the second proposal with these additions: `src/coc/`, `tests/`,
`.github/`, `.env.example`, `.pre-commit-config.yaml`, `.gitattributes`.

```text
catalog-of-complexity/
├── AGENTS.md
├── CLAUDE.md                    # one-liner pointer to AGENTS.md
├── README.md
├── LICENSE                      # MIT for code (see open decisions)
├── LICENSE-DATA                 # CC-BY-4.0 for data (see open decisions)
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── .gitattributes               # LFS rules
├── .pre-commit-config.yaml
├── .codex/
│   └── config.toml
├── .claude/
│   ├── settings.json
│   └── commands/
├── .github/
│   ├── workflows/
│   │   ├── validate.yml
│   │   ├── ci.yml
│   │   └── materialize.yml      # optional, nightly
│   ├── ISSUE_TEMPLATE/
│   │   ├── new-system.yml
│   │   ├── new-metric.yml
│   │   └── bug.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
├── src/
│   └── coc/
│       ├── __init__.py
│       ├── cli.py               # click entrypoint
│       ├── models.py            # pydantic mirrors of JSON Schemas
│       ├── schemas.py           # schema loader + validator
│       ├── registry.py          # CRUD over registry/
│       ├── queue.py             # lease / heartbeat / complete
│       ├── warehouse.py         # materialize to parquet/duckdb
│       ├── release.py           # datapackage + ro-crate build
│       ├── taxonomy.py          # SKOS export
│       └── events.py            # JSONL append helpers
├── tests/
│   ├── conftest.py
│   ├── test_schemas.py
│   ├── test_queue.py
│   ├── test_warehouse.py
│   └── fixtures/
├── schemas/                     # JSON Schema Draft 2020-12
│   ├── system.schema.json
│   ├── metric.schema.json
│   ├── source.schema.json
│   ├── observation.schema.json
│   ├── task.schema.json
│   ├── run.schema.json
│   └── event.schema.json
├── prompts/
│   ├── task-envelope.md
│   ├── scout-systems.md
│   ├── define-metrics.md
│   ├── profile-system.md
│   ├── extract-observations.md
│   ├── review-records.md
│   └── analyze-archetypes.md
├── skills/
│   ├── setup-repo/
│   ├── scout-systems/
│   ├── define-metrics/
│   ├── profile-system/
│   ├── extract-observations/
│   ├── review-records/
│   ├── materialize-warehouse/
│   └── analyze-archetypes/      # scaffolded but disabled until data breadth exists
├── taxonomy/
│   ├── source/
│   │   ├── system-domains.yaml
│   │   ├── system-classes.yaml
│   │   ├── metric-families.yaml
│   │   └── evidence-types.yaml
│   └── exports/
├── registry/
│   ├── systems/
│   ├── metrics/
│   ├── sources/
│   └── observations/
├── ops/
│   ├── tasks/{inbox,ready,leased,running,blocked,review,done,failed,archive}/
│   ├── runs/
│   └── events/
│       ├── task-events.jsonl
│       ├── run-events.jsonl
│       └── provenance-events.jsonl
├── warehouse/
│   ├── parquet/                 # git-ignored; regenerable
│   ├── duckdb/                  # git-ignored; regenerable
│   └── sql/
├── qc/
│   ├── fixtures/
│   ├── evals/
│   ├── goldens/
│   └── reports/
├── releases/                    # snapshots; datapackage + optional ro-crate
├── scripts/
│   ├── validate_registry.py
│   ├── lease_task.py
│   ├── heartbeat.py
│   ├── complete_task.py
│   ├── requeue_stale_tasks.py
│   ├── materialize_warehouse.py
│   ├── build_release.py
│   └── export_taxonomy.py
└── workspace/                   # agent scratchpad; git-ignored
```

Scripts in `scripts/` are thin wrappers that delegate to `src/coc/*` — this keeps the
logic importable and testable while still giving agents a stable file-path surface.

---

## 4. Phased execution (each phase must clear its gate)

### Phase 0 — Foundation
1. `uv init` → create `pyproject.toml` with pinned deps above
2. `src/coc/__init__.py`, `src/coc/cli.py` stub (`coc` command prints version)
3. `tests/` scaffolding with one smoke test
4. `.gitignore` (Python + `.venv/`, `warehouse/parquet/`, `warehouse/duckdb/`, `ops/runs/`, `workspace/`, `.env`)
5. `.gitattributes` — LFS for `registry/sources/*/raw/**`, `releases/**/*.parquet`, PDFs
6. `.env.example` with `OPENAI_API_KEY=`, `ANTHROPIC_API_KEY=`
7. `.pre-commit-config.yaml` — ruff, JSON/YAML syntax, trailing whitespace
8. `LICENSE` (MIT) + `LICENSE-DATA` (CC-BY-4.0) — subject to decision #5
9. Initial `README.md` with mission, quickstart, layout summary

**Gate:** `uv sync` succeeds, `uv run coc --version` prints, `uv run pytest` green on smoke test.

### Phase 1 — Agent & IDE configuration
1. `AGENTS.md` — adapted from proposal, citations stripped, tightened for execution
2. `CLAUDE.md` — one line: `See [AGENTS.md](AGENTS.md).`
3. `.codex/config.toml` — content above
4. `.claude/settings.json` — content above
5. `.claude/commands/` — five initial slash commands

**Gate:** Opening repo in Claude Code + Codex both parse config without warnings.
Manual check: `/coc-validate` surfaces in Claude Code slash menu.

### Phase 2 — Schemas & typed models
1. Seven JSON Schema files under `schemas/` (Draft 2020-12, all `$id` set, all `required` set)
2. `src/coc/schemas.py` — schema loader with caching + registry for `$ref` resolution
3. `src/coc/models.py` — Pydantic v2 models mirroring each schema
4. `tests/test_schemas.py` — validates every fixture under `qc/fixtures/` against its schema

**Gate:** `uv run pytest tests/test_schemas.py` green. One intentionally-invalid fixture
under `qc/fixtures/invalid/` fails validation with the expected error.

**Domain enum** (pending decision #1): `ecological, biological, technological, social, physical, computational, economic, cognitive`.

### Phase 3 — Taxonomy seed
1. `taxonomy/source/system-domains.yaml` — the enum above with descriptions
2. `taxonomy/source/system-classes.yaml` — initial ~20 classes across domains
3. `taxonomy/source/metric-families.yaml` — 8 families from proposal
4. `taxonomy/source/evidence-types.yaml` — `direct, derived, proxy, simulation, expert_estimate`
5. `src/coc/taxonomy.py` + `scripts/export_taxonomy.py` → SKOS Turtle + labels.json

**Gate:** `uv run coc export-taxonomy` writes valid Turtle (rdflib round-trips it).

### Phase 4 — Registry sample seeds
1. `registry/systems/sys-000001--amazon-rainforest/` (system.yaml, notes.md, links.yaml)
2. `registry/metrics/mtr-000001--network-modularity/` (metric.yaml, rubric.md, examples.yaml)
3. `registry/sources/src-000001--example-review/` (source.yaml, empty raw/, parsed/, evidence.jsonl)
4. `registry/observations/sys-000001--amazon-rainforest/topology.jsonl` (one record)

**Gate:** `uv run coc validate` passes on all seeds. `git ls-files` shows no LFS
smudge errors.

### Phase 5 — Ops queue
1. All nine `ops/tasks/<state>/` directories with `.gitkeep`
2. `ops/runs/.gitkeep`, `ops/events/*.jsonl` (empty, tracked)
3. `src/coc/queue.py` implementing atomic move (os.rename) for state transitions
4. `src/coc/events.py` with append-JSONL + fsync
5. `scripts/{lease_task,heartbeat,complete_task,requeue_stale_tasks}.py` as thin wrappers
6. Seed `ops/tasks/ready/tsk-bootstrap-dryrun.yaml` (a no-op task)

**Gate:** Dry-run cycle completes:
```
uv run coc lease tsk-bootstrap-dryrun
uv run coc heartbeat tsk-bootstrap-dryrun
uv run coc complete tsk-bootstrap-dryrun --outputs '{}'
```
`ops/events/task-events.jsonl` contains the three transitions.

### Phase 6 — Warehouse materialization
1. `src/coc/warehouse.py` — reads registry, writes Parquet via pyarrow
2. DuckDB table registration from Parquet
3. `warehouse/sql/{latest_observations,system_metric_matrix,similarity_edges,coverage_views}.sql`
4. `scripts/materialize_warehouse.py` wrapper

**Gate:** `uv run coc materialize` produces `warehouse/parquet/*.parquet` and
`warehouse/duckdb/coc.duckdb`. `duckdb -c "SELECT count(*) FROM systems"` returns 1.

### Phase 7 — Skills library (all seven, kept split)
Each skill directory gets `SKILL.md` with YAML frontmatter (`name`, `description`,
`inputs`, `outputs`, `stop_conditions`) plus optional `scripts/` and `references/`.

1. `skills/setup-repo/` (captures THIS document)
2. `skills/scout-systems/`
3. `skills/define-metrics/`
4. `skills/profile-system/`
5. `skills/extract-observations/`
6. `skills/review-records/`
7. `skills/materialize-warehouse/`
8. `skills/analyze-archetypes/` (scaffolded, SKILL.md marks it `status: disabled`)

**Gate:** `scripts/lint_skills.py` verifies frontmatter completeness; `AGENTS.md`
references all 8 by path.

### Phase 8 — Prompt library
1. `prompts/task-envelope.md` — canonical wrapper with `{ROLE}`, `{TASK_MANIFEST_CONTENT}`,
   `{APPLICABLE_SKILL}`, output schema pointer
2. Six role prompts (`scout-systems`, `define-metrics`, `profile-system`,
   `extract-observations`, `review-records`, `analyze-archetypes`)

Prompts target the common denominator between Claude and Codex — no tool-native
function-call syntax embedded. Output shape is JSON validated by `schemas/run.schema.json`.

**Gate:** Smoke test — manually feed `tsk-bootstrap-dryrun` through both runtimes,
confirm each produces a valid `run.json`.

### Phase 9 — QC + evals
1. `qc/fixtures/valid/`, `qc/fixtures/invalid/` — minimal examples per schema
2. `qc/evals/no-uncited-numeric-claims.yaml`
3. `qc/evals/minimum-one-evidence-ref.yaml`
4. `qc/goldens/` — one golden input→output per skill
5. `src/coc/evals.py` + `scripts/run_evals.py`

**Gate:** `uv run coc eval` runs all evals; at least one golden passes per skill.

### Phase 10 — Release packaging
1. `src/coc/release.py` builds `releases/snapshot-YYYY-MM-DD/` containing:
   - `datapackage.json` (Frictionless Data Package)
   - `ro-crate-metadata.jsonld` (RO-Crate)
   - `manifest.md` (human-readable index)
   - `data/*.parquet` copies
2. `scripts/build_release.py` wrapper

**Gate:** `uv run coc release` produces snapshot; `frictionless validate
releases/snapshot-*/datapackage.json` passes.

### Phase 11 — GitHub integration
1. `.github/workflows/validate.yml` — runs `coc validate` + `pytest` on PRs
2. `.github/workflows/ci.yml` — ruff + mypy + pytest matrix
3. `.github/workflows/materialize.yml` — optional weekly rebuild to verify
4. `.github/ISSUE_TEMPLATE/{new-system,new-metric,bug}.yml`
5. `.github/PULL_REQUEST_TEMPLATE.md` — checklist referencing AGENTS.md quality bar
6. `CODEOWNERS`
7. Documented branch-protection rules (applied post-push via `gh api`)

**Gate:** First push → CI green. Synthetic PR triggers validate workflow and blocks
on intentional schema break.

### Phase 12 — End-to-end acceptance
All of these must pass before declaring the repo bootable:

- [ ] `uv sync` from fresh clone (no hidden state)
- [ ] `uv run coc validate` passes on all seeded files
- [ ] Dry-run task completes full lifecycle: ready → leased → running → review → done → archive
- [ ] `uv run coc materialize` produces Parquet + DuckDB from seeds
- [ ] `uv run coc release` produces a valid Data Package snapshot
- [ ] `uv run coc export-taxonomy` produces valid SKOS Turtle
- [ ] `uv run coc eval` runs at least one passing golden per skill
- [ ] Opening repo in Claude Code: slash commands work, AGENTS.md is read
- [ ] Opening repo in Codex: config.toml loads, AGENTS.md is read
- [ ] GitHub Actions: validate + ci workflows green on `main`

---

## 5. Open decisions (please confirm before I start executing)

1. **`domain` enum.** Proposed: `ecological, biological, technological, social, physical, computational, economic, cognitive`. Add/remove any?
2. **ID format.** Proposed:
   - `sys-NNNNNN--slug` (zero-padded 6 digits)
   - `mtr-NNNNNN--slug`
   - `src-NNNNNN--slug`
   - `obs-<8-hex>` (random)
   - `evi-<8-hex>` (random)
   - `tsk-YYYYMMDD-NNNNNN`
   - `run-<ulid>`
3. **GitHub repo visibility** at bootstrap: public or private?
4. **LFS budget.** OK using Git LFS for `registry/sources/*/raw/`? (Free tier is 1 GB storage / 1 GB bandwidth per month. Alternative: keep raw sources out of Git entirely and store provenance-only.)
5. **Licensing.** MIT for code + CC-BY-4.0 for data is the standard research-catalog choice. Confirm, or pick alternatives.
6. **Model pins.** Claude: `claude-opus-4-7`. Codex: whichever is current (need the right ID). Confirm.
7. **Scope of bootstrap execution.** Two options:
   - (a) Setup agent executes Phases 0–12 in one shot, committing per phase.
   - (b) I execute Phases 0–6 now (substrate through working warehouse) so you can verify it end-to-end before we codify it in the `setup-repo` skill for later re-execution.
   I recommend (b) — cheaper to catch structural misfires before they're embedded in a skill.

---

## 6. Out of scope for bootstrap (captured for later)

- DVC pipelines + remotes
- OpenTelemetry / AgentTrace observability
- Vector index over `/knowledge/`-style unstructured corpus (defer until scout-systems
  generates enough literature to warrant it)
- Firecrawl or equivalent dedicated web-extraction tooling
- Hypergraph construction + I-Con analysis (Phase 2 research workstream)
- Any `/knowledge/`-style S3/Box mount — superseded by `registry/sources/` on disk

---

## 7. What this plan changes from the second proposal

| Change | Why |
|--------|-----|
| Cite markers stripped | Research-report artifacts, not valid content |
| Runtime pinned to Python 3.11 + uv | Enables concrete dependency graph |
| DVC deferred | Adds setup friction before it's justified; LFS covers bootstrap-era files |
| `src/coc/` package added | Scripts become thin wrappers; logic is testable and importable |
| `CLAUDE.md` pointer + `.claude/` configs added | Explicit dual-runtime support |
| `.github/` workflows + templates added | GitHub is the declared collaboration substrate |
| `.env.example`, `.gitattributes`, `.pre-commit-config.yaml` added | Reproducibility hygiene |
| `tests/` added | Phase-0 gate is "smoke test green" |
| `analyze-archetypes` scaffolded but disabled | Matches proposal's "sequence later" guidance without leaving a gap in the skills directory |

Everything else in the second proposal (registry/warehouse/ops split, task lifecycle,
three-layer prompt stack, skill-per-workflow, Data Package + RO-Crate releases, SKOS
exports) is preserved verbatim.
