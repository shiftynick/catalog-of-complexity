---
name: profile-system
description: Define a single system's canonical record — boundary, components, interaction types, scales, and taxonomy placement. Produces `registry/systems/<id>/system.yaml` that downstream `extract-observations` and `analyze-archetypes` bind to.
status: active
inputs:
  - 'system_slug — kebab-case slug (e.g. `amazon-rainforest`, `ethernet-tcp-stack`).'
  - 'candidate_description — prose from a scouting pass.'
  - 'domain_slug — `system-domain:*` taxonomy slug.'
  - 'class_slugs — one or more `system-class:*` slugs.'
  - 'prior_sources — list of source IDs or DOIs.'
outputs:
  - '`registry/systems/sys-NNNNNN--<slug>/system.yaml` — canonical profile (schema-validated).'
  - '`registry/systems/sys-NNNNNN--<slug>/notes.md` — discursive context (history, controversies, open questions).'
  - '`registry/systems/sys-NNNNNN--<slug>/links.yaml` — structured cross-refs to sources, related systems, authoritative datasets.'
stop_conditions:
  - '`system.yaml` validates against `schemas/system.schema.json` with `status: profiled`.'
  - 'All taxonomy refs resolve.'
  - '`boundary`, `components`, `interaction_types`, `scales` are populated with specifics (not placeholders like "TBD").'
  - '`links.yaml` cites at least 2 authoritative sources.'
---

## When to use

Use this skill to turn a candidate proposal (from `scout-systems`) into a canonical system record. Trigger:

- A `profile-system` task lands in `ops/tasks/ready/`.
- An existing system record has a missing or incorrect structural field (boundary, scales, etc.) and a reviewer has requested repair.

Do **not** use this skill to add observations — that is `extract-observations`. Do **not** invent taxonomy slugs.

## Preconditions

- `domain_slug` and every `class_slug` resolve in `taxonomy/source/*.yaml`.
- No existing system record uses the same `slug`: `ls registry/systems | grep -i <slug>`.
- At least one source is either already in `registry/sources/` or listed in the task manifest for acquisition.

## Procedure

1. Allocate the system ID: `sys-NNNNNN--<slug>`, N = next unused zero-padded 6-digit integer.
2. Read 2-4 canonical sources. Focus on: boundary definitions, component taxonomy, known scales, dominant interaction modes.
3. Draft `system.yaml` with every required field from [system.schema.json](../../schemas/system.schema.json):
   - `id`, `slug`, `name`, `status: profiled` (the schema enum is `candidate | profiling | profiled | deprecated` — use `profiled` for a completed canonical profile).
   - `taxonomy_refs` — exactly one `system-domain:*`, one or more `system-class:*`.
   - `boundary` — what is in/out of scope, and the criterion for membership.
   - `components` — list of kinds of constituent entities with cardinality hints.
   - `interaction_types` — list of dominant interaction modes (e.g. predation, signaling, electrical, informational).
   - `scales` — object with `spatial` and `temporal` fields (the schema sets `additionalProperties: false` and declares only these two); each an ordered list of characteristic scales. Organizational-scale content, when relevant, belongs in `notes.md` or `components` — extending `scales` requires a schema change, which is out of scope for this skill.
   - `created_at`, `updated_at`.
4. Draft `notes.md` — prose sections: Overview, History, Controversies, Open Questions, Known-ill-defined aspects.
5. Draft `links.yaml` — `sources:` list of `src-NNNNNN` IDs or DOIs; `related_systems:` list of `sys-NNNNNN` IDs; `datasets:` list of `{name, url, license}`.
6. Run `uv run coc validate registry/systems/sys-NNNNNN--<slug>/`.
7. If any cited source is not already in `registry/sources/`, emit a follow-up task to acquire/register the source — do not fabricate a source ID.

## Output shape

- `system.yaml` — valid against [system.schema.json](../../schemas/system.schema.json). Each `scales.*` entry includes magnitude ranges where possible (e.g. `1 m–10^6 m`), not just labels.
- `notes.md` — markdown, no YAML frontmatter. Use header-level sections.
- `links.yaml` — lists only; no nested prose.

## Block or fail when

- The system's boundary cannot be defined without circularity ("the system is everything inside the system") — block with specific clarifying questions.
- Only one authoritative source exists — block and request `scout-systems` to surface more.
- Two or more `system-class` slugs fit equally well and the choice is non-obvious — propose a multi-class entry or block for reviewer judgement.
- An existing `sys-*` record covers the same boundary — block; propose a merge task.

## References

- [schemas/system.schema.json](../../schemas/system.schema.json)
- [taxonomy/source/system-domains.yaml](../../taxonomy/source/system-domains.yaml)
- [taxonomy/source/system-classes.yaml](../../taxonomy/source/system-classes.yaml)
- [registry/systems/sys-000001--amazon-rainforest/](../../registry/systems/sys-000001--amazon-rainforest/) — reference shape.
