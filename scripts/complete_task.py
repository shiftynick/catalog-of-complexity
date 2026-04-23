"""`python scripts/complete_task.py <task-id> [--state done] [--outputs '{}']`."""

from __future__ import annotations

import argparse

from coc.queue import complete_task


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("task_id")
    p.add_argument("--state", default="done", choices=("review", "done", "blocked", "failed"))
    p.add_argument("--outputs", default="{}")
    args = p.parse_args()
    path = complete_task(args.task_id, outputs_json=args.outputs, terminal_state=args.state)
    print(f"{args.state} {args.task_id} -> {path}")


if __name__ == "__main__":
    main()
