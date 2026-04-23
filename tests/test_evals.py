"""Smoke test for the eval runner."""

from __future__ import annotations

from coc.evals import check_goldens, run_evals


def test_evals_clean_on_seeds():
    ok, problems = run_evals()
    assert ok, problems


def test_every_active_skill_has_a_passing_golden():
    ok, problems = check_goldens()
    assert ok, problems
