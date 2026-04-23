"""Repo-wide validation: schema-shape + taxonomy-reference resolution."""

from __future__ import annotations

import json
from pathlib import Path

from coc.paths import (
    OPS_TASKS,
    QC_FIXTURES,
    REG_METRICS,
    REG_OBSERVATIONS,
    REG_SOURCES,
    REG_SYSTEMS,
    REPO_ROOT,
    TAXONOMY_SRC,
)
from coc.schemas import validate_instance
from coc.taxonomy import load_index
from coc.yamlio import load_yaml

Problem = str


def _check_taxonomy_refs(record: dict, index, where: str) -> list[Problem]:
    """Return problems for unresolved `taxonomy_refs` or `family` references."""
    problems: list[Problem] = []
    refs = record.get("taxonomy_refs") or []
    for ref in refs:
        if not index.has(ref):
            problems.append(f"{where}: unresolved taxonomy ref '{ref}'")
    family = record.get("family")
    if family:
        qualified = f"metric-family:{family}"
        if not index.has(qualified):
            problems.append(f"{where}: unresolved metric family '{family}'")
    return problems


def _iter_yaml(pattern_root: Path, leaf_name: str):
    if not pattern_root.exists():
        return
    for entry in sorted(pattern_root.iterdir()):
        if not entry.is_dir():
            continue
        target = entry / leaf_name
        if target.exists():
            yield target


def _validate_systems(index) -> list[Problem]:
    problems: list[Problem] = []
    for path in _iter_yaml(REG_SYSTEMS, "system.yaml"):
        data = load_yaml(path) or {}
        rel = path.relative_to(REPO_ROOT).as_posix()
        for err in validate_instance("system", data):
            problems.append(f"{rel}: {err}")
        problems.extend(_check_taxonomy_refs(data, index, rel))
    return problems


def _validate_metrics(index) -> list[Problem]:
    problems: list[Problem] = []
    for path in _iter_yaml(REG_METRICS, "metric.yaml"):
        data = load_yaml(path) or {}
        rel = path.relative_to(REPO_ROOT).as_posix()
        for err in validate_instance("metric", data):
            problems.append(f"{rel}: {err}")
        problems.extend(_check_taxonomy_refs(data, index, rel))
    return problems


def _validate_sources() -> list[Problem]:
    problems: list[Problem] = []
    for path in _iter_yaml(REG_SOURCES, "source.yaml"):
        data = load_yaml(path) or {}
        rel = path.relative_to(REPO_ROOT).as_posix()
        for err in validate_instance("source", data):
            problems.append(f"{rel}: {err}")
    return problems


def _validate_observations() -> list[Problem]:
    problems: list[Problem] = []
    if not REG_OBSERVATIONS.exists():
        return problems
    for jsonl in sorted(REG_OBSERVATIONS.rglob("*.jsonl")):
        rel = jsonl.relative_to(REPO_ROOT).as_posix()
        with jsonl.open("r", encoding="utf-8") as f:
            for line_no, raw in enumerate(f, start=1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError as e:
                    problems.append(f"{rel}:{line_no}: invalid JSON: {e}")
                    continue
                for err in validate_instance("observation", obj):
                    problems.append(f"{rel}:{line_no}: {err}")
    return problems


def _validate_tasks() -> list[Problem]:
    problems: list[Problem] = []
    if not OPS_TASKS.exists():
        return problems
    for state_dir in sorted(OPS_TASKS.iterdir()):
        if not state_dir.is_dir():
            continue
        for task_file in sorted(state_dir.glob("*.yaml")):
            data = load_yaml(task_file) or {}
            rel = task_file.relative_to(REPO_ROOT).as_posix()
            for err in validate_instance("task", data):
                problems.append(f"{rel}: {err}")
            # state-dir / state-field coherence
            if data.get("state") != state_dir.name and state_dir.name != "archive":
                problems.append(
                    f"{rel}: state field '{data.get('state')}' does not match directory '{state_dir.name}'"
                )
    return problems


def _validate_fixtures() -> list[Problem]:
    """Sanity-check qc/fixtures/{valid,invalid}/<schema>/*.(yaml|json)."""
    problems: list[Problem] = []
    valid_dir = QC_FIXTURES / "valid"
    invalid_dir = QC_FIXTURES / "invalid"
    if valid_dir.exists():
        for schema_dir in sorted(p for p in valid_dir.iterdir() if p.is_dir()):
            schema = schema_dir.name
            for f in sorted(schema_dir.glob("*.yaml")):
                data = load_yaml(f) or {}
                rel = f.relative_to(REPO_ROOT).as_posix()
                for err in validate_instance(schema, data):
                    problems.append(f"{rel}: expected valid but {err}")
    if invalid_dir.exists():
        for schema_dir in sorted(p for p in invalid_dir.iterdir() if p.is_dir()):
            schema = schema_dir.name
            for f in sorted(schema_dir.glob("*.yaml")):
                data = load_yaml(f) or {}
                rel = f.relative_to(REPO_ROOT).as_posix()
                errs = validate_instance(schema, data)
                if not errs:
                    problems.append(f"{rel}: expected invalid but schema accepted it")
    return problems


def validate_path(path: str = ".") -> tuple[bool, list[Problem]]:
    """Validate the entire repo (currently ignores `path`; full-sweep is cheap)."""
    index = load_index()
    problems: list[Problem] = []
    problems.extend(_validate_systems(index))
    problems.extend(_validate_metrics(index))
    problems.extend(_validate_sources())
    problems.extend(_validate_observations())
    problems.extend(_validate_tasks())
    problems.extend(_validate_fixtures())
    return (len(problems) == 0, problems)


def _iter_yaml_taxonomy() -> list[Path]:
    if not TAXONOMY_SRC.exists():
        return []
    return sorted(TAXONOMY_SRC.glob("*.yaml"))
