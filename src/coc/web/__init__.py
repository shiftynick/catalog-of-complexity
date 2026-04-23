"""Web UI for browsing registry data and inspecting the agent task queue.

Two modes:
- ``internal`` mounts ``/data``, ``/taxonomy``, and ``/ops``. For operator use.
- ``public``   mounts only ``/data`` and ``/taxonomy``. Safe to expose.

Run with ``coc serve`` (CLI) or ``uvicorn coc.web.app:app``.
"""

from coc.web.app import create_app

__all__ = ["create_app"]
