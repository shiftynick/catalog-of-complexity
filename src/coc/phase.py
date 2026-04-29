"""Project-phase reader.

Phase gates which plan-backlog tiers fire on each scheduled invocation.
See `config/phase.yaml` for the vocabulary and `skills/plan-backlog/SKILL.md`
for how the tier list maps to gap heuristics.

This module is intentionally tiny: the file is small, validation is
permissive (a typo in `current` falls back to `discovery` rather than
exploding the autorun), and the helper short-circuits when the file
doesn't exist (treated as legacy `discovery` behavior).
"""

from __future__ import annotations

from coc.paths import CONFIG
from coc.yamlio import load_yaml

PHASE_FILE = CONFIG / "phase.yaml"

VALID_PHASES = ("bootstrap", "metrics-fill", "discovery", "analysis")
DEFAULT_PHASE = "discovery"

# Default tier gating if config/phase.yaml is missing. Mirrors the file's
# defaults so legacy repos behave as `discovery` until they opt in.
_DEFAULT_TIER_GATING: dict[str, tuple[str, ...]] = {
    "0":    ("discovery",),
    "0.5":  ("discovery",),
    "0.75": ("bootstrap", "metrics-fill", "discovery"),
    "1":    ("bootstrap", "metrics-fill", "discovery", "analysis"),
    "2":    ("metrics-fill", "discovery"),
    "3":    ("bootstrap", "metrics-fill", "discovery"),
    "4":    ("metrics-fill", "discovery"),
    "5":    ("discovery",),
}


def current_phase() -> str:
    """Return the phase name from config/phase.yaml, falling back to default."""
    if not PHASE_FILE.exists():
        return DEFAULT_PHASE
    data = load_yaml(PHASE_FILE) or {}
    name = data.get("current") or DEFAULT_PHASE
    if name not in VALID_PHASES:
        return DEFAULT_PHASE
    return name


def tier_fires(tier: str, phase: str | None = None) -> bool:
    """True if `tier` (e.g. "0.5", "2") should fire under the active phase."""
    phase = phase or current_phase()
    data = load_yaml(PHASE_FILE) if PHASE_FILE.exists() else None
    if data and isinstance(data.get("tier_gating"), dict):
        allowed = data["tier_gating"].get(tier)
        if allowed is None:
            # Tier not listed: be conservative — fire only in discovery.
            return phase == "discovery"
        return phase in allowed
    return phase in _DEFAULT_TIER_GATING.get(tier, ())
