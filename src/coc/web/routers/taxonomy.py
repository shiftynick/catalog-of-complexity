"""Public-safe taxonomy browser."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from coc.web.app import templates
from coc.web.deps import all_taxonomies, taxonomy

router = APIRouter()


def _render(request: Request, name: str, ctx: dict) -> HTMLResponse:
    return templates.TemplateResponse(request, name, ctx)


@router.get("/taxonomy/", response_class=HTMLResponse, name="taxonomy_index")
def taxonomy_index(request: Request) -> HTMLResponse:
    names = all_taxonomies()
    summaries = []
    for n in names:
        t = taxonomy(n)
        summaries.append(
            {
                "name": n,
                "label": t.get("name") or n,
                "description": t.get("description") or "",
                "count": len(t.get("items") or []),
            }
        )
    return _render(request, "taxonomy/index.html", {"summaries": summaries})


@router.get("/taxonomy/{name}", response_class=HTMLResponse, name="taxonomy_detail")
def taxonomy_detail(request: Request, name: str) -> HTMLResponse:
    if name not in all_taxonomies():
        raise HTTPException(status_code=404, detail=f"taxonomy not found: {name}")
    t = taxonomy(name)
    return _render(request, "taxonomy/detail.html", {"name": name, "tax": t})
