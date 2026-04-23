"""Filesystem layout constants.

Centralized so that scripts, tests, and CLI commands all agree on where things
live. The repo root is resolved from this file's location, not from CWD, so
commands work from any subdirectory.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCHEMAS = REPO_ROOT / "schemas"
PROMPTS = REPO_ROOT / "prompts"
SKILLS = REPO_ROOT / "skills"

TAXONOMY_SRC = REPO_ROOT / "taxonomy" / "source"
TAXONOMY_EXPORTS = REPO_ROOT / "taxonomy" / "exports"

REGISTRY = REPO_ROOT / "registry"
REG_SYSTEMS = REGISTRY / "systems"
REG_METRICS = REGISTRY / "metrics"
REG_SOURCES = REGISTRY / "sources"
REG_OBSERVATIONS = REGISTRY / "observations"

OPS = REPO_ROOT / "ops"
OPS_TASKS = OPS / "tasks"
OPS_RUNS = OPS / "runs"
OPS_EVENTS = OPS / "events"

WAREHOUSE = REPO_ROOT / "warehouse"
WH_PARQUET = WAREHOUSE / "parquet"
WH_DUCKDB = WAREHOUSE / "duckdb"
WH_SQL = WAREHOUSE / "sql"

QC = REPO_ROOT / "qc"
QC_FIXTURES = QC / "fixtures"
QC_EVALS = QC / "evals"
QC_GOLDENS = QC / "goldens"
QC_REPORTS = QC / "reports"

RELEASES = REPO_ROOT / "releases"
WORKSPACE = REPO_ROOT / "workspace"

TASK_STATES = (
    "inbox",
    "ready",
    "leased",
    "running",
    "blocked",
    "review",
    "done",
    "failed",
    "archive",
)
