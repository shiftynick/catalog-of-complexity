"""Thin YAML I/O helpers using ruamel.yaml for round-trip fidelity.

Timestamps parsed by YAML are normalized to ISO-8601 strings on load so they
round-trip through JSON Schema `format: date-time` validation without a
custom format checker. Our canonical records treat timestamps as strings.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

_yaml = YAML(typ="safe")
_yaml.default_flow_style = False
_yaml.indent(mapping=2, sequence=4, offset=2)


def _iso(obj: Any) -> Any:
    if isinstance(obj, datetime):
        s = obj.isoformat()
        return s.replace("+00:00", "Z") if obj.tzinfo is not None else s
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _iso(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_iso(v) for v in obj]
    return obj


def load_yaml(path: Path | str) -> Any:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return _iso(_yaml.load(f))


def load_yaml_text(text: str) -> Any:
    return _iso(_yaml.load(text))


def dump_yaml(data: Any, path: Path | str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        _yaml.dump(data, f)
