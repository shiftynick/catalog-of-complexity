"""End-to-end warehouse materialization test on the seeded registry."""

from __future__ import annotations

from coc.warehouse import materialize, query


def test_materialize_produces_expected_tables():
    counts = materialize()
    assert counts["systems"] >= 1
    assert counts["metrics"] >= 1
    assert counts["sources"] >= 1
    assert counts["observations"] >= 1
    assert counts["evidence"] >= 1
    assert "applicability" in counts
    assert "edges" in counts


def test_duckdb_views_are_queryable():
    materialize()
    rows = query("SELECT systems_total, metrics_total, observations_total FROM v_coverage_summary")
    assert len(rows) == 1
    systems, metrics, obs = rows[0]
    assert systems >= 1
    assert metrics >= 1
    assert obs >= 1


def test_system_metric_matrix_returns_value():
    materialize()
    rows = query(
        """
        SELECT value_numeric
        FROM v_system_metric_matrix
        WHERE system_id = 'sys-000001--amazon-rainforest'
          AND metric_id = 'mtr-000001--network-modularity'
        """
    )
    assert rows
    assert abs(rows[0][0] - 0.41) < 1e-9
