"""Public-safe data routes: landing, systems, metrics, observations, sources."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse

from coc.web.app import templates
from coc.web.deps import (
    decode_json_columns,
    query,
    scalar,
    warehouse_available,
)

router = APIRouter()


def _render(request: Request, name: str, ctx: dict) -> HTMLResponse:
    return templates.TemplateResponse(request, name, ctx)


@router.get("/data/", response_class=HTMLResponse, name="data_index")
def data_index(request: Request) -> HTMLResponse:
    if not warehouse_available():
        return _render(request, "data/warehouse_missing.html", {})
    counts = {
        "systems": scalar("SELECT COUNT(*) FROM systems"),
        "metrics": scalar("SELECT COUNT(*) FROM metrics"),
        "observations": scalar("SELECT COUNT(*) FROM observations"),
        "sources": scalar("SELECT COUNT(*) FROM sources"),
    }
    # Domain distribution is parsed from the JSON-encoded taxonomy_refs column.
    by_domain = query(
        """
        WITH tagged AS (
            SELECT
                id,
                CASE
                    WHEN taxonomy_refs LIKE '%"system-domain:ecological"%' THEN 'ecological'
                    WHEN taxonomy_refs LIKE '%"system-domain:biological"%' THEN 'biological'
                    WHEN taxonomy_refs LIKE '%"system-domain:technological"%' THEN 'technological'
                    WHEN taxonomy_refs LIKE '%"system-domain:social"%' THEN 'social'
                    WHEN taxonomy_refs LIKE '%"system-domain:physical"%' THEN 'physical'
                    WHEN taxonomy_refs LIKE '%"system-domain:computational"%' THEN 'computational'
                    WHEN taxonomy_refs LIKE '%"system-domain:economic"%' THEN 'economic'
                    WHEN taxonomy_refs LIKE '%"system-domain:cognitive"%' THEN 'cognitive'
                    ELSE 'unclassified'
                END AS domain
            FROM systems
        )
        SELECT domain, COUNT(*) AS n FROM tagged GROUP BY 1 ORDER BY n DESC, domain ASC
        """
    )
    latest = query(
        """
        SELECT observation_id, system_id, metric_id, value_numeric, value_text,
               unit, confidence, review_state, observed_at
        FROM observations
        ORDER BY observed_at DESC NULLS LAST
        LIMIT 10
        """
    )
    return _render(
        request,
        "data/index.html",
        {"counts": counts, "by_domain": by_domain, "latest": latest},
    )


# --- systems ---------------------------------------------------------------


@router.get("/data/systems", response_class=HTMLResponse, name="data_systems_list")
def systems_list(
    request: Request,
    q: str | None = Query(default=None),
    domain: str | None = Query(default=None),
) -> HTMLResponse:
    if not warehouse_available():
        return _render(request, "data/warehouse_missing.html", {})
    where = ["1=1"]
    params: list = []
    if q:
        where.append("(lower(name) LIKE ? OR lower(slug) LIKE ?)")
        like = f"%{q.lower()}%"
        params.extend([like, like])
    if domain:
        where.append("taxonomy_refs LIKE ?")
        params.append(f'%"system-domain:{domain}"%')
    rows = query(
        f"""
        SELECT id, slug, name, status, summary, taxonomy_refs
        FROM systems
        WHERE {' AND '.join(where)}
        ORDER BY name ASC
        """,
        params,
    )
    rows = [decode_json_columns(r, ["taxonomy_refs"]) for r in rows]
    return _render(
        request,
        "data/systems_list.html",
        {"rows": rows, "q": q or "", "domain": domain or ""},
    )


@router.get("/data/systems/{system_id}", response_class=HTMLResponse, name="data_system_detail")
def system_detail(request: Request, system_id: str) -> HTMLResponse:
    if not warehouse_available():
        return _render(request, "data/warehouse_missing.html", {})
    rows = query("SELECT * FROM systems WHERE id = ?", [system_id])
    if not rows:
        raise HTTPException(status_code=404, detail=f"system not found: {system_id}")
    system = decode_json_columns(
        rows[0],
        [
            "aliases",
            "taxonomy_refs",
            "components",
            "interaction_types",
            "scales_spatial",
            "scales_temporal",
            "source_refs",
        ],
    )
    observations = query(
        """
        SELECT observation_id, metric_id, value_numeric, value_text, unit,
               value_kind, confidence, review_state, observed_at
        FROM observations
        WHERE system_id = ?
        ORDER BY observed_at DESC NULLS LAST
        """,
        [system_id],
    )
    return _render(
        request,
        "data/system_detail.html",
        {"system": system, "observations": observations},
    )


# --- metrics ---------------------------------------------------------------


@router.get("/data/metrics", response_class=HTMLResponse, name="data_metrics_list")
def metrics_list(
    request: Request,
    family: str | None = Query(default=None),
) -> HTMLResponse:
    if not warehouse_available():
        return _render(request, "data/warehouse_missing.html", {})
    where = ["1=1"]
    params: list = []
    if family:
        where.append("family = ?")
        params.append(family)
    rows = query(
        f"""
        SELECT id, slug, name, family, status, value_type, unit, directionality
        FROM metrics
        WHERE {' AND '.join(where)}
        ORDER BY family, name
        """,
        params,
    )
    families = [
        r["family"]
        for r in query("SELECT DISTINCT family FROM metrics WHERE family IS NOT NULL ORDER BY 1")
    ]
    return _render(
        request,
        "data/metrics_list.html",
        {"rows": rows, "families": families, "family": family or ""},
    )


@router.get("/data/metrics/{metric_id}", response_class=HTMLResponse, name="data_metric_detail")
def metric_detail(request: Request, metric_id: str) -> HTMLResponse:
    if not warehouse_available():
        return _render(request, "data/warehouse_missing.html", {})
    rows = query("SELECT * FROM metrics WHERE id = ?", [metric_id])
    if not rows:
        raise HTTPException(status_code=404, detail=f"metric not found: {metric_id}")
    metric = decode_json_columns(rows[0], ["requires", "excludes", "estimation_methods"])
    observations = query(
        """
        SELECT observation_id, system_id, value_numeric, value_text, unit,
               value_kind, confidence, review_state, observed_at
        FROM observations
        WHERE metric_id = ?
        ORDER BY observed_at DESC NULLS LAST
        """,
        [metric_id],
    )
    return _render(
        request,
        "data/metric_detail.html",
        {"metric": metric, "observations": observations},
    )


# --- observations ----------------------------------------------------------


@router.get("/data/observations", response_class=HTMLResponse, name="data_observations_list")
def observations_list(
    request: Request,
    system_id: str | None = Query(default=None),
    metric_id: str | None = Query(default=None),
    review_state: str | None = Query(default=None),
) -> HTMLResponse:
    if not warehouse_available():
        return _render(request, "data/warehouse_missing.html", {})
    where = ["1=1"]
    params: list = []
    for col, val in (
        ("system_id", system_id),
        ("metric_id", metric_id),
        ("review_state", review_state),
    ):
        if val:
            where.append(f"{col} = ?")
            params.append(val)
    rows = query(
        f"""
        SELECT observation_id, system_id, metric_id, value_numeric, value_text,
               unit, value_kind, confidence, review_state, observed_at
        FROM observations
        WHERE {' AND '.join(where)}
        ORDER BY observed_at DESC NULLS LAST
        LIMIT 500
        """,
        params,
    )
    review_states = [
        r["review_state"]
        for r in query(
            "SELECT DISTINCT review_state FROM observations "
            "WHERE review_state IS NOT NULL ORDER BY 1"
        )
    ]
    return _render(
        request,
        "data/observations_list.html",
        {
            "rows": rows,
            "review_states": review_states,
            "system_id": system_id or "",
            "metric_id": metric_id or "",
            "review_state": review_state or "",
        },
    )


# --- sources ---------------------------------------------------------------


@router.get("/data/sources", response_class=HTMLResponse, name="data_sources_list")
def sources_list(request: Request) -> HTMLResponse:
    if not warehouse_available():
        return _render(request, "data/warehouse_missing.html", {})
    rows = query(
        """
        SELECT id, slug, title, kind, year, doi, url
        FROM sources
        ORDER BY year DESC NULLS LAST, title ASC
        """
    )
    return _render(request, "data/sources_list.html", {"rows": rows})


@router.get("/data/sources/{source_id}", response_class=HTMLResponse, name="data_source_detail")
def source_detail(request: Request, source_id: str) -> HTMLResponse:
    if not warehouse_available():
        return _render(request, "data/warehouse_missing.html", {})
    rows = query("SELECT * FROM sources WHERE id = ?", [source_id])
    if not rows:
        raise HTTPException(status_code=404, detail=f"source not found: {source_id}")
    source = decode_json_columns(rows[0], ["authors"])
    # Observations citing this source. source_refs is a JSON-encoded list.
    citing = query(
        """
        SELECT observation_id, system_id, metric_id, value_numeric, value_text,
               unit, review_state, observed_at
        FROM observations
        WHERE source_refs LIKE ?
        ORDER BY observed_at DESC NULLS LAST
        """,
        [f'%"{source_id}"%'],
    )
    return _render(
        request,
        "data/source_detail.html",
        {"source": source, "citing": citing},
    )
