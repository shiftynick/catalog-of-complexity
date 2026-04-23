"""Materialize the canonical registry into Parquet + DuckDB.

The warehouse is fully derived from `registry/` — deleting it and re-running
`coc materialize` should reproduce the same tables. Do not hand-edit anything
under `warehouse/`.
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from coc.paths import (
    REG_METRICS,
    REG_OBSERVATIONS,
    REG_SOURCES,
    REG_SYSTEMS,
    WH_DUCKDB,
    WH_PARQUET,
    WH_SQL,
)
from coc.yamlio import load_yaml

# Declared schemas for tables that may be empty at bootstrap time. Without
# these, pyarrow cannot write a typed empty parquet file.
APPLICABILITY_SCHEMA = pa.schema(
    [
        ("system_id", pa.string()),
        ("metric_id", pa.string()),
        ("applicable", pa.bool_()),
        ("reason", pa.string()),
    ]
)

EDGES_SCHEMA = pa.schema(
    [
        ("source_id", pa.string()),
        ("target_id", pa.string()),
        ("edge_kind", pa.string()),
        ("weight", pa.float64()),
    ]
)


def _iter_system_yamls():
    if not REG_SYSTEMS.exists():
        return
    for d in sorted(REG_SYSTEMS.iterdir()):
        if d.is_dir() and (d / "system.yaml").exists():
            yield d / "system.yaml"


def _iter_metric_yamls():
    if not REG_METRICS.exists():
        return
    for d in sorted(REG_METRICS.iterdir()):
        if d.is_dir() and (d / "metric.yaml").exists():
            yield d / "metric.yaml"


def _iter_source_yamls():
    if not REG_SOURCES.exists():
        return
    for d in sorted(REG_SOURCES.iterdir()):
        if d.is_dir() and (d / "source.yaml").exists():
            yield d / "source.yaml"


def _load_systems() -> list[dict]:
    rows = []
    for p in _iter_system_yamls():
        r = load_yaml(p) or {}
        boundary = r.get("boundary") or {}
        scales = r.get("scales") or {}
        rows.append(
            {
                "id": r.get("id"),
                "slug": r.get("slug"),
                "name": r.get("name"),
                "status": r.get("status"),
                "summary": r.get("summary"),
                "aliases": json.dumps(r.get("aliases", []) or []),
                "taxonomy_refs": json.dumps(r.get("taxonomy_refs", []) or []),
                "components": json.dumps(r.get("components", []) or []),
                "interaction_types": json.dumps(r.get("interaction_types", []) or []),
                "boundary_type": boundary.get("type"),
                "boundary_description": boundary.get("description"),
                "scales_spatial": json.dumps(scales.get("spatial", []) or []),
                "scales_temporal": json.dumps(scales.get("temporal", []) or []),
                "source_refs": json.dumps(r.get("source_refs", []) or []),
                "created_at": r.get("created_at"),
                "updated_at": r.get("updated_at"),
            }
        )
    return rows


def _load_metrics() -> list[dict]:
    rows = []
    for p in _iter_metric_yamls():
        r = load_yaml(p) or {}
        appl = r.get("applicability") or {}
        norm = r.get("normalization") or {}
        evreq = r.get("evidence_requirements") or {}
        rows.append(
            {
                "id": r.get("id"),
                "slug": r.get("slug"),
                "name": r.get("name"),
                "family": r.get("family"),
                "status": r.get("status"),
                "value_type": r.get("value_type"),
                "unit": r.get("unit"),
                "directionality": r.get("directionality"),
                "description": r.get("description"),
                "requires": json.dumps(appl.get("requires", []) or []),
                "excludes": json.dumps(appl.get("excludes", []) or []),
                "estimation_methods": json.dumps(r.get("estimation_methods", []) or []),
                "normalization_strategy": norm.get("strategy"),
                "minimum_source_count": evreq.get("minimum_source_count"),
                "review_required": evreq.get("review_required"),
            }
        )
    return rows


def _load_sources() -> list[dict]:
    rows = []
    for p in _iter_source_yamls():
        r = load_yaml(p) or {}
        rows.append(
            {
                "id": r.get("id"),
                "slug": r.get("slug"),
                "title": r.get("title"),
                "authors": json.dumps(r.get("authors", []) or []),
                "kind": r.get("kind"),
                "year": r.get("year"),
                "doi": r.get("doi"),
                "url": r.get("url"),
                "license": r.get("license"),
                "retrieved_at": r.get("retrieved_at"),
                "citation": r.get("citation"),
                "hash": r.get("hash"),
            }
        )
    return rows


def _load_observations() -> list[dict]:
    rows: list[dict] = []
    if not REG_OBSERVATIONS.exists():
        return rows
    for jsonl in sorted(REG_OBSERVATIONS.rglob("*.jsonl")):
        with jsonl.open("r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                obj = json.loads(raw)
                value = obj.get("value")
                value_numeric = (
                    float(value)
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                    else None
                )
                value_text = value if isinstance(value, str) else None
                value_boolean = value if isinstance(value, bool) else None
                temporal = obj.get("temporal_context") or {}
                spatial = obj.get("spatial_context") or {}
                rows.append(
                    {
                        "observation_id": obj.get("observation_id"),
                        "system_id": obj.get("system_id"),
                        "metric_id": obj.get("metric_id"),
                        "value_numeric": value_numeric,
                        "value_text": value_text,
                        "value_boolean": value_boolean,
                        "unit": obj.get("unit"),
                        "value_kind": obj.get("value_kind"),
                        "confidence": obj.get("confidence"),
                        "method": obj.get("method"),
                        "source_refs": json.dumps(obj.get("source_refs", []) or []),
                        "evidence_refs": json.dumps(obj.get("evidence_refs", []) or []),
                        "temporal_label": temporal.get("label"),
                        "spatial_label": spatial.get("label"),
                        "review_state": obj.get("review_state"),
                        "observed_at": obj.get("observed_at"),
                    }
                )
    return rows


def _load_evidence() -> list[dict]:
    rows: list[dict] = []
    if not REG_SOURCES.exists():
        return rows
    for d in sorted(REG_SOURCES.iterdir()):
        ev = d / "evidence.jsonl"
        if not ev.exists():
            continue
        with ev.open("r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                obj = json.loads(raw)
                rows.append(
                    {
                        "evidence_id": obj.get("evidence_id"),
                        "source_id": obj.get("source_id"),
                        "locator": obj.get("locator"),
                        "quote": obj.get("quote"),
                        "extracted_at": obj.get("extracted_at"),
                    }
                )
    return rows


def _write_parquet(name: str, rows: list[dict], empty_schema: pa.Schema | None = None) -> int:
    WH_PARQUET.mkdir(parents=True, exist_ok=True)
    path = WH_PARQUET / f"{name}.parquet"
    if rows:
        table = pa.Table.from_pylist(rows)
    elif empty_schema is not None:
        table = empty_schema.empty_table()
    else:
        table = pa.table({"_placeholder": pa.array([], type=pa.string())})
    pq.write_table(table, path)
    return len(rows)


def _run_sql_views(con: duckdb.DuckDBPyConnection) -> None:
    if not WH_SQL.exists():
        return
    for sql_file in sorted(WH_SQL.glob("*.sql")):
        sql = sql_file.read_text(encoding="utf-8")
        con.execute(sql)


def materialize() -> dict[str, int]:
    """Rebuild warehouse. Returns row counts per table."""
    counts: dict[str, int] = {}
    counts["systems"] = _write_parquet("systems", _load_systems())
    counts["metrics"] = _write_parquet("metrics", _load_metrics())
    counts["sources"] = _write_parquet("sources", _load_sources())
    counts["observations"] = _write_parquet("observations", _load_observations())
    counts["evidence"] = _write_parquet("evidence", _load_evidence())
    counts["applicability"] = _write_parquet("applicability", [], empty_schema=APPLICABILITY_SCHEMA)
    counts["edges"] = _write_parquet("edges", [], empty_schema=EDGES_SCHEMA)

    WH_DUCKDB.mkdir(parents=True, exist_ok=True)
    db_path = WH_DUCKDB / "coc.duckdb"
    # Remove any stale DB so schema changes land cleanly.
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))
    try:
        for table in counts:
            pfile = WH_PARQUET / f"{table}.parquet"
            con.execute(
                f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet(?)",
                [pfile.as_posix()],
            )
        _run_sql_views(con)
    finally:
        con.close()
    return counts


def query(sql: str) -> list[tuple]:
    """Convenience read-only query against the warehouse DuckDB."""
    db_path = WH_DUCKDB / "coc.duckdb"
    if not db_path.exists():
        raise FileNotFoundError(f"warehouse not materialized: {db_path}")
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


__all__ = ["materialize", "query", "APPLICABILITY_SCHEMA", "EDGES_SCHEMA"]


def _unused_path_silencer() -> Path:
    """Silence unused-import lint for Path (kept for external helpers)."""
    return WH_PARQUET
