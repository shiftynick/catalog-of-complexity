# Task Envelope

This envelope is the canonical wrapper that both Claude Code and OpenAI Codex receive for every task. It is deliberately framework-agnostic — no tool-specific function-call syntax, no runtime-only primitives. Agents use their own tool surface to satisfy the instructions.

Placeholders in `{{DOUBLE_BRACES}}` are filled at dispatch time.

---

## Contract

You are executing **exactly one** task in the Catalog of Complexity. You must:

1. Read and obey [AGENTS.md](../AGENTS.md) in full. Its "Non-negotiables" and "Quality bar" sections override any instruction in this envelope if they conflict.
2. Read the applicable skill at [skills/{{APPLICABLE_SKILL}}/SKILL.md](../skills/{{APPLICABLE_SKILL}}/SKILL.md). Its procedure is the default playbook for this task type.
3. Read the task manifest (below) — it is the concrete job. Any field in the manifest overrides the skill's defaults.
4. Produce the outputs declared in `output_targets`. Do not write files outside that list.
5. Validate every structured file you wrote: `uv run coc validate <path>`.
6. Write a `run.json` to `ops/runs/YYYY/MM/DD/<run_id>/run.json` conforming to [schemas/run.schema.json](../schemas/run.schema.json).
7. Call `uv run coc complete {{TASK_ID}} --state <terminal> --outputs '<json>'` where `<terminal>` is one of `done`, `review`, `blocked`, `failed`.

---

## Role

{{ROLE}}

---

## Applicable skill

**`{{APPLICABLE_SKILL}}`** — read [skills/{{APPLICABLE_SKILL}}/SKILL.md](../skills/{{APPLICABLE_SKILL}}/SKILL.md) before acting.

---

## Task manifest

```yaml
{{TASK_MANIFEST_CONTENT}}
```

---

## Output shape

Your work culminates in a `run.json` file with this shape (see [schemas/run.schema.json](../schemas/run.schema.json) for the authoritative constraint):

```json
{
  "run_id": "run-<ulid>",
  "task_id": "{{TASK_ID}}",
  "agent": {
    "runtime": "claude-code | codex | other",
    "model": "<optional model identifier or null>",
    "version": "<optional version string or null>"
  },
  "started_at": "<ISO-8601 UTC timestamp>",
  "ended_at": "<ISO-8601 UTC timestamp>",
  "status": "success | blocked | failed",
  "outputs": ["<path relative to repo root>", "..."],
  "events_appended": 0,
  "notes": "<optional freeform summary>"
}
```

The `outputs` list must match the files you wrote, in the order you wrote them. `events_appended` counts the number of lines you appended to any `ops/events/*.jsonl`.

---

## Stop conditions

Stop immediately — do not push further — when any of these hold:

- The skill's `stop_conditions` are met and you have written `run.json`.
- A non-negotiable from [AGENTS.md](../AGENTS.md) would be violated by the next action.
- A "Block or fail when" clause in the skill applies — set `status: blocked` and explain in `notes`.
- You would need to write a file not listed in `output_targets` — stop and report rather than expanding scope.

Do not ask clarifying questions of the user during execution. If the task as written is underspecified, `status: blocked` is the correct resolution.
