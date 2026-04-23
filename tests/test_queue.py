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


def test_next_ready_task_orders_by_priority_then_created_at(fake_ops):
    for tid, prio, created in [
        ("tsk-20260422-999990", "normal", "2026-04-22T00:00:00Z"),
        ("tsk-20260422-999991", "high", "2026-04-22T01:00:00Z"),
        ("tsk-20260422-999992", "high", "2026-04-22T00:30:00Z"),
        ("tsk-20260422-999993", "urgent", "2026-04-22T02:00:00Z"),
    ]:
        path = fake_ops / "tasks" / "ready" / f"{tid}.yaml"
        dump_yaml(
            {
                "id": tid,
                "type": "bootstrap",
                "skill": "setup-repo",
                "state": "ready",
                "priority": prio,
                "output_targets": ["ops/runs/noop.json"],
                "acceptance_tests": [],
                "lease": {"ttl_minutes": 30, "max_attempts": 1},
                "created_at": created,
            },
            path,
        )
    # Urgent wins over high regardless of created_at.
    assert q.next_ready_task() == "tsk-20260422-999993"


def test_next_ready_task_returns_none_when_empty(fake_ops):
    assert q.next_ready_task() is None


def test_requeue_stale_moves_expired_lease_back_to_ready(fake_ops):
    tid = "tsk-20260422-888888"
    path = fake_ops / "tasks" / "ready" / f"{tid}.yaml"
    dump_yaml(
        {
            "id": tid,
            "type": "bootstrap",
            "skill": "setup-repo",
            "state": "ready",
            "priority": "normal",
            "output_targets": ["ops/runs/noop.json"],
            "acceptance_tests": [],
            "lease": {"ttl_minutes": 30, "max_attempts": 3},
            "created_at": "2026-04-22T00:00:00Z",
        },
        path,
    )
    q.lease_task(tid)
    # Age the heartbeat past the lease TTL.
    leased_path = fake_ops / "tasks" / "leased" / f"{tid}.yaml"
    from coc.yamlio import load_yaml

    data = load_yaml(leased_path)
    data["lease"]["last_heartbeat"] = "2026-04-21T00:00:00Z"  # day-old
    dump_yaml(data, leased_path)

    moved = q.requeue_stale()
    assert moved == 1
    assert (fake_ops / "tasks" / "ready" / f"{tid}.yaml").exists()
    assert not leased_path.exists()

    events_log = fake_ops / "events" / "task-events.jsonl"
    kinds = [
        ln.split('"kind":')[1].split(",")[0].strip().strip('"')
        for ln in events_log.read_text(encoding="utf-8").strip().splitlines()
    ]
    assert "task.requeue" in kinds


def test_requeue_stale_fails_task_when_max_attempts_reached(fake_ops):
    tid = "tsk-20260422-888887"
    path = fake_ops / "tasks" / "ready" / f"{tid}.yaml"
    dump_yaml(
        {
            "id": tid,
            "type": "bootstrap",
            "skill": "setup-repo",
            "state": "ready",
            "priority": "normal",
            "output_targets": ["ops/runs/noop.json"],
            "acceptance_tests": [],
            "lease": {"ttl_minutes": 30, "max_attempts": 1},
            "created_at": "2026-04-22T00:00:00Z",
        },
        path,
    )
    q.lease_task(tid)
    leased_path = fake_ops / "tasks" / "leased" / f"{tid}.yaml"
    from coc.yamlio import load_yaml

    data = load_yaml(leased_path)
    data["lease"]["last_heartbeat"] = "2026-04-21T00:00:00Z"
    dump_yaml(data, leased_path)

    moved = q.requeue_stale()
    assert moved == 1
    assert (fake_ops / "tasks" / "failed" / f"{tid}.yaml").exists()
    assert not leased_path.exists()


def test_requeue_stale_leaves_fresh_leases_alone(fake_ops):
    tid = "tsk-20260422-888886"
    _make_task(fake_ops, tid)
    q.lease_task(tid)
    # heartbeat is fresh — should not be moved.
    moved = q.requeue_stale()
    assert moved == 0
    assert (fake_ops / "tasks" / "leased" / f"{tid}.yaml").exists()


def _make_inbox_task(tasks_root: Path, task_id: str, task_type: str) -> Path:
    path = tasks_root / "tasks" / "inbox" / f"{task_id}.yaml"
    dump_yaml(
        {
            "id": task_id,
            "type": task_type,
            "skill": task_type,
            "state": "inbox",
            "priority": "normal",
            "output_targets": ["ops/runs/noop.json"],
            "acceptance_tests": [],
            "lease": {"ttl_minutes": 30, "max_attempts": 1},
            "created_at": "2026-04-22T00:00:00Z",
        },
        path,
    )
    return path


def test_advance_queue_promotes_eligible_types(fake_ops):
    _make_inbox_task(fake_ops, "tsk-20260422-777001", "scout-systems")
    _make_inbox_task(fake_ops, "tsk-20260422-777002", "extract-observations")
    _make_inbox_task(fake_ops, "tsk-20260422-777003", "review-records")

    promoted = q.advance_queue()
    assert set(promoted) == {
        "tsk-20260422-777001",
        "tsk-20260422-777002",
        "tsk-20260422-777003",
    }
    for tid in promoted:
        assert (fake_ops / "tasks" / "ready" / f"{tid}.yaml").exists()
        assert not (fake_ops / "tasks" / "inbox" / f"{tid}.yaml").exists()

    events_log = fake_ops / "events" / "task-events.jsonl"
    lines = events_log.read_text(encoding="utf-8").strip().splitlines()
    kinds = [ln.split('"kind":')[1].split(",")[0].strip().strip('"') for ln in lines]
    assert kinds.count("task.promote") == 3


def test_advance_queue_skips_human_review_types(fake_ops):
    _make_inbox_task(fake_ops, "tsk-20260422-777010", "profile-system")
    _make_inbox_task(fake_ops, "tsk-20260422-777011", "define-metrics")
    _make_inbox_task(fake_ops, "tsk-20260422-777012", "apply-retros")

    promoted = q.advance_queue()
    assert promoted == []
    for tid in ("tsk-20260422-777010", "tsk-20260422-777011", "tsk-20260422-777012"):
        assert (fake_ops / "tasks" / "inbox" / f"{tid}.yaml").exists()


def test_advance_queue_respects_per_type_cap(fake_ops):
    # Seed ready/ with cap of an eligible type.
    for i in range(q.PER_TYPE_READY_CAP):
        tid = f"tsk-20260422-77702{i}"
        path = fake_ops / "tasks" / "ready" / f"{tid}.yaml"
        dump_yaml(
            {
                "id": tid,
                "type": "scout-systems",
                "skill": "scout-systems",
                "state": "ready",
                "priority": "normal",
                "output_targets": ["ops/runs/noop.json"],
                "acceptance_tests": [],
                "lease": {"ttl_minutes": 30, "max_attempts": 1},
                "created_at": "2026-04-22T00:00:00Z",
            },
            path,
        )
    # Inbox has more scout-systems — should not promote any of them.
    _make_inbox_task(fake_ops, "tsk-20260422-777030", "scout-systems")
    # But extract-observations should still promote.
    _make_inbox_task(fake_ops, "tsk-20260422-777031", "extract-observations")

    promoted = q.advance_queue()
    assert promoted == ["tsk-20260422-777031"]
    assert (fake_ops / "tasks" / "inbox" / "tsk-20260422-777030.yaml").exists()
    assert (fake_ops / "tasks" / "ready" / "tsk-20260422-777031.yaml").exists()
