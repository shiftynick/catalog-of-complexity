"""Directory-based task queue with atomic-move lease semantics.

The state of a task is encoded in two places: the `state` field inside the
task's YAML file, and the subdirectory it lives in under `ops/tasks/`. These
must agree — the validator enforces it. Every transition here keeps them in
sync.

Claiming a task is an atomic `os.rename` from `ready/` to `leased/`. On the
same filesystem this is atomic on both POSIX and Windows, so two agents
racing to claim the same task see exactly one winner.
"""

from __future__ import annotations

import json
import os
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ulid import ULID

from coc.events import append_event
from coc.paths import OPS_TASKS, TASK_STATES
from coc.yamlio import dump_yaml, load_yaml

VALID_TERMINAL_STATES = ("review", "done", "blocked", "failed")

PRIORITY_ORDER = {"urgent": 0, "high": 1, "normal": 2, "low": 3}

AUTO_PROMOTE_TYPES = frozenset(
    {
        "scout-systems",
        "profile-system",
        "define-metrics",
        "extract-observations",
        "review-records",
        "apply-retros",
        "analyze-archetypes",
        "acquire-source",
    }
)
PER_TYPE_READY_CAP = 3

# Per-type overrides of PER_TYPE_READY_CAP. review-records is capped tighter
# because the self-improvement loop (retro → cluster → review-records)
# otherwise fills the ready queue and starves catalog-growth task types
# (scout-systems, profile-system) of auto-promote slots.
PER_TYPE_READY_CAP_OVERRIDES: dict[str, int] = {
    "review-records": 1,
}


def _ready_cap_for(task_type: str) -> int:
    return PER_TYPE_READY_CAP_OVERRIDES.get(task_type, PER_TYPE_READY_CAP)


class QueueError(RuntimeError):
    """Raised for queue invariant violations (missing task, wrong state, etc.)."""


def _task_path(task_id: str, state: str) -> Path:
    return OPS_TASKS / state / f"{task_id}.yaml"


def _find_task(task_id: str) -> tuple[Path, str]:
    for state in TASK_STATES:
        p = _task_path(task_id, state)
        if p.exists():
            return p, state
    raise QueueError(f"task not found: {task_id}")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _agent_id() -> str:
    return f"{platform.node()}/{os.getpid()}"


def _event_id() -> str:
    return f"ev-{ULID()}"


