"""Task queue lifecycle tests.

These tests use a temporary OPS_TASKS / OPS_EVENTS directory via monkeypatch
so they don't depend on repo state.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from coc import queue as q
from coc.yamlio import dump_yaml


@pytest.fixture
def fake_ops(tmp_path, monkeypatch):
    tasks = tmp_path / "tasks"
    events = tmp_path / "events"
    for state in (
        "inbox",
        "ready",
        "leased",
        "running",
        "blocked",
        "review",
        "done",
        "failed",
        "archive",
    ):
        (tasks / state).mkdir(parents=True)
    events.mkdir(parents=True)
    monkeypatch.setattr(q, "OPS_TASKS", tasks)
    # Also patch the events module so append_event writes into our tmp tree.
    from coc import events as ev

    monkeypatch.setattr(ev, "OPS_EVENTS", events)
    return tmp_path


def _make_task(tasks_root: Path, task_id: str) -> Path:
    path = tasks_root / "tasks" / "ready" / f"{task_id}.yaml"
    dump_yaml(
        {
            "id": task_id,
            "type": "bootstrap",
            "skill": "setup-repo",
            "state": "ready",
            "priority": "normal",
            "output_targets": ["ops/runs/noop.json"],
            "acceptance_tests": [],
            "lease": {"ttl_minutes": 30, "max_attempts": 1},
            "notes": "test",
            "created_at": "2026-04-22T00:00:00Z",
        },
        path,
    )
    return path


def test_lease_heartbeat_complete_cycle(fake_ops):
    tid = "tsk-20260422-999999"
    _make_task(fake_ops, tid)

    leased = q.lease_task(tid)
    assert leased.parent.name == "leased"

    hb = q.heartbeat_task(tid)
    assert hb == leased

    done = q.complete_task(tid, outputs_json='{"files": []}', terminal_state="done")
    assert done.parent.name == "done"

    events_log = fake_ops / "events" / "task-events.jsonl"
    lines = events_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    kinds = [line.split('"kind":')[1].split(",")[0].strip().strip('"') for line in lines]
    assert kinds == ["task.lease", "task.heartbeat", "task.complete"]


def test_double_lease_fails(fake_ops):
    tid = "tsk-20260422-999998"
    _make_task(fake_ops, tid)
    q.lease_task(tid)
    with pytest.raises(q.QueueError):
        q.lease_task(tid)


def test_complete_wrong_state_fails(fake_ops):
    tid = "tsk-20260422-999997"
    _make_task(fake_ops, tid)  # still in ready/
    with pytest.raises(q.QueueError):
        q.complete_task(tid)
