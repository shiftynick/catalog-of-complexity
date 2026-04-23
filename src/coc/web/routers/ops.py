"""Internal-only ops routes: queue, runs, events, retros, skills."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from coc.paths import TASK_STATES
from coc.web.app import templates
from coc.web.deps import (
    event_streams,
    find_run,
    find_task,
    list_retros,
    list_runs,
    list_skills,
    queue_counts,
    run_artifacts,
    tail_events,
    tasks_in_state,
)

router = APIRouter()


def _render(request: Request, name: str, ctx: dict) -> HTMLResponse:
    return templates.TemplateResponse(request, name, ctx)


@router.get("/ops/", response_class=HTMLResponse, name="ops_index")
def ops_index(request: Request) -> HTMLResponse:
    counts = queue_counts()
    runs = list_runs(limit=10)
    events = tail_events("task-events", limit=15)
    return _render(
        request,
        "ops/index.html",
        {"counts": counts, "runs": runs, "events": events, "states": TASK_STATES},
    )


# --- queue -----------------------------------------------------------------


@router.get("/ops/queue", response_class=HTMLResponse, name="ops_queue")
def ops_queue(
    request: Request,
    state: str | None = Query(default=None),
) -> HTMLResponse:
    groups: dict[str, list[dict]] = {}
    target_states = [state] if state in TASK_STATES else list(TASK_STATES)
    for st in target_states:
        groups[st] = tasks_in_state(st)
    return _render(
        request,
        "ops/queue.html",
        {"groups": groups, "selected_state": state or "", "states": TASK_STATES},
    )


@router.get("/ops/queue/{task_id}", response_class=HTMLResponse, name="ops_task_detail")
def ops_task_detail(request: Request, task_id: str) -> HTMLResponse:
    data, state, path = find_task(task_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"task not found: {task_id}")
    # Recent events scoped to this task
    events = [
        e
        for e in tail_events("task-events", limit=1000)
        if str(e.get("subject") or "") == task_id
    ]
    return _render(
        request,
        "ops/task_detail.html",
        {
            "task": data,
            "state": state,
            "path": str(path) if path else "",
            "events": events,
        },
    )


# --- runs ------------------------------------------------------------------


@router.get("/ops/runs", response_class=HTMLResponse, name="ops_runs")
def ops_runs(request: Request, status: str | None = Query(default=None)) -> HTMLResponse:
    rows = list_runs(limit=500)
    if status:
        rows = [r for r in rows if r.get("status") == status]
    statuses = sorted({r.get("status") for r in rows if r.get("status")})
    return _render(
        request,
        "ops/runs.html",
        {"rows": rows, "statuses": statuses, "selected_status": status or ""},
    )


@router.get("/ops/runs/{run_id}", response_class=HTMLResponse, name="ops_run_detail")
def ops_run_detail(request: Request, run_id: str) -> HTMLResponse:
    run, run_dir = find_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"run not found: {run_id}")
    artifacts = [p.name for p in run_artifacts(run_dir)] if run_dir else []
    events = [
        e
        for e in tail_events("run-events", limit=1000)
        if str(e.get("subject") or "") == run_id or str(e.get("run_id") or "") == run_id
    ]
    return _render(
        request,
        "ops/run_detail.html",
        {
            "run": run,
            "run_dir": str(run_dir) if run_dir else "",
            "artifacts": artifacts,
            "events": events,
        },
    )


@router.get(
    "/ops/runs/{run_id}/artifacts/{name}",
    response_class=PlainTextResponse,
    name="ops_run_artifact",
)
def ops_run_artifact(run_id: str, name: str) -> PlainTextResponse:
    _, run_dir = find_run(run_id)
    if not run_dir:
        raise HTTPException(status_code=404, detail=f"run not found: {run_id}")
    # Guard against path traversal.
    candidate = (run_dir / name).resolve()
    if run_dir.resolve() not in candidate.parents and candidate != (run_dir / name).resolve():
        raise HTTPException(status_code=400, detail="invalid artifact path")
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail=f"artifact not found: {name}")
    try:
        return PlainTextResponse(candidate.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        raise HTTPException(status_code=415, detail="binary artifact not rendered") from None


# --- events + retros + skills ---------------------------------------------


@router.get("/ops/events", response_class=HTMLResponse, name="ops_events")
def ops_events(
    request: Request,
    stream: str = Query(default="task-events"),
    limit: int = Query(default=100, le=2000),
) -> HTMLResponse:
    streams = event_streams()
    rows = tail_events(stream, limit=limit)
    return _render(
        request,
        "ops/events.html",
        {"rows": rows, "streams": streams, "stream": stream, "limit": limit},
    )


@router.get("/ops/retros", response_class=HTMLResponse, name="ops_retros")
def ops_retros(request: Request) -> HTMLResponse:
    rows = list_retros(limit=500)
    return _render(request, "ops/retros.html", {"rows": rows})


@router.get("/ops/skills", response_class=HTMLResponse, name="ops_skills")
def ops_skills(request: Request) -> HTMLResponse:
    rows = list_skills()
    return _render(request, "ops/skills.html", {"rows": rows})
