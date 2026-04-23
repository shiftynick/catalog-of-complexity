"""`python scripts/requeue_stale_tasks.py` — janitor for expired leases."""

from __future__ import annotations

from coc.queue import requeue_stale


def main() -> None:
    n = requeue_stale()
    print(f"requeued {n} task(s)")


if __name__ == "__main__":
    main()
