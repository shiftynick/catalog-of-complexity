"""Schema validity + fixture sanity tests."""

from __future__ import annotations

import pytest
from jsonschema import Draft202012Validator

from coc.paths import QC_FIXTURES
from coc.schemas import SCHEMA_NAMES, load_schema, validate_instance
from coc.yamlio import load_yaml


@pytest.mark.parametrize("name", SCHEMA_NAMES)
def test_schema_is_valid_draft_2020_12(name):
    schema = load_schema(name)
    # Raises SchemaError if invalid.
    Draft202012Validator.check_schema(schema)
    assert schema.get("$id", "").startswith("https://catalog-of-complexity.org/schemas/")


def _collect_fixtures(subdir: str):
    root = QC_FIXTURES / subdir
    if not root.exists():
        return []
    cases = []
    for schema_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for f in sorted(schema_dir.glob("*.yaml")):
            cases.append((schema_dir.name, f))
    return cases


@pytest.mark.parametrize(
    "schema_name,fixture_path",
    _collect_fixtures("valid"),
    ids=lambda x: str(x) if not hasattr(x, "name") else x.name,
)
def test_valid_fixtures_pass(schema_name, fixture_path):
    data = load_yaml(fixture_path)
    errors = validate_instance(schema_name, data)
    assert not errors, f"valid fixture unexpectedly failed: {errors}"


@pytest.mark.parametrize(
    "schema_name,fixture_path",
    _collect_fixtures("invalid"),
    ids=lambda x: str(x) if not hasattr(x, "name") else x.name,
)
def test_invalid_fixtures_fail(schema_name, fixture_path):
    data = load_yaml(fixture_path)
    errors = validate_instance(schema_name, data)
    assert errors, f"invalid fixture unexpectedly passed: {fixture_path}"
