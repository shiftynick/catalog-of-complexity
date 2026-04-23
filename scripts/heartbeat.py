"""`python scripts/heartbeat.py <task-id>` — refresh a lease."""

from __future__ import annotations

import sys

from coc.queue import heartbeat_task


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: heartbeat.py <task-id>", file=sys.stderr)
        raise SystemExit(2)
    heartbeat_task(sys.argv[1])
    print(f"heartbeat {sys.argv[1]}")


if __name__ == "__main__":
    main()
