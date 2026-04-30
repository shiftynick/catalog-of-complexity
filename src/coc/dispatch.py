"""Task-manifest emitter for the sweep autorun model.

Given (phase, subject_id), build the task-manifest dict and write it
to `ops/tasks/inbox/tsk-YYYYMMDD-NNNNNN.yaml`. The autonomous-run
prompt calls this once per worklist item per cron tick; `coc advance`
in the next preflight step will promote the inbox manifest to ready/.

The manifest shape is per-phase:

  system-profiling   →  profile-system task     (subject = sys-* id)
  metric-definition  →  define-metrics task     (subject = mtr-* id)
  matrix-fill        →  fill-system-metrics task (subject = sys-* id)

Each manifest:

  * Validates against schemas/task.schema.json.
  * Carries a `notes` field naming the dispatch source (so plan-backlog
    Tier-0.75 source-debt sweep and review-records can correlate).
  * Has `state: inbox` (autorun's preflight `coc advance` promotes it).
  * Has `priority: normal` and a sensible per-phase lease ttl_minutes.

Idempotency: if a task is already in flight against the same subject
(same skill, same target id, in inbox/ready/leased/running), skip
emission. Returns the existing task id when found.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from coc.paths import OPS_TASKS, REG_METRICS, REG_SYSTEMS
from coc.yamlio import dump_yaml, load_yaml

INBOX = OPS_TASKS / "inbox"
ACTIVE_STATES = ("inbox", "ready", "leased", "running")


def _ts_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _next_task_id(date_prefix: str) -> str:
    """Allocate the next free `tsk-YYYYMMDD-NNNNNN` for the given date,
    scanning all task states."""
    pat = re.compile(rf"^tsk-{re.escape(date_prefix)}-([0-9]{{6}})\.yaml$")
    used: set[int] = set()
    for state_dir in OPS_TASKS.iterdir() if OPS_TASKS.exists() else ():
        if not state_dir.is_dir():
            continue
        for f in state_dir.iterdir():
            m = pat.match(f.name)
            if m:
                used.add(int(m.group(1)))
    n = 1
    while n in used:
        n += 1
    return f"tsk-{date_prefix}-{n:06d}"


def _existing_task_for_subject(skill: str, subject_field: str, subject_id: str) -> str | None:
    """Return existing task id (e.g. tsk-...) if a task with the same
    skill + subject is already in active state. Otherwise None."""
    for state in ACTIVE_STATES:
        d = OPS_TASKS / state
        if not d.exists():
            continue
        for f in d.glob("*.yaml"):
            data = load_yaml(f) or {}
            if data.get("skill") == skill and data.get(subject_field) == subject_id:
                return data.get("id")
    return None


def _read_system_stub(sys_id: str) -> dict:
    path = REG_SYSTEMS / sys_id / "system.yaml"
    if not path.exists():
        raise FileNotFoundError(f"system not found: {sys_id}")
    return load_yaml(path) or {}


def _read_metric_stub(mtr_id: str) -> dict:
    path = REG_METRICS / mtr_id / "metric.yaml"
    if not path.exists():
        raise FileNotFoundError(f"metric not found: {mtr_id}")
    return load_yaml(path) or {}


def build_profile_system_manifest(sys_id: str, ts: str | None = None) -> dict:
    """profile-system upgrade task for one bootstrap-stub system."""
    ts = ts or _ts_iso()
    stub = _read_system_stub(sys_id)
    summary = (stub.get("summary") or "").strip().replace("\n", " ")
    domain = ""
    classes: list[str] = []
    for ref in stub.get("taxonomy_refs", []):
        if ref.startswith("system-domain:"):
            domain = ref.split(":", 1)[1]
        elif ref.startswith("system-class:"):
            classes.append(ref.split(":", 1)[1])
    date_prefix = ts[:10].replace("-", "")
    tid = _next_task_id(date_prefix)
    return {
        "id": tid,
        "type": "profile-system",
        "skill": "profile-system",
        "state": "inbox",
        "system_id": sys_id,
        "output_targets": [
            f"registry/systems/{sys_id}/system.yaml",
            f"registry/systems/{sys_id}/notes.md",
            f"registry/systems/{sys_id}/links.yaml",
        ],
        "acceptance_tests": [
            "system.yaml validates against schemas/system.schema.json with status: candidate",
            "all taxonomy refs resolve",
            "boundary, components, interaction_types, scales populated with specifics (not bootstrap-stub placeholders)",
            ">=4 of the 9 v0.2 structural facets populated (system_kind, substrate, origin, boundary_clarity, primary_function, lifecycle_stage, main_feedbacks, dominant_constraints, emergent_properties, failure_modes, primary_resources)",
            "canonical_examples lists >=3 instances OR notes.md justifies why the type is genuinely singular",
        ],
        "notes": (
            f"Phase: system-profiling. Stub upgrade for {sys_id}. "
            f"Domain: {domain}. Classes: {', '.join(classes) if classes else '(none)'}. "
            f"Source provenance from existing summary: {summary[:200]}"
        ),
        "priority": "normal",
        "lease": {"ttl_minutes": 60, "max_attempts": 2},
        "created_at": ts,
    }


def build_define_metrics_manifest(mtr_id: str, ts: str | None = None) -> dict:
    """define-metrics upgrade task for one bootstrap-stub metric."""
    ts = ts or _ts_iso()
    stub = _read_metric_stub(mtr_id)
    family = stub.get("family") or ""
    description = (stub.get("description") or "").strip().replace("\n", " ")
    slug = stub.get("slug") or ""
    date_prefix = ts[:10].replace("-", "")
    tid = _next_task_id(date_prefix)
    return {
        "id": tid,
        "type": "define-metrics",
        "skill": "define-metrics",
        "state": "inbox",
        "metric_ids": [mtr_id],
        "output_targets": [
            f"registry/metrics/{mtr_id}/metric.yaml",
            f"registry/metrics/{mtr_id}/rubric.md",
            f"registry/metrics/{mtr_id}/examples.yaml",
        ],
        "acceptance_tests": [
            "metric.yaml validates against schemas/metric.schema.json with status in (proposed, canonical)",
            "rubric.md contains >=3 worked examples spanning >=2 system-domain slugs",
            "examples.yaml contains >=3 entries",
            "applicability.requires and applicability.excludes populated (or empty arrays with explicit rationale in rubric.md)",
            "scale_level and maturity_level set",
        ],
        "notes": (
            f"Phase: metric-definition. Rubric upgrade for {mtr_id} (slug={slug}, "
            f"family={family}). Stub description: {description[:200]}"
        ),
        "priority": "normal",
        "lease": {"ttl_minutes": 60, "max_attempts": 2},
        "created_at": ts,
    }


def build_fill_system_metrics_manifest(
    sys_id: str, metric_filter: list[str] | None = None, ts: str | None = None
) -> dict:
    """fill-system-metrics task for one fully-profiled system."""
    ts = ts or _ts_iso()
    date_prefix = ts[:10].replace("-", "")
    tid = _next_task_id(date_prefix)
    note = f"Phase: matrix-fill. System-fill for {sys_id}."
    if metric_filter:
        note += f" Restricted to metric_filter ({len(metric_filter)} metrics)."
    rec: dict = {
        "id": tid,
        "type": "fill-system-metrics",
        "skill": "fill-system-metrics",
        "state": "inbox",
        "system_id": sys_id,
        "output_targets": [
            f"registry/observations/{sys_id}/",
            "registry/sources/",
            "ops/tasks/inbox/",
        ],
        "acceptance_tests": [
            "every applicable metric is classified as extracted, skipped_undefined, or blocked_source_not_acquired",
            "every extracted observation carries run_id and produced_by_task_id (v0.3 fields)",
            "every blocked_source_not_acquired entry has a paired acquire-source task in ops/tasks/inbox/ (or an existing one)",
            "no observation overwrites a prior row in place; all writes are append-only",
        ],
        "notes": note,
        "priority": "normal",
        "lease": {"ttl_minutes": 90, "max_attempts": 2},
        "created_at": ts,
    }
    if metric_filter:
        rec["metric_ids"] = list(metric_filter)
    return rec


PHASE_DISPATCHERS = {
    "system-profiling": ("profile-system", "system_id", build_profile_system_manifest),
    "metric-definition": ("define-metrics", "metric_ids", build_define_metrics_manifest),
    "matrix-fill": ("fill-system-metrics", "system_id", build_fill_system_metrics_manifest),
}


def emit_phase_task(phase: str, subject_id: str, ts: str | None = None) -> tuple[str, Path | None]:
    """Build a task manifest for (phase, subject_id) and write it into
    ops/tasks/inbox/. Idempotent: returns the existing task id (and
    None for path) if a task with the same skill + subject is already
    in flight.

    Returns (task_id, path). path is None when an existing task was
    detected; otherwise the path of the newly-written manifest.
    """
    if phase not in PHASE_DISPATCHERS:
        raise ValueError(f"unknown phase: {phase}")
    skill, subject_field, builder = PHASE_DISPATCHERS[phase]

    # Idempotency: existing task in active state for the same subject.
    if subject_field == "metric_ids":
        # define-metrics manifest stores metric ids in a list; check membership
        existing = _existing_task_for_metric(skill, subject_id)
    else:
        existing = _existing_task_for_subject(skill, subject_field, subject_id)
    if existing:
        return existing, None

    rec = builder(subject_id, ts=ts)
    INBOX.mkdir(parents=True, exist_ok=True)
    target = INBOX / f"{rec['id']}.yaml"
    dump_yaml(rec, target)
    return rec["id"], target


def _existing_task_for_metric(skill: str, mtr_id: str) -> str | None:
    """define-metrics tasks store the metric id in metric_ids[]."""
    for state in ACTIVE_STATES:
        d = OPS_TASKS / state
        if not d.exists():
            continue
        for f in d.glob("*.yaml"):
            data = load_yaml(f) or {}
            if data.get("skill") != skill:
                continue
            if mtr_id in (data.get("metric_ids") or []):
                return data.get("id")
    return None
