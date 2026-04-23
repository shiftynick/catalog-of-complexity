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
@click.option(
    "--unblock-on-taxonomy",
    default=None,
    help="Set unblock condition: qualified slug (e.g. `system-class:atomic-system`). Auto-unblocks when the slug is added to taxonomy/source/. Only meaningful with --state blocked.",
)
@click.option(
    "--unblock-on-task",
    default=None,
    help="Set unblock condition: `tsk-YYYYMMDD-NNNNNN`. Auto-unblocks when that task reaches done/. Only meaningful with --state blocked.",
)
def complete(
    task_id: str,
    outputs: str,
    state: str,
    unblock_on_taxonomy: str | None,
    unblock_on_task: str | None,
) -> None:
    """Validate outputs, append event, and move task to its terminal state.

    When --state blocked, optionally record an unblock condition so the task
    moves back to ready/ automatically on the next `coc advance` once the
    condition is satisfied.
    """
    from coc.queue import complete_task
    from coc.yamlio import dump_yaml, load_yaml

    if unblock_on_taxonomy and unblock_on_task:
        raise click.UsageError(
            "--unblock-on-taxonomy and --unblock-on-task are mutually exclusive"
        )
    if (unblock_on_taxonomy or unblock_on_task) and state != "blocked":
        raise click.UsageError(
            "--unblock-on-* only applies with --state blocked"
        )
    if unblock_on_taxonomy or unblock_on_task:
        # Write unblock spec onto the leased task before the terminal move.
        # complete_task preserves arbitrary top-level fields on rename.
        from coc.paths import OPS_TASKS

        leased = OPS_TASKS / "leased" / f"{task_id}.yaml"
        running = OPS_TASKS / "running" / f"{task_id}.yaml"
        src_path = leased if leased.exists() else running
        if not src_path.exists():
            raise click.UsageError(f"task not leased/running: {task_id}")
        data = load_yaml(src_path)
        if unblock_on_taxonomy:
            data["unblock"] = {
                "kind": "taxonomy-slug-exists",
                "taxonomy_ref": unblock_on_taxonomy,
            }
        else:
            data["unblock"] = {
                "kind": "task-complete",
                "task_id": unblock_on_task,
            }
        dump_yaml(data, src_path)
    complete_task(task_id, outputs_json=outputs, terminal_state=state)
    console.print(f"[green]{state}[/green] {task_id}")


@main.command("next")
@click.option("--lane", default=None, help="Filter by lane (or task type).")
def next_cmd(lane: str | None) -> None:
    """Print the ID of the highest-priority ready task (exit 1 if queue empty)."""
    from coc.queue import next_ready_task

    tid = next_ready_task(lane=lane)
    if tid is None:
        raise SystemExit(1)
    console.print(tid)


@main.command()
def requeue() -> None:
    """Requeue tasks whose leases have expired."""
    from coc.queue import requeue_stale

    moved = requeue_stale()
    console.print(f"[green]requeued[/green] {moved} task(s)")


@main.command()
def advance() -> None:
    """Sweep blocked/ (unblock satisfied conditions), then auto-promote inbox/ → ready/."""
    from coc.queue import advance_queue, sweep_blocked

    unblocked = sweep_blocked()
    for tid in unblocked:
        console.print(f"[green]unblocked[/green] {tid}")
    promoted = advance_queue()
    for tid in promoted:
        console.print(f"[green]promoted[/green] {tid}")
    if not unblocked and not promoted:
        console.print("[dim]no auto-eligible tasks[/dim]")


@main.command()
@click.argument("task_id", required=False)
def unblock(task_id: str | None) -> None:
    """Move a blocked task back to ready/. With no arg, sweep all satisfied conditions."""
    from coc.queue import sweep_blocked, unblock_task

    if task_id:
        unblock_task(task_id)
        console.print(f"[green]unblocked[/green] {task_id}")
        return
    unblocked = sweep_blocked()
    for tid in unblocked:
        console.print(f"[green]unblocked[/green] {tid}")
    if not unblocked:
        console.print("[dim]no satisfied unblock conditions[/dim]")


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


@main.command()
@click.argument("ref")
def acquire(ref: str) -> None:
    """Resolve a prefixed ref (doi:/arxiv:/url:) and register it under registry/sources/."""
    from coc.sources import ResolutionError
    from coc.sources import acquire as _acquire

    try:
        path = _acquire(ref)
    except ResolutionError as exc:
        console.print(f"[red]FAIL[/red] {exc}")
        raise SystemExit(1) from exc
    console.print(f"[green]acquired[/green] {path}")


@main.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
@click.option(
    "--mode",
    type=click.Choice(["internal", "public"]),
    default="internal",
    show_default=True,
    help="internal mounts /ops; public exposes only /data and /taxonomy.",
)
@click.option("--reload/--no-reload", default=False, help="Autoreload on code changes (dev).")
def serve(host: str, port: int, mode: str, reload: bool) -> None:
    """Run the web UI (requires `coc[web]` extra)."""
    import os

    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            "coc[web] is not installed. Install with:\n"
            "  uv pip install -e '.[web]'"
        ) from exc

    os.environ["COC_WEB_MODE"] = mode
    console.print(
        f"[green]coc serve[/green] mode=[bold]{mode}[/bold] on http://{host}:{port}"
    )
    uvicorn.run(
        "coc.web.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
