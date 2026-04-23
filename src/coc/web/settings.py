"""Runtime settings for the web UI, driven by env vars with safe defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from coc.paths import WH_DUCKDB

Mode = Literal["internal", "public"]


@dataclass(frozen=True)
class Settings:
    mode: Mode
    duckdb_path: Path
    title: str

    @property
    def is_public(self) -> bool:
        return self.mode == "public"


def load_settings() -> Settings:
    mode_raw = os.environ.get("COC_WEB_MODE", "internal").strip().lower()
    mode: Mode = "public" if mode_raw == "public" else "internal"
    db_env = os.environ.get("COC_DUCKDB_PATH")
    db_path = Path(db_env) if db_env else (WH_DUCKDB / "coc.duckdb")
    title = os.environ.get("COC_WEB_TITLE", "Catalog of Complexity")
    return Settings(mode=mode, duckdb_path=db_path, title=title)
