"""`python scripts/build_release.py [YYYY-MM-DD]` — build a release snapshot."""

from __future__ import annotations

import sys

from coc.release import build_release


def main() -> int:
    snapshot_date = sys.argv[1] if len(sys.argv) > 1 else None
    path = build_release(snapshot_date=snapshot_date)
    print(f"release: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
