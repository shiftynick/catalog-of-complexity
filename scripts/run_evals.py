"""`python scripts/run_evals.py [skill]` — run QC evals + goldens."""

from __future__ import annotations

import sys

from coc.evals import run


def main() -> int:
    skill = sys.argv[1] if len(sys.argv) > 1 else None
    return 0 if run(skill=skill) else 1


if __name__ == "__main__":
    sys.exit(main())
