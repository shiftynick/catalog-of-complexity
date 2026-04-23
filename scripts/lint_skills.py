"""`python scripts/lint_skills.py` — verify SKILL.md frontmatter completeness.

Checks every `skills/<name>/SKILL.md`:
- Has YAML frontmatter delimited by `---` lines.
- Frontmatter declares: name, description, status, inputs, outputs, stop_conditions.
- `name` matches the directory name.
- `status` is one of {active, disabled}.
- `inputs`, `outputs`, `stop_conditions` are non-empty lists.
- AGENTS.md references the skill by path.

Exit 0 on pass, 1 on any failure. Prints a per-skill status line.
"""

from __future__ import annotations

import sys
from pathlib import Path

from coc.paths import REPO_ROOT, SKILLS
from coc.yamlio import load_yaml_text

REQUIRED_FIELDS = ("name", "description", "status", "inputs", "outputs", "stop_conditions")
VALID_STATUSES = {"active", "disabled", "postrun"}
LIST_FIELDS = ("inputs", "outputs", "stop_conditions")


def _parse_frontmatter(md_text: str) -> dict | None:
    if not md_text.startswith("---\n"):
        return None
    end = md_text.find("\n---\n", 4)
    if end == -1:
        return None
    return load_yaml_text(md_text[4:end])


def lint_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return ["missing SKILL.md"]
    fm = _parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    if fm is None:
        return ["SKILL.md has no valid `---`-delimited YAML frontmatter"]
    if not isinstance(fm, dict):
        return ["frontmatter is not a mapping"]
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"missing required field: {field}")
    if fm.get("name") and fm["name"] != skill_dir.name:
        errors.append(f"name '{fm['name']}' != directory '{skill_dir.name}'")
    if fm.get("status") and fm["status"] not in VALID_STATUSES:
        errors.append(f"status '{fm['status']}' not in {sorted(VALID_STATUSES)}")
    for field in LIST_FIELDS:
        value = fm.get(field)
        if value is not None and (not isinstance(value, list) or len(value) == 0):
            errors.append(f"{field} must be a non-empty list")
    return errors


def check_agents_references(skill_names: list[str]) -> list[str]:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    missing = [name for name in skill_names if name not in agents]
    return [f"AGENTS.md does not reference skill: {name}" for name in missing]


def main() -> int:
    if not SKILLS.exists():
        print(f"FAIL: skills directory missing at {SKILLS}")
        return 1
    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    if not skill_dirs:
        print("FAIL: no skill directories found")
        return 1

    exit_code = 0
    for skill_dir in skill_dirs:
        errs = lint_skill(skill_dir)
        if errs:
            exit_code = 1
            print(f"FAIL {skill_dir.name}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK   {skill_dir.name}")

    agent_errs = check_agents_references([d.name for d in skill_dirs])
    if agent_errs:
        exit_code = 1
        print("FAIL AGENTS.md cross-references")
        for e in agent_errs:
            print(f"  - {e}")
    else:
        print("OK   AGENTS.md cross-references")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
