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


def test_complete_does_not_auto_materialize_for_ops_output(fake_ops, monkeypatch):
    """The default test fixture declares ops/ outputs — hook must stay dormant."""
    called: list[bool] = []

    def _fake_mat() -> dict[str, int]:
        called.append(True)
        return {}

    monkeypatch.setattr("coc.warehouse.materialize", _fake_mat)
    tid = "tsk-20260422-999970"
    _make_task(fake_ops, tid)
    q.lease_task(tid)
    q.complete_task(tid)

    assert called == []


def test_complete_auto_materializes_for_registry_output(fake_ops, monkeypatch):
    """A task declaring registry/ outputs triggers a warehouse rebuild on complete."""
    called: list[bool] = []

    def _fake_mat() -> dict[str, int]:
        called.append(True)
        return {"systems": 1}

    monkeypatch.setattr("coc.warehouse.materialize", _fake_mat)
    tid = "tsk-20260422-999971"
    path = fake_ops / "tasks" / "ready" / f"{tid}.yaml"
    dump_yaml(
        {
            "id": tid,
            "type": "profile-system",
            "skill": "profile-system",
            "state": "ready",
            "priority": "normal",
            "output_targets": ["registry/systems/"],
            "acceptance_tests": [],
            "lease": {"ttl_minutes": 30, "max_attempts": 1},
            "created_at": "2026-04-22T00:00:00Z",
        },
        path,
    )
    q.lease_task(tid)
    q.complete_task(tid)

    assert called == [True]
    kinds = _event_kinds(fake_ops)
    assert kinds[-1] == "warehouse.materialize"


def test_complete_auto_materialize_skipped_by_env(fake_ops, monkeypatch):
    called: list[bool] = []
    monkeypatch.setattr(
        "coc.warehouse.materialize",
        lambda: called.append(True) or {},
    )
    monkeypatch.setenv("COC_SKIP_AUTO_MATERIALIZE", "1")
    tid = "tsk-20260422-999972"
    path = fake_ops / "tasks" / "ready" / f"{tid}.yaml"
    dump_yaml(
        {
            "id": tid,
            "type": "profile-system",
            "skill": "profile-system",
            "state": "ready",
            "priority": "normal",
            "output_targets": ["registry/systems/"],
            "acceptance_tests": [],
            "lease": {"ttl_minutes": 30, "max_attempts": 1},
            "created_at": "2026-04-22T00:00:00Z",
        },
        path,
    )
    q.lease_task(tid)
    q.complete_task(tid)

    assert called == []


def _event_kinds(fake_ops: Path) -> list[str]:
    log = fake_ops / "events" / "task-events.jsonl"
    lines = log.read_text(encoding="utf-8").strip().splitlines()
    return [line.split('"kind":')[1].split(",")[0].strip().strip('"') for line in lines]


def test_complete_rejects_malformed_outputs_json_atomically(fake_ops):
    """Malformed --outputs must leave the task in leased/ with no task.complete event."""
    tid = "tsk-20260422-999960"
    _make_task(fake_ops, tid)
    q.lease_task(tid)
    leased_path = fake_ops / "tasks" / "leased" / f"{tid}.yaml"
    assert leased_path.exists()

    with pytest.raises(q.QueueError):
        q.complete_task(tid, outputs_json="{not json", terminal_state="done")

    # Task must remain in leased/ — no orphan rename.
    assert leased_path.exists()
    assert not (fake_ops / "tasks" / "done" / f"{tid}.yaml").exists()
    # And no task.complete event was appended.
    kinds = _event_kinds(fake_ops)
    assert "task.complete" not in kinds
    assert kinds == ["task.lease"]


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


def test_advance_queue_promotes_expanded_research_types(fake_ops):
    # Types added to the autonomy policy: profile-system, define-metrics,
    # apply-retros, analyze-archetypes. They now auto-promote.
    _make_inbox_task(fake_ops, "tsk-20260422-777010", "profile-system")
    _make_inbox_task(fake_ops, "tsk-20260422-777011", "define-metrics")
    _make_inbox_task(fake_ops, "tsk-20260422-777012", "apply-retros")
    _make_inbox_task(fake_ops, "tsk-20260422-777013", "analyze-archetypes")

    promoted = q.advance_queue()
    assert set(promoted) == {
        "tsk-20260422-777010",
        "tsk-20260422-777011",
        "tsk-20260422-777012",
        "tsk-20260422-777013",
    }
    for tid in promoted:
        assert (fake_ops / "tasks" / "ready" / f"{tid}.yaml").exists()
        assert not (fake_ops / "tasks" / "inbox" / f"{tid}.yaml").exists()


