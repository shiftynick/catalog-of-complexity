"""FastAPI app factory. Mounts routers based on the configured mode."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from coc.web.settings import Settings, load_settings

_STATIC_DIR = Path(__file__).parent / "static"
_TEMPLATE_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=str(_TEMPLATE_DIR))


def _inject_globals(settings: Settings) -> None:
    templates.env.globals["settings"] = settings
    templates.env.globals["is_public"] = settings.is_public
    templates.env.globals["site_title"] = settings.title


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    _inject_globals(settings)

    app = FastAPI(title=settings.title, docs_url=None, redoc_url=None)
    app.state.settings = settings

    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    # Import routers lazily so modules with no route deps don't import fastapi
    # at package import time.
    from coc.web.routers import data as data_router
    from coc.web.routers import taxonomy as taxonomy_router

    app.include_router(data_router.router)
    app.include_router(taxonomy_router.router)

    if not settings.is_public:
        from coc.web.routers import ops as ops_router

        app.include_router(ops_router.router)

    @app.get("/", include_in_schema=False)
    def _root(request: Request):  # type: ignore[override]
        return RedirectResponse(request.url_for("data_index"))

    @app.get("/healthz", include_in_schema=False)
    def _healthz():
        return {"ok": True, "mode": settings.mode}

    return app


# Default app for `uvicorn coc.web.app:app`.
app = create_app()
