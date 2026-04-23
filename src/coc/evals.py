"""QC evals + goldens runner.

Evals are YAML rules under `qc/evals/`. Each eval declares a `scope`
(currently just `observations`) and a list of `checks`, where each check
carries a Python `assertion` expression evaluated against a per-scope binding
(`obs` for observations). A few safe helpers are injected into the eval
namespace — the biggest being `resolve_evidence(ref)` which resolves an
`evi-*` id to its record in some source's `evidence.jsonl`.

Goldens live under `qc/goldens/<skill>/<scenario>/{input.yaml,expected.yaml}`.
For the bootstrap slice we verify structural health — every active skill has
at least one golden directory whose `input.yaml` validates against
`schemas/task.schema.json` and whose `expected.yaml` parses. Running the
goldens end-to-end through an LLM is out of scope here.

The runner prints a one-line status per eval and per skill-golden, and
returns True iff everything passes.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from rich.console import Console

from coc.paths import QC_EVALS, QC_GOLDENS, REG_OBSERVATIONS, REG_SOURCES, SKILLS
from coc.schemas import validate_instance
from coc.yamlio import load_yaml, load_yaml_text

console = Console()

ALLOWED_BUILTINS = {
    "len": len,
    "all": all,
    "any": any,
    "isinstance": isinstance,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
}


def _load_evidence_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    if not REG_SOURCES.exists():
        return index
    for evidence_file in REG_SOURCES.glob("*/evidence.jsonl"):
        for line in evidence_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            index[row["evidence_id"]] = row
    return index


def _iter_observations() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not REG_OBSERVATIONS.exists():
        return rows
    for jsonl in REG_OBSERVATIONS.glob("*/*.jsonl"):
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _load_evals() -> list[dict[str, Any]]:
    if not QC_EVALS.exists():
        return []
    return [load_yaml(p) for p in sorted(QC_EVALS.glob("*.yaml"))]


def _run_check(
    expression: str,
    obs: dict[str, Any],
    resolve_evidence: Callable[[str], dict[str, Any] | None],
) -> bool:
    globals_dict = {
        "__builtins__": ALLOWED_BUILTINS,
        "resolve_evidence": resolve_evidence,
        "obs": obs,
    }
    return bool(eval(expression, globals_dict))


def run_evals() -> tuple[bool, list[str]]:
    """Run every eval over the registry. Returns (ok, problems)."""
    problems: list[str] = []
    evidence_idx = _load_evidence_index()
    observations = _iter_observations()

    def resolve_evidence(ref: str) -> dict[str, Any] | None:
        return evidence_idx.get(ref)

    for eval_def in _load_evals():
        name = eval_def.get("name", "<unnamed>")
        scope = eval_def.get("scope")
        if scope != "observations":
            problems.append(f"{name}: unsupported scope {scope!r}")
            continue
        for check in eval_def.get("checks", []):
            cid = check.get("id", "<anon>")
            expr = check["assertion"]
            fails = 0
            for obs in observations:
                try:
                    if not _run_check(expr, obs, resolve_evidence):
                        fails += 1
                except Exception as exc:  # noqa: BLE001 — eval errors are reported per-check
                    problems.append(f"{name}/{cid}: error on {obs.get('observation_id')}: {exc}")
                    fails += 1
            if fails:
                problems.append(f"{name}/{cid}: {fails} observation(s) failed")
                console.print(f"[red]FAIL[/red] {name}/{cid}  ({fails} fail)")
            else:
                console.print(f"[green]OK[/green]   {name}/{cid}  ({len(observations)} checked)")
    return (not problems), problems


def _active_skills() -> list[str]:
    if not SKILLS.exists():
        return []
    names: list[str] = []
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        fm = _parse_frontmatter((d / "SKILL.md").read_text(encoding="utf-8"))
        if fm and fm.get("status") == "active":
            names.append(d.name)
    return names


def _parse_frontmatter(md_text: str) -> dict | None:
    if not md_text.startswith("---\n"):
        return None
    end = md_text.find("\n---\n", 4)
    if end == -1:
        return None
    return load_yaml_text(md_text[4:end])


def check_goldens(skill_filter: str | None = None) -> tuple[bool, list[str]]:
    """Verify each active skill has at least one structurally-valid golden."""
    problems: list[str] = []
    skills = _active_skills()
    if skill_filter:
        skills = [s for s in skills if s == skill_filter]
    for skill in skills:
        skill_dir = QC_GOLDENS / skill
        scenarios = (
            sorted(p for p in skill_dir.iterdir() if p.is_dir()) if skill_dir.exists() else []
        )
        if not scenarios:
            problems.append(f"{skill}: no goldens found under {skill_dir}")
            console.print(f"[red]FAIL[/red] goldens/{skill}: missing")
            continue
        passed = 0
        for scenario in scenarios:
            input_yaml = scenario / "input.yaml"
            expected_yaml = scenario / "expected.yaml"
            if not input_yaml.exists():
                problems.append(f"{skill}/{scenario.name}: missing input.yaml")
                continue
            if not expected_yaml.exists():
                problems.append(f"{skill}/{scenario.name}: missing expected.yaml")
                continue
            data = load_yaml(input_yaml)
            errs = validate_instance("task", data)
            if errs:
                problems.append(f"{skill}/{scenario.name}: input.yaml does not validate: {errs[0]}")
                continue
            exp = load_yaml(expected_yaml)
            if not isinstance(exp, dict) or "assertions" not in exp:
                problems.append(
                    f"{skill}/{scenario.name}: expected.yaml must be a mapping with `assertions`"
                )
                continue
            passed += 1
        if passed == 0:
            console.print(f"[red]FAIL[/red] goldens/{skill}: 0 scenarios pass structural check")
        else:
            console.print(
                f"[green]OK[/green]   goldens/{skill}: {passed}/{len(scenarios)} scenarios pass"
            )
    return (not problems), problems


def run(skill: str | None = None) -> bool:
    """Entrypoint used by `coc eval`. Returns True iff everything passes."""
    console.print("[bold]evals[/bold]")
    evals_ok, eval_problems = run_evals()
    console.print("[bold]goldens[/bold]")
    goldens_ok, golden_problems = check_goldens(skill_filter=skill)
    ok = evals_ok and goldens_ok
    if not ok:
        console.print("[red]eval run had failures[/red]")
        for p in eval_problems + golden_problems:
            console.print(f"  - {p}")
    else:
        console.print("[green]eval run clean[/green]")
    return ok
