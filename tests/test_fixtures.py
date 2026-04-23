"""Schema fixtures — valid examples pass, invalid examples fail."""

from __future__ import annotations

import json

import pytest

from coc.paths import QC_FIXTURES
from coc.schemas import validate_instance
from coc.yamlio import load_yaml

VALID_DIR = QC_FIXTURES / "valid"
INVALID_DIR = QC_FIXTURES / "invalid"


def _load(path):
    if path.suffix == ".jsonl":
        first = path.read_text(encoding="utf-8").splitlines()[0]
        return json.loads(first)
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return load_yaml(path)


def _schema_for(filename: str) -> str:
    return filename.split(".")[0]


@pytest.mark.parametrize("path", sorted(VALID_DIR.glob("*.*")))
def test_valid_fixtures_validate(path):
    schema = _schema_for(path.name)
    errors = validate_instance(schema, _load(path))
    assert not errors, f"{path.name}: {errors}"


@pytest.mark.parametrize("path", sorted(INVALID_DIR.glob("*.*")))
def test_invalid_fixtures_fail(path):
    schema = _schema_for(path.name)
    errors = validate_instance(schema, _load(path))
    assert errors, f"{path.name} was expected to fail but passed"