def test_advance_queue_skips_warehouse_and_release_types(fake_ops):
    # materialize-warehouse and build-release stay gated — their artifacts
    # (warehouse/, releases/) are hard to undo from the planned webUI prune.
    _make_inbox_task(fake_ops, "tsk-20260422-777014", "materialize-warehouse")
    _make_inbox_task(fake_ops, "tsk-20260422-777015", "build-release")

    promoted = q.advance_queue()
    assert promoted == []
    for tid in ("tsk-20260422-777014", "tsk-20260422-777015"):
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


def test_advance_queue_tight_cap_for_review_records(fake_ops):
    # review-records has a per-type override of 1 so the self-improvement
    # loop can't starve catalog-growth task types.
    assert q._ready_cap_for("review-records") == 1
    assert q._ready_cap_for("scout-systems") == q.PER_TYPE_READY_CAP
    # Seed ready/ with one review-records task.
    tid_in_ready = "tsk-20260422-777040"
    path = fake_ops / "tasks" / "ready" / f"{tid_in_ready}.yaml"
    dump_yaml(
        {
            "id": tid_in_ready,
            "type": "review-records",
            "skill": "review-records",
            "state": "ready",
            "priority": "normal",
            "output_targets": ["ops/runs/noop.json"],
            "acceptance_tests": [],
            "lease": {"ttl_minutes": 30, "max_attempts": 1},
            "created_at": "2026-04-22T00:00:00Z",
        },
        path,
    )
    _make_inbox_task(fake_ops, "tsk-20260422-777041", "review-records")
    _make_inbox_task(fake_ops, "tsk-20260422-777042", "review-records")
    # scout-systems should still promote — different type, different cap.
    _make_inbox_task(fake_ops, "tsk-20260422-777043", "scout-systems")

    promoted = q.advance_queue()
    assert promoted == ["tsk-20260422-777043"]
    for waiting in ("tsk-20260422-777041", "tsk-20260422-777042"):
        assert (fake_ops / "tasks" / "inbox" / f"{waiting}.yaml").exists()
    assert (fake_ops / "tasks" / "ready" / "tsk-20260422-777043.yaml").exists()


def _make_blocked_task(
    tasks_root: Path,
    task_id: str,
    unblock: dict | None = None,
) -> Path:
    path = tasks_root / "tasks" / "blocked" / f"{task_id}.yaml"
    data: dict = {
        "id": task_id,
        "type": "scout-systems",
        "skill": "scout-systems",
        "state": "blocked",
        "priority": "normal",
        "output_targets": ["ops/tasks/inbox/"],
        "acceptance_tests": [],
        "lease": {
            "ttl_minutes": 90,
            "max_attempts": 1,
            "attempts": 1,
            "leased_by": "prior-agent/1",
            "leased_at": "2026-04-23T00:00:00Z",
            "last_heartbeat": "2026-04-23T00:10:00Z",
        },
        "created_at": "2026-04-23T00:00:00Z",
    }
    if unblock is not None:
        data["unblock"] = unblock
    dump_yaml(data, path)
    return path


def _fake_taxonomy(monkeypatch, slugs_by_prefix: dict[str, set[str]]) -> None:
    """Stub coc.taxonomy.load_index so queue's slug check doesn't hit disk."""
    from coc import taxonomy as t

    def _load() -> t.TaxonomyIndex:
        return t.TaxonomyIndex(by_prefix=dict(slugs_by_prefix))

    monkeypatch.setattr(t, "load_index", _load)


