"""JSON Schema loader + shared validator factory."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coc.paths import SCHEMAS

SCHEMA_NAMES = (
    "system",
    "metric",
    "source",
    "observation",
    "task",
    "run",
    "event",
)


@cache
def load_schema(name: str) -> dict[str, Any]:
    """Load and cache a schema by short name (e.g. "system")."""
    path = SCHEMAS / f"{name}.schema.json"
    if not path.exists():
        raise FileNotFoundError(f"Unknown schema: {name} (expected {path})")
    return json.loads(path.read_text(encoding="utf-8"))


@cache
def get_validator(name: str) -> Draft202012Validator:
    """Return a cached Draft 2020-12 validator for the named schema."""
    schema = load_schema(name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_instance(name: str, instance: Any) -> list[str]:
    """Return a list of human-readable errors (empty on success)."""
    v = get_validator(name)
    errors: list[str] = []
    for err in sorted(v.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    return errors


def all_schema_paths() -> list[Path]:
    return [SCHEMAS / f"{n}.schema.json" for n in SCHEMA_NAMES]
