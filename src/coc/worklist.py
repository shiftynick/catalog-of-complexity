"""Worklist resolver for the sweep autorun model.

Given the active phase, computes the next K subjects to process from
the registry in deterministic priority-then-domain-interleave order.

The autonomous-run prompt calls `next_worklist_items(phase, k)` once
per cron tick; the resulting list of subject ids drives task-manifest
emission. This module is pure: it queries the registry filesystem and
returns subject ids; the autonomous-run code is responsible for
turning those into `ops/tasks/inbox/*.yaml` manifests and promoting
them to ready/.

Phase → subject-source mapping:

    system-profiling   → systems with status: bootstrap-stub
    metric-definition  → metrics with status: bootstrap-stub
    matrix-fill        → systems with status: candidate or profiled
                         that have not yet been processed by a
                         fill-system-metrics task

Ordering for system-shaped phases (system-profiling, matrix-fill):

    1. Primary key: priority bucket (P0 → P1 → P2 → P3 → C → unset)
    2. Within bucket: round-robin across system-domain slugs
       (deterministic by domain slug ordering in
       taxonomy/source/system-domains.yaml)
    3. Within (bucket, domain): system slug ascending

Ordering for metric-definition phase:

    1. Primary key: maturity_level inverted (L2 first, then L1, L0,
       L3) — the most operationally well-defined metrics first because
       their rubrics are easiest to write
    2. Secondary: family slug ascending
    3. Tertiary: metric slug ascending

The resolver does NOT modify state. It does NOT promote anything to
ready/. It is a pure read-and-sort function suitable for testing in
isolation.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from coc.paths import REG_METRICS, REG_SYSTEMS, TAXONOMY_SRC
from coc.yamlio import load_yaml

PRIORITY_ORDER: list[str | None] = ["P0", "P1", "P2", "P3", "C", None]
MATURITY_ORDER_FOR_METRICS: list[str | None] = ["L2", "L1", "L0", "L3", "L4", "L5", None]


@dataclass(frozen=True)
class SystemSubject:
    """Lightweight handle on a system entry — only the fields the
    resolver needs for filtering and sorting."""

    id: str
    slug: str
    status: str
    priority: str | None
    domain: str
    has_observations: bool


@dataclass(frozen=True)
class MetricSubject:
    """Lightweight handle on a metric entry."""

    id: str
    slug: str
    status: str
    family: str
    maturity_level: str | None


def _domain_order() -> list[str]:
    """Read the canonical ordering of system-domains for deterministic
    round-robin. Falls back to alphabetical if the taxonomy file is
    missing."""
    path = TAXONOMY_SRC / "system-domains.yaml"
    if not path.exists():
        return []
    data = load_yaml(path) or {}
    return [item["slug"] for item in data.get("items", []) if "slug" in item]


def _load_systems() -> list[SystemSubject]:
    out: list[SystemSubject] = []
    if not REG_SYSTEMS.exists():
        return out
    for entry in sorted(REG_SYSTEMS.iterdir()):
        if not entry.is_dir():
            continue
        sys_path = entry / "system.yaml"
        if not sys_path.exists():
            continue
        d = load_yaml(sys_path) or {}
        domain = ""
        for ref in d.get("taxonomy_refs", []):
            if ref.startswith("system-domain:"):
                domain = ref.split(":", 1)[1]
                break
        obs_dir = entry.parent.parent / "observations" / d.get("id", "")
        # Cheaper: probe by walking REG_OBSERVATIONS later in callers; here we
        # approximate "has any observations" by directory existence to keep
        # the resolver O(systems).
        from coc.paths import REG_OBSERVATIONS

        obs_for_sys = REG_OBSERVATIONS / d.get("id", "")
        has_obs = obs_for_sys.exists() and any(obs_for_sys.glob("*.jsonl"))
        out.append(
            SystemSubject(
                id=d.get("id", ""),
                slug=d.get("slug", ""),
                status=d.get("status", ""),
                priority=d.get("priority"),
                domain=domain,
                has_observations=has_obs,
            )
        )
    return out


def _load_metrics() -> list[MetricSubject]:
    out: list[MetricSubject] = []
    if not REG_METRICS.exists():
        return out
    for entry in sorted(REG_METRICS.iterdir()):
        if not entry.is_dir():
            continue
        mtr_path = entry / "metric.yaml"
        if not mtr_path.exists():
            continue
        d = load_yaml(mtr_path) or {}
        out.append(
            MetricSubject(
                id=d.get("id", ""),
                slug=d.get("slug", ""),
                status=d.get("status", ""),
                family=d.get("family", ""),
                maturity_level=d.get("maturity_level"),
            )
        )
    return out


def _interleave_by_domain(
    items: list[SystemSubject], domain_seq: list[str]
) -> list[SystemSubject]:
    """Round-robin items across domains in `domain_seq` order. Items
    whose domain isn't in the sequence go to the tail in slug order."""
    by_domain: dict[str, list[SystemSubject]] = defaultdict(list)
    for it in items:
        by_domain[it.domain].append(it)
    # Sort within each domain by slug for determinism
    for d in by_domain:
        by_domain[d].sort(key=lambda s: s.slug)

    result: list[SystemSubject] = []
    queues = [list(by_domain[d]) for d in domain_seq if d in by_domain]
    while any(queues):
        for q in queues:
            if q:
                result.append(q.pop(0))
    # Append items with unknown / unlisted domains
    listed = set(domain_seq)
    leftover = sorted(
        (it for it in items if it.domain not in listed),
        key=lambda s: (s.domain, s.slug),
    )
    result.extend(leftover)
    return result


