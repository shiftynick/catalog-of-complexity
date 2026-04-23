"""Read-only data access for the web UI.

Data reads go through DuckDB (warehouse). Process reads (tasks, runs, events,
retros) go through the filesystem directly — this keeps the public mode
decoupled from ``ops/`` entirely, since those routes aren't mounted in public
mode.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import duckdb

from coc.paths import (
    OPS_EVENTS,
    OPS_RETROS,
    OPS_RUNS,
    OPS_TASKS,
    SKILLS,
    TASK_STATES,
    TAXONOMY_SRC,
)
from coc.web.settings import load_settings
from coc.yamlio import load_yaml


# ---------------------------------------------------------------------------
# DuckDB access
# ---------------------------------------------------------------------------


def _connect() -> duckdb.DuckDBPyConnection:
    settings = load_settings()
    if not settings.duckdb_path.exists():
        raise FileNotFoundError(
            f"warehouse not materialized: {settings.duckdb_path}. "
            "Run `uv run coc materialize` first."
        )
    return duckdb.connect(str(settings.duckdb_path), read_only=True)


def query(sql: str, params: list[Any] | None = None) -> list[dict]:
    con = _connect()
    try:
        cur = con.execute(sql, params or [])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row, strict=False)) for row in cur.fetchall()]
    finally:
        con.close()


def scalar(sql: str, params: list[Any] | None = None) -> Any:
    con = _connect()
    try:
        row = con.execute(sql, params or []).fetchone()
        return None if row is None else row[0]
    finally:
        con.close()


def warehouse_available() -> bool:
    return load_settings().duckdb_path.exists()


def decode_json_columns(row: dict, cols: list[str]) -> dict:
    """Best-effort decode of JSON-encoded string columns to Python lists/dicts."""
    out = dict(row)
    for c in cols:
        v = out.get(c)
        if isinstance(v, str) and v:
            try:
                out[c] = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                pass
    return out


# ---------------------------------------------------------------------------
# Taxonomy (cached; small files)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=8)
def taxonomy(name: str) -> dict:
    """Return a taxonomy source file as a dict. Caches the parsed YAML."""
    path = TAXONOMY_SRC / f"{name}.yaml"
    if not path.exists():
        return {"name": name, "items": []}
    return load_yaml(path) or {"name": name, "items": []}


def all_taxonomies() -> list[str]:
    if not TAXONOMY_SRC.exists():
        return []
    return sorted(p.stem for p in TAXONOMY_SRC.glob("*.yaml"))


# ---------------------------------------------------------------------------
# Ops: tasks
# ---------------------------------------------------------------------------


def queue_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for state in TASK_STATES:
        d = OPS_TASKS / state
        counts[state] = len(list(d.glob("*.yaml"))) if d.exists() else 0
    return counts


def tasks_in_state(state: str) -> list[dict]:
    d = OPS_TASKS / state
    if not d.exists():
        return []
    rows = []
    for p in sorted(d.glob("*.yaml")):
        data = load_yaml(p) or {}
        data["_path"] = str(p.relative_to(OPS_TASKS.parent.parent))
        rows.append(data)
    rows.sort(
        key=lambda r: (str(r.get("priority") or "normal"), str(r.get("created_at") or "")),
    )
    return rows


def all_tasks() -> list[dict]:
    """Every task across every state, each tagged with its state."""
    out: list[dict] = []
    for state in TASK_STATES:
        for t in tasks_in_state(state):
            t["_state"] = state
            out.append(t)
    return out


def find_task(task_id: str) -> tuple[dict | None, str | None, Path | None]:
    for state in TASK_STATES:
        p = OPS_TASKS / state / f"{task_id}.yaml"
        if p.exists():
            return load_yaml(p) or {}, state, p
    return None, None, None


# ---------------------------------------------------------------------------
# Ops: runs
# ---------------------------------------------------------------------------


def iter_run_files() -> list[Path]:
    if not OPS_RUNS.exists():
        return []
    return sorted(OPS_RUNS.rglob("run.json"), reverse=True)


def list_runs(limit: int = 200) -> list[dict]:
    rows: list[dict] = []
    for p in iter_run_files()[:limit]:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        data["_run_dir"] = str(p.parent.relative_to(OPS_RUNS.parent.parent))
        rows.append(data)
    return rows


def find_run(run_id: str) -> tuple[dict | None, Path | None]:
    for p in iter_run_files():
        if p.parent.name == run_id:
            try:
                return json.loads(p.read_text(encoding="utf-8")), p.parent
            except (OSError, json.JSONDecodeError):
                return None, p.parent
    return None, None


def run_artifacts(run_dir: Path) -> list[Path]:
    if not run_dir or not run_dir.exists():
        return []
    return sorted(p for p in run_dir.iterdir() if p.is_file() and p.name != "run.json")


# ---------------------------------------------------------------------------
# Ops: events + retros
# ---------------------------------------------------------------------------


def tail_events(stream: str = "task-events", limit: int = 100) -> list[dict]:
    path = OPS_EVENTS / f"{stream}.jsonl"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    out: list[dict] = []
    for raw in reversed(lines[-limit:]):
        raw = raw.strip()
        if not raw:
            continue
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return out


def event_streams() -> list[str]:
    if not OPS_EVENTS.exists():
        return []
    return sorted(p.stem for p in OPS_EVENTS.glob("*.jsonl"))


def list_retros(limit: int = 200) -> list[dict]:
    if not OPS_RETROS.exists():
        return []
    rows: list[dict] = []
    for p in sorted(OPS_RETROS.rglob("*.json"), reverse=True)[:limit]:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        data["_path"] = str(p.relative_to(OPS_RETROS.parent.parent))
        rows.append(data)
    return rows


# ---------------------------------------------------------------------------
# Skills roster
# ---------------------------------------------------------------------------


def list_skills() -> list[dict]:
    if not SKILLS.exists():
        return []
    out: list[dict] = []
    for d in sorted(SKILLS.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue
        description, status = _parse_skill_header(skill_md)
        out.append(
            {
                "name": d.name,
                "description": description,
                "status": status,
                "path": str(skill_md.relative_to(SKILLS.parent)),
            }
        )
    return out


def _parse_skill_header(skill_md: Path) -> tuple[str, str | None]:
    """Pull description + optional status from a SKILL.md frontmatter block."""
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return ("", None)
    if not text.startswith("---"):
        return (text.splitlines()[0][:200] if text else "", None)
    _, _, rest = text.partition("---\n")
    fm, _, _ = rest.partition("\n---")
    desc = ""
    status: str | None = None
    for line in fm.splitlines():
        if line.startswith("description:"):
            desc = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("status:"):
            status = line.split(":", 1)[1].strip().strip('"').strip("'")
    return (desc, status)
