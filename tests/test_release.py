"""Release snapshot build smoke test."""

from __future__ import annotations

import json

from coc.release import build_release


def test_release_produces_datapackage_and_crate(tmp_path, monkeypatch):
    from coc import release as release_module

    monkeypatch.setattr(release_module, "RELEASES", tmp_path)
    snapshot = build_release(snapshot_date="2099-01-01")

    assert snapshot.exists()
    assert (snapshot / "datapackage.json").exists()
    assert (snapshot / "ro-crate-metadata.json").exists()
    assert (snapshot / "manifest.md").exists()
    assert (snapshot / "data").is_dir()

    dp = json.loads((snapshot / "datapackage.json").read_text(encoding="utf-8"))
    assert dp["name"] == "snapshot-2099-01-01"
    assert dp["licenses"][0]["name"] == "CC-BY-4.0"
    assert len(dp["resources"]) >= 5
    for r in dp["resources"]:
        assert r["hash"].startswith("sha256:")

    crate = json.loads((snapshot / "ro-crate-metadata.json").read_text(encoding="utf-8"))
    assert "@graph" in crate
    assert any(e.get("@type") == "Dataset" for e in crate["@graph"])
