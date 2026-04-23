"""Append-only JSONL event logs under ops/events/."""

from __future__ import annotations

import json
from typing import Any

from coc.paths import OPS_EVENTS
from coc.schemas import validate_instance

VALID_LOGS = frozenset({"task-events", "run-events", "provenance-events"})


def append_event(log: str, event: dict[str, Any]) -> None:
    """Validate against the Event schema, then append one line to the named log."""
    if log not in VALID_LOGS:
        raise ValueError(f"unknown event log: {log!r}; must be one of {sorted(VALID_LOGS)}")
    errors = validate_instance("event", event)
    if errors:
        raise ValueError(f"event fails schema: {errors}")
    path = OPS_EVENTS / f"{log}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
