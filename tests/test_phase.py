"""Tests for `coc.phase` — phase state machine + auto-advance."""

from __future__ import annotations

from coc.phase import (
    advance_phase,
    auto_advance_enabled,
    current_phase,
    phase_completion_check,
    phase_to_task_type,
    side_channel_cap,
)


def test_current_phase_against_live_config():
    """Reads config/phase.yaml as committed; should be a known value."""
    p = current_phase()
    assert p in ("system-profiling", "metric-definition", "matrix-fill", "analysis")


def test_auto_advance_default_true():
    assert auto_advance_enabled() is True


def test_phase_to_task_type_mapping():
    assert phase_to_task_type("system-profiling") == "profile-system"
    assert phase_to_task_type("metric-definition") == "define-metrics"
    assert phase_to_task_type("matrix-fill") == "fill-system-metrics"
    # analysis is human-gated; resolver should not auto-dispatch
    assert phase_to_task_type("analysis") is None


def test_side_channel_cap_for_matrix_fill_is_10():
    """matrix-fill raises acquire-source cap to 10 because
    fill-system-metrics emits many during execution."""
    assert side_channel_cap("acquire-source", phase="matrix-fill") == 10
    assert side_channel_cap("acquire-source", phase="system-profiling") == 3


def test_side_channel_cap_unknown_returns_zero():
    assert side_channel_cap("nonsense-channel", phase="system-profiling") == 0


def test_phase_completion_check_returns_none_while_worklist_nonempty():
    """In the live registry, system-profiling phase has 639 stubs;
    completion check should return None and the reason should mention
    worklist size."""
    nxt, reason = phase_completion_check(phase="system-profiling")
    assert nxt is None
    assert "worklist size" in reason or "satisfied" in reason


def test_phase_completion_check_matrix_fill_never_advances():
    """matrix-fill is open-ended (next: null, when: never). Should
    always return None regardless of registry state."""
    nxt, reason = phase_completion_check(phase="matrix-fill")
    assert nxt is None


def test_advance_phase_writes_config(tmp_path, monkeypatch):
    """advance_phase rewrites config/phase.yaml::current. We monkeypatch
    PHASE_FILE to a temp path so this test doesn't mutate the live
    repo state."""
    fake_cfg = tmp_path / "phase.yaml"
    fake_cfg.write_text(
        "current: system-profiling\nauto_advance: true\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("coc.phase.PHASE_FILE", fake_cfg)
    advance_phase("metric-definition")
    from coc.yamlio import load_yaml

    cfg = load_yaml(fake_cfg)
    assert cfg["current"] == "metric-definition"


def test_advance_phase_rejects_invalid_phase():
    import pytest

    with pytest.raises(ValueError):
        advance_phase("not-a-real-phase")