def system_worklist_for_profiling(systems: list[SystemSubject] | None = None) -> list[SystemSubject]:
    """Systems remaining to be upgraded from bootstrap-stub. Ordered:
    priority bucket (P0..C), within each bucket round-robin by domain."""
    if systems is None:
        systems = _load_systems()
    pending = [s for s in systems if s.status == "bootstrap-stub"]
    domain_seq = _domain_order()

    out: list[SystemSubject] = []
    for prio in PRIORITY_ORDER:
        bucket = [s for s in pending if s.priority == prio]
        out.extend(_interleave_by_domain(bucket, domain_seq))
    return out


def system_worklist_for_matrix_fill(systems: list[SystemSubject] | None = None) -> list[SystemSubject]:
    """Systems eligible for fill-system-metrics. Status must be
    candidate or profiled (NOT bootstrap-stub). Skips systems that
    already have observations on disk (proxy for `already filled`).
    Ordering same as profiling."""
    if systems is None:
        systems = _load_systems()
    pending = [
        s
        for s in systems
        if s.status in ("candidate", "profiled") and not s.has_observations
    ]
    domain_seq = _domain_order()

    out: list[SystemSubject] = []
    for prio in PRIORITY_ORDER:
        bucket = [s for s in pending if s.priority == prio]
        out.extend(_interleave_by_domain(bucket, domain_seq))
    return out


def metric_worklist_for_definition(metrics: list[MetricSubject] | None = None) -> list[MetricSubject]:
    """Metrics remaining to be upgraded from bootstrap-stub. Ordered:
    maturity-level descending operational-ness (L2 → L1 → L0 → L3+),
    then family slug, then metric slug."""
    if metrics is None:
        metrics = _load_metrics()
    pending = [m for m in metrics if m.status == "bootstrap-stub"]
    out: list[MetricSubject] = []
    for ml in MATURITY_ORDER_FOR_METRICS:
        bucket = [m for m in pending if m.maturity_level == ml]
        bucket.sort(key=lambda m: (m.family, m.slug))
        out.extend(bucket)
    return out


def next_worklist_items(phase: str, k: int) -> list[str]:
    """Return up to K subject ids for the given phase, in worklist
    order. Caller is responsible for emitting task manifests + promoting
    to ready/.

    Returns subject ids (sys-NNN--<slug> or mtr-NNN--<slug>), not
    full subject objects. Callers that need the rich metadata should
    call the phase-specific functions above and slice the result.
    """
    if phase == "system-profiling":
        wl = system_worklist_for_profiling()
        return [s.id for s in wl[:k]]
    if phase == "metric-definition":
        wl = metric_worklist_for_definition()
        return [m.id for m in wl[:k]]
    if phase == "matrix-fill":
        wl = system_worklist_for_matrix_fill()
        return [s.id for s in wl[:k]]
    return []


def phase_worklist_size(phase: str) -> int:
    """Total remaining items for the active phase. Useful for
    completion-check and progress reporting."""
    if phase == "system-profiling":
        return len(system_worklist_for_profiling())
    if phase == "metric-definition":
        return len(metric_worklist_for_definition())
    if phase == "matrix-fill":
        return len(system_worklist_for_matrix_fill())
    return 0