def lease_task(task_id: str) -> Path:
    """Atomically claim `task_id` (ready → leased). Raises on race loss or wrong state."""
    src = _task_path(task_id, "ready")
    dst = _task_path(task_id, "leased")
    if not src.exists():
        raise QueueError(f"task not in ready/: {task_id}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.rename(src, dst)  # atomic lock acquisition
    data = load_yaml(dst)
    data["state"] = "leased"
    lease = data.setdefault("lease", {"ttl_minutes": 60, "max_attempts": 3})
    lease["leased_by"] = _agent_id()
    lease["leased_at"] = _now()
    lease["last_heartbeat"] = _now()
    lease["attempts"] = int(lease.get("attempts", 0)) + 1
    dump_yaml(data, dst)
    append_event(
        "task-events",
        {
            "event_id": _event_id(),
            "timestamp": _now(),
            "kind": "task.lease",
            "subject": task_id,
            "actor": _agent_id(),
            "payload": {"attempts": lease["attempts"]},
        },
    )
    return dst


def heartbeat_task(task_id: str) -> Path:
    """Refresh the lease liveness timestamp. Must be leased or running."""
    path, state = _find_task(task_id)
    if state not in ("leased", "running"):
        raise QueueError(f"task not leased/running: {task_id} (state={state})")
    data = load_yaml(path)
    data.setdefault("lease", {})["last_heartbeat"] = _now()
    dump_yaml(data, path)
    append_event(
        "task-events",
        {
            "event_id": _event_id(),
            "timestamp": _now(),
            "kind": "task.heartbeat",
            "subject": task_id,
            "actor": _agent_id(),
            "payload": {},
        },
    )
    return path


def _writes_to_registry(output_targets: Any) -> bool:
    """True if any declared output target is under ``registry/``."""
    if not isinstance(output_targets, list):
        return False
    for t in output_targets:
        s = str(t or "").lstrip("./").replace("\\", "/")
        if s.startswith("registry/"):
            return True
    return False


def _auto_materialize(task_id: str) -> None:
    """Rebuild the warehouse after a registry-touching task completes.

    Failures are logged as an event but do not raise — a successful task
    completion must not be undone by a downstream derived-artifact rebuild.
    Opt out by setting ``COC_SKIP_AUTO_MATERIALIZE=1`` in the environment.
    """
    if os.environ.get("COC_SKIP_AUTO_MATERIALIZE") == "1":
        return
    # Imported lazily: avoids pulling duckdb/pyarrow into `coc queue` imports
    # and prevents any circular-import risk during test monkeypatching.
    from coc.warehouse import materialize

    try:
        counts = materialize()
        append_event(
            "task-events",
            {
                "event_id": _event_id(),
                "timestamp": _now(),
                "kind": "warehouse.materialize",
                "subject": task_id,
                "actor": _agent_id(),
                "payload": {"reason": "post-task-complete", "counts": counts},
            },
        )
    except Exception as exc:  # noqa: BLE001 — event captures detail
        append_event(
            "task-events",
            {
                "event_id": _event_id(),
                "timestamp": _now(),
                "kind": "warehouse.materialize.error",
                "subject": task_id,
                "actor": _agent_id(),
                "payload": {"reason": "post-task-complete", "error": str(exc)},
            },
        )


def complete_task(
    task_id: str,
    outputs_json: str = "{}",
    terminal_state: str = "done",
) -> Path:
    """Move a leased/running task into its terminal state."""
    if terminal_state not in VALID_TERMINAL_STATES:
        raise QueueError(
            f"invalid terminal state: {terminal_state!r} (want one of {VALID_TERMINAL_STATES})"
        )
    src_path, src_state = _find_task(task_id)
    if src_state not in ("leased", "running"):
        raise QueueError(f"task not leased/running: {task_id} (state={src_state})")
    # Parse and validate outputs_json BEFORE mutating any task state. A
    # malformed argument must leave the task in `leased/` so the caller can
    # retry without an orphan rename / missing `task.complete` event.
    try:
        outputs = json.loads(outputs_json) if outputs_json else {}
    except json.JSONDecodeError as exc:
        raise QueueError(
            f"invalid outputs_json for {task_id}: {exc.msg} (line {exc.lineno} col {exc.colno})"
        ) from exc
    data = load_yaml(src_path)
    data["state"] = terminal_state
    dump_yaml(data, src_path)
    dst = _task_path(task_id, terminal_state)
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.rename(src_path, dst)
    kind_map = {
        "done": "task.complete",
        "review": "task.complete",
        "blocked": "task.block",
        "failed": "task.fail",
    }
    append_event(
        "task-events",
        {
            "event_id": _event_id(),
            "timestamp": _now(),
            "kind": kind_map[terminal_state],
            "subject": task_id,
            "actor": _agent_id(),
            "payload": {"outputs": outputs, "terminal_state": terminal_state},
        },
    )
    if _writes_to_registry(data.get("output_targets")):
        _auto_materialize(task_id)
    return dst


def next_ready_task(lane: str | None = None) -> str | None:
    """Return the highest-priority ready task ID, or None if the queue is empty.

    Ordering: priority tier (urgent → low), then `created_at` ascending, then
    task id. Optional `lane` filters against the task's `lane` field (reserved
    for future lane-based parallelism) or its `type`.
    """
    ready = OPS_TASKS / "ready"
    if not ready.exists():
        return None
    candidates: list[tuple[int, str, str]] = []
    for path in sorted(ready.glob("*.yaml")):
        data: dict[str, Any] = load_yaml(path) or {}
        if lane and data.get("lane") != lane and data.get("type") != lane:
            continue
        prio = PRIORITY_ORDER.get(str(data.get("priority", "normal")), 2)
        created = str(data.get("created_at") or "")
        candidates.append((prio, created, str(data.get("id") or path.stem)))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def advance_queue() -> list[str]:
    """Auto-promote eligible inbox tasks to ready/.

    A task is eligible iff its `type` is in AUTO_PROMOTE_TYPES and the
    ready/ queue currently holds fewer than PER_TYPE_READY_CAP tasks of
    that type. Returns the list of promoted task IDs in promotion order.
    """
    inbox = OPS_TASKS / "inbox"
    ready = OPS_TASKS / "ready"
    if not inbox.exists():
        return []
    ready.mkdir(parents=True, exist_ok=True)

    ready_counts: dict[str, int] = {}
    for p in ready.glob("*.yaml"):
        data: dict[str, Any] = load_yaml(p) or {}
        t = str(data.get("type") or "")
        ready_counts[t] = ready_counts.get(t, 0) + 1

    promoted: list[str] = []
    for src in sorted(inbox.glob("*.yaml")):
        data = load_yaml(src) or {}
        task_type = str(data.get("type") or "")
        if task_type not in AUTO_PROMOTE_TYPES:
            continue
        if ready_counts.get(task_type, 0) >= _ready_cap_for(task_type):
            continue
        dst = ready / src.name
        os.rename(src, dst)
        data["state"] = "ready"
        dump_yaml(data, dst)
        ready_counts[task_type] = ready_counts.get(task_type, 0) + 1
        task_id = str(data.get("id") or src.stem)
        promoted.append(task_id)
        append_event(
            "task-events",
            {
                "event_id": _event_id(),
                "timestamp": _now(),
                "kind": "task.promote",
                "subject": task_id,
                "actor": _agent_id(),
                "payload": {
                    "from_state": "inbox",
                    "to_state": "ready",
                    "task_type": task_type,
                    "reason": "auto-advance",
                },
            },
        )
    return promoted


def _task_is_done(task_id: str) -> bool:
    return (OPS_TASKS / "done" / f"{task_id}.yaml").exists()


def _taxonomy_slug_exists(qualified: str) -> bool:
    # Imported lazily so the queue module stays importable even if the
    # taxonomy module's rdflib dep isn't installed in minimal contexts.
    from coc.taxonomy import load_index

    return load_index().has(qualified)


def _unblock_condition_met(spec: Any) -> bool:
    if not isinstance(spec, dict):
        return False
    kind = spec.get("kind")
    if kind == "taxonomy-slug-exists":
        ref = spec.get("taxonomy_ref")
        if not isinstance(ref, str) or ":" not in ref:
            return False
        return _taxonomy_slug_exists(ref)
    if kind == "task-complete":
        tid = spec.get("task_id")
        if not isinstance(tid, str):
            return False
        return _task_is_done(tid)
    return False


def unblock_task(task_id: str) -> Path:
    """Move `task_id` from blocked/ back to ready/ and reset lease counters.

    Raises if the task isn't in blocked/. The `unblock` field (if any) is
    preserved on the task so a repeat block can reuse the same condition.
    """
    src = _task_path(task_id, "blocked")
    if not src.exists():
        raise QueueError(f"task not in blocked/: {task_id}")
    data = load_yaml(src)
    data["state"] = "ready"
    lease = data.setdefault("lease", {"ttl_minutes": 90, "max_attempts": 1})
    lease["attempts"] = 0
    lease["leased_by"] = None
    lease["leased_at"] = None
    lease["last_heartbeat"] = None
    dump_yaml(data, src)
    dst = _task_path(task_id, "ready")
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.rename(src, dst)
    append_event(
        "task-events",
        {
            "event_id": _event_id(),
            "timestamp": _now(),
            "kind": "task.unblock",
            "subject": task_id,
            "actor": _agent_id(),
            "payload": {
                "from_state": "blocked",
                "to_state": "ready",
                "unblock": data.get("unblock"),
            },
        },
    )
    return dst


def sweep_blocked() -> list[str]:
    """Scan blocked/, unblock tasks whose `unblock` condition is satisfied.

    Returns the list of unblocked task ids in scan order. Tasks without an
    `unblock` field, or with a malformed spec, are left in place.
    """
    blocked = OPS_TASKS / "blocked"
    if not blocked.exists():
        return []
    unblocked: list[str] = []
    for path in sorted(blocked.glob("*.yaml")):
        data: dict[str, Any] = load_yaml(path) or {}
        spec = data.get("unblock")
        if not spec:
            continue
        if not _unblock_condition_met(spec):
            continue
        task_id = str(data.get("id") or path.stem)
        unblock_task(task_id)
        unblocked.append(task_id)
    return unblocked


def requeue_stale() -> int:
    """Requeue tasks whose leases have expired. Returns number of tasks moved."""
    leased = OPS_TASKS / "leased"
    if not leased.exists():
        return 0
    moved = 0
    now = datetime.now(UTC)
    for path in sorted(leased.glob("*.yaml")):
        data: dict[str, Any] = load_yaml(path)
        lease = data.get("lease", {}) or {}
        ttl_min = int(lease.get("ttl_minutes", 60))
        last = lease.get("last_heartbeat") or lease.get("leased_at")
        if not last:
            continue
        last_dt = datetime.fromisoformat(str(last).replace("Z", "+00:00"))
        age_min = (now - last_dt).total_seconds() / 60.0
        if age_min <= ttl_min:
            continue
        attempts = int(lease.get("attempts", 1))
        max_attempts = int(lease.get("max_attempts", 3))
        terminal = "failed" if attempts >= max_attempts else "ready"
        data["state"] = terminal
        lease["leased_by"] = None
        lease["last_heartbeat"] = None
        dump_yaml(data, path)
        dst = _task_path(data["id"], terminal)
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.rename(path, dst)
        append_event(
            "task-events",
            {
                "event_id": _event_id(),
                "timestamp": _now(),
                "kind": "task.requeue" if terminal == "ready" else "task.fail",
                "subject": str(data["id"]),
                "actor": "janitor",
                "payload": {"reason": "lease-expired", "age_minutes": age_min},
            },
        )
        moved += 1
    return moved
