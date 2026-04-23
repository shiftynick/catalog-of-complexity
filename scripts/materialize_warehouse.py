"""`python scripts/materialize_warehouse.py` — rebuild Parquet + DuckDB."""

from __future__ import annotations

from coc.warehouse import materialize


def main() -> None:
    counts = materialize()
    for table, n in counts.items():
        print(f"  {table}: {n}")


if __name__ == "__main__":
    main()
