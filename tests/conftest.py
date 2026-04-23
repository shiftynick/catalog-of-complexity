"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from coc.paths import REPO_ROOT


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT
