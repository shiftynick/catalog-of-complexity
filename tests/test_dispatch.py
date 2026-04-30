"""Tests for `coc.dispatch` — phase-driven task manifest emission."""

from __future__ import annotations

import pytest

from coc.dispatch import (
    PHASE_DISPATCHERS,
    build_define_metrics_manifest,
    build_fill_system_metrics_manifest,
    build_profile_system_manifest,
    emit_phase_task,
)
from coc.schemas import validate_instance


def _first_existing_sys_id() -> str:
    """Pick a real sys-* id from the live registry for tests that
    need to read a stub. Returns the lowest-numbered one with status
    bootstrap-stub if any, else the lowest-numbered candidate."""
    from coc.paths import REG_SYSTEMS
    from coc.yamlio import load_yaml

    cands: list[tuple[str, str]] = []  # (status, id)
    for d in sorted(REG_SYSTEMS.iterdir()):
        if not d.is_dir():
            continue
        f = d / "system.yaml"
        if not f.exists():
            continue
        rec = load_yaml(f) or {}
        cands.append((rec.get("status", ""), rec.get("id", "")))
    # Prefer bootstrap-stub for testing the upgrade-flow manifests
    stubs = [c for c in cands if c[0] == "bootstrap-stub"]
    if stubs:
        return stubs[0][1]
    return cands[0][1] if cands else ""


def _first_existing_mtr_id() -> str:
    from coc.paths import REG_METRICS
    from coc.yamlio import load_yaml

    for d in sorted(REG_METRICS.iterdir()):
        if not d.is_dir():
            continue
        f = d / "metric.yaml"
        if not f.exists():
            continue
        rec = load_yaml(f) or {}
        return rec.get("id", "")
    return ""


def test_phase_dispatchers_cover_all_three_active_phases():
    """The dispatcher table must cover system-profiling,
    metric-definition, and matrix-fill. analysis is human-gated."""
    assert set(PHASE_DISPATCHERS.keys()) == {
        "system-profiling",
        "metric-definition",
        "matrix-fill",
    }


def test_profile_system_manifest_validates():
    sys_id = _first_existing_sys_id()
    if not sys_id:
        pytest.skip("no systems in registry to dispatch")
    rec = build_profile_system_manifest(sys_id)
    errs = validate_instance("task", rec)
    assert not errs, errs
    assert rec["type"] == "profile-system"
    assert rec["system_id"] == sys_id
    assert rec["state"] == "inbox"
    assert "v0.2 structural facets" in " ".join(rec["acceptance_tests"])


def test_define_metrics_manifest_validates():
    mtr_id = _first_existing_mtr_id()
    if not mtr_id:
        pytest.skip("no metrics in registry")
    rec = build_define_metrics_manifest(mtr_id)
    errs = validate_instance("task", rec)
    assert not errs, errs
    assert rec["type"] == "define-metrics"
    assert mtr_id in rec["metric_ids"]


def test_fill_system_metrics_manifest_validates():
    sys_id = _first_existing_sys_id()
    if not sys_id:
        pytest.skip("no systems in registry")
    rec = build_fill_system_metrics_manifest(sys_id)
    errs = validate_instance("task", rec)
    assert not errs, errs
    assert rec["type"] == "fill-system-metrics"
    assert rec["system_id"] == sys_id
    # Must list the observations directory as a write target
    assert any("registry/observations/" in t for t in rec["output_targets"])


def test_fill_system_metrics_with_metric_filter():
    sys_id = _first_existing_sys_id()
    mtr_id = _first_existing_mtr_id()
    if not (sys_id and mtr_id):
        pytest.skip("registry too sparse")
    rec = build_fill_system_metrics_manifest(sys_id, metric_filter=[mtr_id])
    errs = validate_instance("task", rec)
    assert not errs, errs
    assert rec["metric_ids"] == [mtr_id]


def test_emit_phase_task_idempotent_on_subject(tmp_path, monkeypatch):
    """Two consecutive calls for the same (phase, subject) must NOT
    write a second manifest. The second call should return the same
    task id and a None path."""
    sys_id = _first_existing_sys_id()
    if not sys_id:
        pytest.skip("no systems in registry")
    # Redirect inbox to tmp so we don't pollute the live queue.
    fake_inbox = tmp_path / "inbox"
    fake_inbox.mkdir()
    fake_ops = tmp_path
    fake_ops_tasks = tmp_path  # dispatch reads from inbox, ready, leased, running
    # Make all four state dirs exist under fake_ops_tasks
    for s in ("inbox", "ready", "leased", "running"):
        (fake_ops_tasks / s).mkdir(exist_ok=True)
    monkeypatch.setattr("coc.dispatch.INBOX", fake_ops_tasks / "inbox")
    monkeypatch.setattr("coc.dispatch.OPS_TASKS", fake_ops_tasks)

    tid_a, path_a = emit_phase_task("system-profiling", sys_id)
    assert path_a is not None and path_a.exists()
    tid_b, path_b = emit_phase_task("system-profiling", sys_id)
    assert tid_a == tid_b
    assert path_b is None  # second call was idempotent


def test_emit_phase_task_unknown_phase_raises():
    with pytest.raises(ValueError):
        emit_phase_task("not-a-phase", "sys-000001--whatever")
