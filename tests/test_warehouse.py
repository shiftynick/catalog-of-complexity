"""End-to-end warehouse materialization test on the live registry.

Updated for the v0.2 bootstrap: the registry holds catalog-bootstrap
systems and metrics but **zero observations** until the metrics-fill
phase produces them. These tests therefore exercise the materializer's
empty-observations path (which the v0.1 tests did not).
"""

from __future__ import annotations

import json
import textwrap
import uuid

from coc.paths import REG_OBSERVATIONS
from coc.warehouse import materialize, query


def test_materialize_produces_expected_tables():
    """Materialize against the live registry — observations may be zero."""
    counts = materialize()
    assert counts["systems"] >= 1
    assert counts["metrics"] >= 1
    assert counts["sources"] >= 1
    # observations may legitimately be zero immediately after bootstrap
    assert counts["observations"] >= 0
    assert counts["evidence"] >= 0
    assert "applicability" in counts
    assert "edges" in counts


def test_duckdb_views_are_queryable():
    """v_coverage_summary should run even when observations is empty."""
    materialize()
    rows = query("SELECT systems_total, metrics_total, observations_total FROM v_coverage_summary")
    assert len(rows) == 1
    systems, metrics, obs = rows[0]
    assert systems >= 1
    assert metrics >= 1
    assert obs >= 0


def test_system_metric_matrix_with_injected_observation(tmp_path, monkeypatch):
    """Inject a synthetic observation into a temporary registry, then verify
    v_system_metric_matrix surfaces it. Uses a real system+metric id from the
    bootstrap registry so taxonomy refs resolve."""
    # Pick the first (system, metric) pair from the live registry to avoid
    # hardcoding a specific bootstrap slug that might be renumbered.
    rows = query("SELECT id FROM systems ORDER BY id LIMIT 1")
    assert rows, "live registry has no systems"
    sys_id = rows[0][0]
    rows = query("SELECT id FROM metrics ORDER BY id LIMIT 1")
    assert rows, "live registry has no metrics"
    mtr_id = rows[0][0]

    # Inject an observation directly into the registry. Stash a marker so we
    # know which file to remove afterward; the registry path is shared with
    # the live repo, so cleanup matters.
    obs_id = "obs-" + uuid.uuid4().hex[:8]
    src_id = "src-000001--example-review"  # preserved from pre-bootstrap registry
    evi_id = "evi-" + uuid.uuid4().hex[:8]
    obs_dir = REG_OBSERVATIONS / sys_id
    obs_dir.mkdir(parents=True, exist_ok=True)
    obs_file = obs_dir / "_test_synthetic.jsonl"
    record = {
        "observation_id": obs_id,
        "system_id": sys_id,
        "metric_id": mtr_id,
        "value": 0.41,
        "unit": "unitless",
        "value_kind": "derived",
        "confidence": 0.5,
        "source_refs": [src_id],
        "evidence_refs": [evi_id],
        "review_state": "auto-validated",
    }
    obs_file.write_text(json.dumps(record) + "\n", encoding="utf-8")
    try:
        materialize()
        rows = query(
            textwrap.dedent(
                f"""
                SELECT value_numeric
                FROM v_system_metric_matrix
                WHERE system_id = '{sys_id}'
                  AND metric_id = '{mtr_id}'
                """
            )
        )
        assert rows
        assert abs(rows[0][0] - 0.41) < 1e-9
    finally:
        obs_file.unlink(missing_ok=True)
        # leave the system's observation directory in place (other observations
        # may live there; cleanup removed in v0.2 wipe but the dir itself
        # is recreated above and is benign).
