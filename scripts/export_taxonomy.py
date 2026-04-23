"""Thin CLI wrapper: `python scripts/export_taxonomy.py`."""

from __future__ import annotations

from coc.taxonomy import export_all


def main() -> None:
    paths = export_all()
    for p in paths:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