def test_sweep_blocked_moves_when_taxonomy_slug_present(fake_ops, monkeypatch):
    _fake_taxonomy(monkeypatch, {"system-class": {"atomic-system"}})
    tid = "tsk-20260423-555001"
    _make_blocked_task(
        fake_ops,
        tid,
        unblock={
            "kind": "taxonomy-slug-exists",
            "taxonomy_ref": "system-class:atomic-system",
        },
    )

    unblocked = q.sweep_blocked()
    assert unblocked == [tid]

    ready_path = fake_ops / "tasks" / "ready" / f"{tid}.yaml"
    assert ready_path.exists()
    assert not (fake_ops / "tasks" / "blocked" / f"{tid}.yaml").exists()

    from coc.yamlio import load_yaml

    data = load_yaml(ready_path)
    assert data["state"] == "ready"
    assert data["lease"]["attempts"] == 0
    assert data["lease"]["leased_by"] is None
    assert data["lease"]["leased_at"] is None
    assert data["lease"]["last_heartbeat"] is None
    # Unblock field is preserved so a repeat block can reuse the condition.
    assert data["unblock"]["taxonomy_ref"] == "system-class:atomic-system"

    kinds = _event_kinds(fake_ops)
    assert kinds[-1] == "task.unblock"


def test_sweep_blocked_leaves_tasks_when_slug_absent(fake_ops, monkeypatch):
    _fake_taxonomy(monkeypatch, {"system-class": {"something-else"}})
    tid = "tsk-20260423-555002"
    _make_blocked_task(
        fake_ops,
        tid,
        unblock={
            "kind": "taxonomy-slug-exists",
            "taxonomy_ref": "system-class:atomic-system",
        },
    )

    assert q.sweep_blocked() == []
    assert (fake_ops / "tasks" / "blocked" / f"{tid}.yaml").exists()


def test_sweep_blocked_ignores_tasks_without_unblock(fake_ops, monkeypatch):
    _fake_taxonomy(monkeypatch, {"system-class": {"atomic-system"}})
    tid = "tsk-20260423-555003"
    _make_blocked_task(fake_ops, tid, unblock=None)

    assert q.sweep_blocked() == []
    assert (fake_ops / "tasks" / "blocked" / f"{tid}.yaml").exists()


def test_sweep_blocked_moves_when_named_task_is_done(fake_ops, monkeypatch):
    _fake_taxonomy(monkeypatch, {})
    upstream = "tsk-20260423-555010"
    blocked_id = "tsk-20260423-555011"
    # Upstream sitting in done/
    done_path = fake_ops / "tasks" / "done" / f"{upstream}.yaml"
    dump_yaml(
        {
            "id": upstream,
            "type": "review-records",
            "skill": "review-records",
            "state": "done",
            "priority": "normal",
            "output_targets": ["taxonomy/source/system-classes.yaml"],
            "acceptance_tests": [],
            "lease": {"ttl_minutes": 30, "max_attempts": 1},
            "created_at": "2026-04-23T00:00:00Z",
        },
        done_path,
    )
    _make_blocked_task(
        fake_ops,
        blocked_id,
        unblock={"kind": "task-complete", "task_id": upstream},
    )

    assert q.sweep_blocked() == [blocked_id]
    assert (fake_ops / "tasks" / "ready" / f"{blocked_id}.yaml").exists()


def test_sweep_blocked_skips_task_complete_when_not_done(fake_ops, monkeypatch):
    _fake_taxonomy(monkeypatch, {})
    blocked_id = "tsk-20260423-555012"
    # Named upstream does not exist anywhere
    _make_blocked_task(
        fake_ops,
        blocked_id,
        unblock={"kind": "task-complete", "task_id": "tsk-20260423-999999"},
    )

    assert q.sweep_blocked() == []
    assert (fake_ops / "tasks" / "blocked" / f"{blocked_id}.yaml").exists()


def test_sweep_blocked_skips_malformed_spec(fake_ops, monkeypatch):
    _fake_taxonomy(monkeypatch, {"system-class": {"atomic-system"}})
    tid = "tsk-20260423-555013"
    # Missing taxonomy_ref; kind alone is insufficient.
    _make_blocked_task(
        fake_ops, tid, unblock={"kind": "taxonomy-slug-exists"}
    )

    assert q.sweep_blocked() == []
    assert (fake_ops / "tasks" / "blocked" / f"{tid}.yaml").exists()


def test_unblock_task_rejects_non_blocked(fake_ops):
    tid = "tsk-20260423-555020"
    _make_task(fake_ops, tid)  # lives in ready/
    with pytest.raises(q.QueueError):
        q.unblock_task(tid)
