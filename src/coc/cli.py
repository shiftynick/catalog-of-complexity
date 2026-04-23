"""Click-based CLI entrypoint for the `coc` command."""

from __future__ import annotations

import click
from rich.console import Console

from coc import __version__

console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="coc")
def main() -> None:
    """Catalog of Complexity CLI."""


@main.command()
@click.argument("path", required=False, default=".")
def validate(path: str) -> None:
    """Validate registry records + taxonomies against schemas."""
    from coc.validate import validate_path

    ok, problems = validate_path(path)
    if ok:
        console.print(f"[green]OK[/green] — {path} validates.")
        return
    for p in problems:
        console.print(f"[red]FAIL[/red] {p}")
    raise SystemExit(1)


@main.command()
@click.argument("task_id")
def lease(task_id: str) -> None:
    """Atomically move a task from ready/ to leased/."""
    from coc.queue import lease_task

    lease_task(task_id)
    console.print(f"[green]leased[/green] {task_id}")


@main.command()
@click.argument("task_id")
def heartbeat(task_id: str) -> None:
    """Update lease liveness timestamp for a leased task."""
    from coc.queue import heartbeat_task

    heartbeat_task(task_id)
    console.print(f"[green]heartbeat[/green] {task_id}")


@main.command()
@click.argument("task_id")
@click.option("--outputs", default="{}", help="JSON describing declared outputs.")
@click.option("--state", default="done", type=click.Choice(["review", "done", "blocked", "failed"]))
def complete(task_id: str, outputs: str, state: str) -> None:
    """Validate outputs, append event, and move task to its terminal state."""
    from coc.queue import complete_task

    complete_task(task_id, outputs_json=outputs, terminal_state=state)
    console.print(f"[green]{state}[/green] {task_id}")


@main.command()
def requeue() -> None:
    """Requeue tasks whose leases have expired."""
    from coc.queue import requeue_stale

    moved = requeue_stale()
    console.print(f"[green]requeued[/green] {moved} task(s)")


@main.command()
def materialize() -> None:
    """Rebuild Parquet + DuckDB warehouse from the canonical registry."""
    from coc.warehouse import materialize as _mat

    counts = _mat()
    for table, n in counts.items():
        console.print(f"  {table}: {n} rows")
    console.print("[green]materialized[/green]")


@main.command()
@click.option("--date", default=None, help="Snapshot date (YYYY-MM-DD). Defaults to today UTC.")
def release(date: str | None) -> None:
    """Build a releases/snapshot-* directory with Data Package + RO-Crate."""
    from coc.release import build_release

    path = build_release(snapshot_date=date)
    console.print(f"[green]release[/green] {path}")


@main.command("export-taxonomy")
def export_taxonomy() -> None:
    """Emit SKOS Turtle + JSON labels for taxonomy/source/."""
    from coc.taxonomy import export_all

    paths = export_all()
    for p in paths:
        console.print(f"  wrote {p}")


@main.command()
@click.argument("skill", required=False)
def eval(skill: str | None) -> None:  # noqa: A001
    """Run QC evals / goldens."""
    from coc.evals import run

    ok = run(skill=skill)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
