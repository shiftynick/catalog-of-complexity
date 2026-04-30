"""Tests for `coc.worklist` — pure ordering logic against synthetic
SystemSubject / MetricSubject inputs, plus a smoke test against the
live registry."""

from __future__ import annotations

import pytest

from coc.worklist import (
    MetricSubject,
    SystemSubject,
    metric_worklist_for_definition,
    next_worklist_items,
    phase_worklist_size,
    system_worklist_for_matrix_fill,
    system_worklist_for_profiling,
)


def _sys(slug: str, status: str, priority: str | None, domain: str, has_obs: bool = False) -> SystemSubject:
    return SystemSubject(
        id=f"sys-000001--{slug}",
        slug=slug,
        status=status,
        priority=priority,
        domain=domain,
        has_observations=has_obs,
    )


def _mtr(slug: str, status: str, family: str, ml: str | None) -> MetricSubject:
    return MetricSubject(
        id=f"mtr-000001--{slug}",
        slug=slug,
        status=status,
        family=family,
        maturity_level=ml,
    )


# ---------- system-profiling ordering ----------


def test_profiling_filters_to_bootstrap_stub_only(monkeypatch):
    """Only systems with status: bootstrap-stub appear in the worklist."""
    sample = [
        _sys("a", "bootstrap-stub", "P0", "physical"),
        _sys("b", "candidate", "P0", "physical"),  # already upgraded; skip
        _sys("c", "profiled", "P0", "physical"),  # already validated; skip
        _sys("d", "deprecated", "P0", "physical"),  # skip
        _sys("e", "bootstrap-stub", "P1", "physical"),
    ]
    wl = system_worklist_for_profiling(sample)
    assert {s.slug for s in wl} == {"a", "e"}


def test_profiling_priority_p0_first():
    sample = [
        _sys("p1a", "bootstrap-stub", "P1", "physical"),
        _sys("p0a", "bootstrap-stub", "P0", "physical"),
        _sys("p2a", "bootstrap-stub", "P2", "physical"),
        _sys("p0b", "bootstrap-stub", "P0", "physical"),
    ]
    wl = system_worklist_for_profiling(sample)
    # All P0 must come before any P1, all P1 before P2.
    priorities = [s.priority for s in wl]
    p0_count = priorities.count("P0")
    assert priorities[:p0_count] == ["P0"] * p0_count
    assert priorities[p0_count:] == ["P1", "P2"]


def test_profiling_domain_interleave_within_priority(tmp_path, monkeypatch):
    """Within one priority bucket, items round-robin across domains in
    the order declared by taxonomy/source/system-domains.yaml. We mock
    the domain order to keep the test independent of taxonomy edits."""
    monkeypatch.setattr("coc.worklist._domain_order", lambda: ["physical", "biological", "social"])
    sample = [
        _sys("phys-a", "bootstrap-stub", "P0", "physical"),
        _sys("phys-b", "bootstrap-stub", "P0", "physical"),
        _sys("bio-a", "bootstrap-stub", "P0", "biological"),
        _sys("bio-b", "bootstrap-stub", "P0", "biological"),
        _sys("soc-a", "bootstrap-stub", "P0", "social"),
    ]
    wl = system_worklist_for_profiling(sample)
    # Round-robin: physical, biological, social, physical, biological
    domains_in_order = [s.domain for s in wl]
    assert domains_in_order == ["physical", "biological", "social", "physical", "biological"]


def test_profiling_unset_priority_goes_last():
    sample = [
        _sys("noprio", "bootstrap-stub", None, "physical"),
        _sys("p0", "bootstrap-stub", "P0", "physical"),
        _sys("c-case", "bootstrap-stub", "C", "physical"),
    ]
    wl = system_worklist_for_profiling(sample)
    assert [s.priority for s in wl] == ["P0", "C", None]


