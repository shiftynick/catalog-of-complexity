"""Build a release snapshot under `releases/snapshot-YYYY-MM-DD/`.

A snapshot bundles the current warehouse Parquet files with:
- `datapackage.json` — Frictionless Data Package descriptor (CC-BY-4.0 data).
- `ro-crate-metadata.json` — RO-Crate metadata (written by the `rocrate`
  library; the library canonicalizes the filename, so we do not rename to
  `.jsonld`).
- `manifest.md` — human-readable index with row counts and SHA-256 per file.
- `data/*.parquet` — copies of the current warehouse tables.

The warehouse is re-materialized before packaging so the snapshot always
reflects the latest registry state — we never ship stale Parquet.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pyarrow.parquet as pq
from rocrate.rocrate import ROCrate

from coc.paths import RELEASES, WH_PARQUET
from coc.warehouse import materialize

DATA_LICENSE = {"name": "CC-BY-4.0", "title": "Creative Commons Attribution 4.0"}


def _today_utc() -> str:
    return date.today().isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _parquet_row_count(path: Path) -> int:
    return pq.read_metadata(str(path)).num_rows


def _build_datapackage(snapshot: Path, data_dir: Path, snapshot_name: str) -> Path:
    resources = []
    for parquet in sorted(data_dir.glob("*.parquet")):
        resources.append(
            {
                "name": parquet.stem,
                "path": f"data/{parquet.name}",
                "format": "parquet",
                "mediatype": "application/vnd.apache.parquet",
                "hash": f"sha256:{_sha256(parquet)}",
            }
        )
    descriptor = {
        "name": snapshot_name,
        "title": f"Catalog of Complexity — {snapshot_name}",
        "description": (
            "Release snapshot of the Catalog of Complexity registry, materialized "
            "to Parquet. Regenerable from the registry at the commit referenced "
            "in manifest.md."
        ),
        "licenses": [DATA_LICENSE],
        "created": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "resources": resources,
    }
    dp_path = snapshot / "datapackage.json"
    dp_path.write_text(json.dumps(descriptor, indent=2), encoding="utf-8")
    return dp_path


def _build_ro_crate(snapshot: Path, data_dir: Path, snapshot_name: str) -> Path:
    crate = ROCrate()
    crate.name = snapshot_name
    crate.description = (
        "Catalog of Complexity snapshot. Bundles Parquet tables for systems, metrics, "
        "sources, observations, evidence, applicability, and edges."
    )
    # Add the datapackage descriptor as a supplementary file
    crate.add_file(str(snapshot / "datapackage.json"), dest_path="datapackage.json")
    for parquet in sorted(data_dir.glob("*.parquet")):
        crate.add_file(
            str(parquet),
            dest_path=f"data/{parquet.name}",
            properties={"encodingFormat": "application/vnd.apache.parquet"},
        )
    crate.write(str(snapshot))
    return snapshot / "ro-crate-metadata.json"


def _build_manifest(snapshot: Path, data_dir: Path, snapshot_name: str) -> Path:
    lines: list[str] = [
        f"# {snapshot_name}",
        "",
        "Release snapshot of the Catalog of Complexity warehouse.",
        "",
        f"- Built: {datetime.now(UTC).isoformat(timespec='seconds').replace('+00:00', 'Z')}",
        "- License (data): CC-BY-4.0",
        "- Regenerable: yes, from the registry at the matching git commit.",
        "",
        "## Data files",
        "",
        "| Table | Rows | SHA-256 |",
        "|-------|------|---------|",
    ]
    for parquet in sorted(data_dir.glob("*.parquet")):
        lines.append(f"| {parquet.stem} | {_parquet_row_count(parquet)} | `{_sha256(parquet)}` |")
    lines.append("")
    lines.append("See `datapackage.json` for the Frictionless descriptor and")
    lines.append("`ro-crate-metadata.json` for the RO-Crate metadata.")
    manifest = snapshot / "manifest.md"
    manifest.write_text("\n".join(lines), encoding="utf-8")
    return manifest


def build_release(snapshot_date: str | None = None) -> Path:
    """Build a release snapshot and return the snapshot directory."""
    materialize()  # always ship the latest warehouse
    snapshot_date = snapshot_date or _today_utc()
    snapshot_name = f"snapshot-{snapshot_date}"
    snapshot = RELEASES / snapshot_name
    if snapshot.exists():
        shutil.rmtree(snapshot)
    data_dir = snapshot / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for parquet in sorted(WH_PARQUET.glob("*.parquet")):
        shutil.copy2(parquet, data_dir / parquet.name)
    _build_datapackage(snapshot, data_dir, snapshot_name)
    _build_ro_crate(snapshot, data_dir, snapshot_name)
    _build_manifest(snapshot, data_dir, snapshot_name)
    return snapshot
