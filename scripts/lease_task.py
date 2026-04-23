"""`python scripts/lease_task.py <task-id>` — atomically claim a task."""

from __future__ import annotations

import sys

from coc.queue import lease_task


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: lease_task.py <task-id>", file=sys.stderr)
        raise SystemExit(2)
    path = lease_task(sys.argv[1])
    print(f"leased {sys.argv[1]} -> {path}")


if __name__ == "__main__":
    main()