def test_profiling_unknown_domain_appended_at_tail(monkeypatch):
    """Items with a domain not in the canonical order go after the
    interleaved items."""
    monkeypatch.setattr("coc.worklist._domain_order", lambda: ["physical", "biological"])
    sample = [
        _sys("a", "bootstrap-stub", "P0", "physical"),
        _sys("b", "bootstrap-stub", "P0", "biological"),
        _sys("weird", "bootstrap-stub", "P0", "made-up-domain"),
    ]
    wl = system_worklist_for_profiling(sample)
    assert [s.slug for s in wl] == ["a", "b", "weird"]


# ---------- matrix-fill ordering ----------


def test_matrix_fill_filters_to_candidate_or_profiled():
    sample = [
        _sys("stub", "bootstrap-stub", "P0", "physical"),  # not eligible
        _sys("cand", "candidate", "P0", "physical"),
        _sys("prof", "profiled", "P0", "physical"),
        _sys("dep", "deprecated", "P0", "physical"),
    ]
    wl = system_worklist_for_matrix_fill(sample)
    assert {s.slug for s in wl} == {"cand", "prof"}


def test_matrix_fill_skips_systems_with_observations():
    sample = [
        _sys("filled", "candidate", "P0", "physical", has_obs=True),
        _sys("empty", "candidate", "P0", "physical", has_obs=False),
    ]
    wl = system_worklist_for_matrix_fill(sample)
    assert {s.slug for s in wl} == {"empty"}


# ---------- metric-definition ordering ----------


def test_metric_definition_filters_to_bootstrap_stub_only():
    sample = [
        _mtr("a", "bootstrap-stub", "topology", "L2"),
        _mtr("b", "proposed", "topology", "L2"),  # skip
        _mtr("c", "canonical", "topology", "L2"),  # skip
    ]
    wl = metric_worklist_for_definition(sample)
    assert {m.slug for m in wl} == {"a"}


def test_metric_definition_l2_before_l1_before_l0():
    sample = [
        _mtr("l0", "bootstrap-stub", "topology", "L0"),
        _mtr("l2", "bootstrap-stub", "topology", "L2"),
        _mtr("l1", "bootstrap-stub", "topology", "L1"),
        _mtr("l3", "bootstrap-stub", "topology", "L3"),
    ]
    wl = metric_worklist_for_definition(sample)
    assert [m.slug for m in wl] == ["l2", "l1", "l0", "l3"]


def test_metric_definition_within_maturity_sort_by_family_then_slug():
    sample = [
        _mtr("zeta", "bootstrap-stub", "topology", "L2"),
        _mtr("alpha", "bootstrap-stub", "dynamics", "L2"),
        _mtr("beta", "bootstrap-stub", "topology", "L2"),
    ]
    wl = metric_worklist_for_definition(sample)
    assert [m.slug for m in wl] == ["alpha", "beta", "zeta"]


# ---------- next_worklist_items dispatcher ----------


def test_next_worklist_unknown_phase_returns_empty():
    assert next_worklist_items("nonsense", 5) == []


# ---------- live-registry smoke test ----------


def test_phase_worklist_size_against_live_registry():
    """Smoke test: the resolver runs against the actual repo state
    without crashing, and the numbers are plausible for the v0.2
    bootstrap state."""
    profiling_size = phase_worklist_size("system-profiling")
    metric_size = phase_worklist_size("metric-definition")
    matrix_size = phase_worklist_size("matrix-fill")
    # All three should be non-negative integers
    assert profiling_size >= 0
    assert metric_size >= 0
    assert matrix_size >= 0
    # At least one of the three should have items in v0.2 state, otherwise
    # the registry is empty or already fully processed.
    assert (profiling_size + metric_size + matrix_size) > 0


def test_next_items_is_idempotent():
    """Calling twice with the same K returns the same ids — the
    resolver is pure."""
    a = next_worklist_items("system-profiling", 3)
    b = next_worklist_items("system-profiling", 3)
    assert a == b


@pytest.mark.parametrize("phase", ["system-profiling", "metric-definition", "matrix-fill"])
def test_next_items_respects_k(phase: str):
    """K=0 returns empty; K=large returns at most worklist size."""
    assert next_worklist_items(phase, 0) == []
    full = next_worklist_items(phase, 10_000)
    assert len(full) == phase_worklist_size(phase)
