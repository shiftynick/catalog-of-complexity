"""Phase-state machinery for the sweep autorun model.

The catalog progresses through a small state machine of phases:

    system-profiling   →  metric-definition  →  matrix-fill  →  analysis

Each phase pins one primary task type. autonomous-run.md reads the
active phase, asks `worklist.next_worklist_items(phase, k)` for the
next K subjects, and dispatches them via `dispatch.emit_phase_task()`.

Phase auto-advance: after a tick's last commit, the autonomous-run
calls `phase_completion_check()`. If the active phase's worklist is
now empty, the helper rewrites `config/phase.yaml::current` to the
next phase and the caller writes a `phase.advance` event.

Phase metadata lives in `config/phase.yaml`:

    current: system-profiling
    auto_advance: true
    phase_to_task_type:   {phase: task_type}
    side_channels:        {phase: {channel: cap_per_tick}}
    phase_advance:        {phase: {next: ..., when: ...}}

This module is small and well-tested; advance and completion checks
are pure (read-only against registry).
"""

from __future__ import annotations

from typing import Any

from coc.paths import CONFIG
from coc.yamlio import dump_yaml, load_yaml

PHASE_FILE = CONFIG / "phase.yaml"

VALID_PHASES = ("system-profiling", "metric-definition", "matrix-fill", "analysis")
DEFAULT_PHASE = "system-profiling"

DEFAULT_PHASE_TO_TASK_TYPE: dict[str, str] = {
    "system-profiling": "profile-system",
    "metric-definition": "define-metrics",
    "matrix-fill": "fill-system-metrics",
    "analysis": "analyze-archetypes",
}

DEFAULT_SIDE_CHANNEL_CAPS: dict[str, dict[str, int]] = {
    "system-profiling": {"acquire-source": 3, "review-records": 1},
    "metric-definition": {"acquire-source": 5, "review-records": 1},
    "matrix-fill": {"acquire-source": 10, "review-records": 1},
    "analysis": {"acquire-source": 3, "review-records": 1},
}

DEFAULT_PHASE_ADVANCE: dict[str, dict[str, Any]] = {
    "system-profiling": {"next": "metric-definition", "when": "zero_systems_at_bootstrap_stub"},
    "metric-definition": {"next": "matrix-fill", "when": "zero_metrics_at_bootstrap_stub"},
    "matrix-fill": {"next": None, "when": "never"},  # human-advanced to analysis
    "analysis": {"next": None, "when": "never"},
}


def _load_config() -> dict[str, Any]:
    if not PHASE_FILE.exists():
        return {}
    return load_yaml(PHASE_FILE) or {}


def current_phase() -> str:
    """Active phase name. Falls back to DEFAULT_PHASE on missing/invalid value."""
    cfg = _load_config()
    name = cfg.get("current") or DEFAULT_PHASE
    if name not in VALID_PHASES:
        return DEFAULT_PHASE
    return name


def auto_advance_enabled() -> bool:
    return bool(_load_config().get("auto_advance", True))


def phase_to_task_type(phase: str | None = None) -> str | None:
    """Primary task type emitted for the given phase. Returns None if the
    phase has no auto-dispatched primary type (e.g. analysis is human-gated)."""
    phase = phase or current_phase()
    cfg = _load_config()
    mapping = cfg.get("phase_to_task_type") or DEFAULT_PHASE_TO_TASK_TYPE
    tt = mapping.get(phase)
    # Treat 'analyze-archetypes' as not-auto-dispatched: it's human-promoted
    # only, and the autorun should not seed it.
    if phase == "analysis":
        return None
    return tt


def side_channel_cap(channel: str, phase: str | None = None) -> int:
    """Per-tick cap for a side-channel task type (acquire-source,
    review-records, apply-retros) under the active phase."""
    phase = phase or current_phase()
    cfg = _load_config()
    caps = cfg.get("side_channels") or DEFAULT_SIDE_CHANNEL_CAPS
    return int((caps.get(phase) or {}).get(channel, 0))


def _completion_satisfied(when: str) -> tuple[bool, str]:
    """Evaluate the completion predicate. Read-only against registry."""
    if when == "never":
        return False, "phase has no auto-advance trigger"
    if when == "zero_systems_at_bootstrap_stub":
        # Lazy import to avoid pulling registry I/O at module load time.
        from coc.worklist import phase_worklist_size

        n = phase_worklist_size("system-profiling")
        return (n == 0, f"system-profiling worklist size = {n}")
    if when == "zero_metrics_at_bootstrap_stub":
        from coc.worklist import phase_worklist_size

        n = phase_worklist_size("metric-definition")
        return (n == 0, f"metric-definition worklist size = {n}")
    return False, f"unknown completion predicate: {when}"


def phase_completion_check(phase: str | None = None) -> tuple[str | None, str]:
    """Return (next_phase, reason). next_phase is None if the active phase
    is not yet complete or has no auto-advance target. The caller is
    responsible for actually flipping the config (see `advance_phase`)
    and writing a phase.advance event."""
    if not auto_advance_enabled():
        return None, "auto_advance disabled in config/phase.yaml"
    phase = phase or current_phase()
    cfg = _load_config()
    advance = cfg.get("phase_advance") or DEFAULT_PHASE_ADVANCE
    spec = advance.get(phase)
    if not spec:
        return None, f"no phase_advance spec for {phase}"
    next_phase = spec.get("next")
    when = spec.get("when") or "never"
    if next_phase is None:
        return None, f"phase {phase} has no next phase ({when})"
    satisfied, why = _completion_satisfied(when)
    if not satisfied:
        return None, f"completion predicate not yet satisfied: {why}"
    return next_phase, why


def advance_phase(next_phase: str) -> None:
    """Rewrite `config/phase.yaml::current` to next_phase. Caller must
    write a phase.advance event separately so the change is auditable."""
    if next_phase not in VALID_PHASES:
        raise ValueError(f"invalid phase: {next_phase}")
    cfg = _load_config()
    cfg["current"] = next_phase
    dump_yaml(cfg, PHASE_FILE)
