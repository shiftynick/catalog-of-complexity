---
name: profile-system
description: Define a type-level complex-system archetype's canonical record — boundary, components, interaction types, scales, taxonomy placement, and canonical examples. Produces `registry/systems/<id>/system.yaml` that downstream `extract-observations` and `analyze-archetypes` bind to. Type-level only; specific instances belong in `canonical_examples`, not as separate entries. See AGENTS.md "What counts as a system worth cataloging".
status: active
inputs:
  - 'system_slug — kebab-case slug naming the type (e.g. `metabolic-network`, `market`, `multicellular-organism`). Should match a `system-class` slug.'
  - 'candidate_description — prose from the scouting pass or priority-list entry.'
  - 'domain_slug — `system-domain:*` taxonomy slug.'
  - 'class_slugs — one or more `system-class:*` slugs.'
  - 'canonical_examples — list of 3+ well-known instances of this type (e.g. for `metabolic-network`: E. coli core metabolism, human RBC metabolism, methanogen archaea metabolism). Genuinely-singular types may have <3 with a justifying note.'
outputs:
  - '`registry/systems/sys-NNNNNN--<slug>/system.yaml` — canonical type-level profile (schema-validated).'
  - '`registry/systems/sys-NNNNNN--<slug>/notes.md` — discursive context (history, characteristic instances, organizational neighbors, open questions).'
  - '`registry/systems/sys-NNNNNN--<slug>/links.yaml` — optional structured cross-refs to foundational refs, related systems, authoritative datasets. Required only when the entry makes specific quantitative or contested claims.'
stop_conditions:
  - '`system.yaml` validates against `schemas/system.schema.json` with `status: profiled`.'
  - 'All taxonomy refs resolve.'
  - '`boundary`, `components`, `interaction_types`, `scales` are populated with specifics (not placeholders like "TBD").'
  - '`canonical_examples` lists ≥3 instances, OR the entry documents in `notes.md` why the type is genuinely singular.'
---

## When to use

Use this skill to turn a candidate type-level archetype (from `scout-systems` or a `plan-backlog` priority seed) into a canonical type entry. Trigger:

- A `profile-system` task lands in `ops/tasks/ready/`.
- An existing type-level system record has a missing or incorrect structural field (boundary, scales, etc.) and a reviewer has requested repair.

Do **not** use this skill to:

- Profile a specific instance (e.g. *E. coli*, the NYSE, the Amazon rainforest). Instances are listed in the type-level entry's `canonical_examples` field; they are not separate registry entries. See AGENTS.md "What counts as a system worth cataloging".
- Add observations — that is `extract-observations`.
- Invent taxonomy slugs — propose them via `review-records` and use `--unblock-on-taxonomy`.

## Preconditions

- `domain_slug` and every `class_slug` resolve in `taxonomy/source/*.yaml`.
- No existing **non-deprecated** system record uses the same `slug`: `ls registry/systems | grep -i <slug>`. Deprecated records with overlapping prose are fine — the new type entry supersedes them.
- The candidate satisfies the inclusion criterion in AGENTS.md (type not instance; distinct organizational level; recognizable characteristic structure; ≥3 well-known examples or genuinely singular; cross-applicable measurability). If unclear, block and request reviewer judgement.
- **`source_refs` is optional** for type-level entries (the entry's bare existence is canonical knowledge). Only when the entry makes specific quantitative or contested claims do `source_refs` become required, and only then does the prefixed-ref / `source-not-acquired` block clause below apply.

## Procedure

1. Allocate the system ID: `sys-NNNNNN--<slug>`, N = next unused zero-padded 6-digit integer.
2. Draft the type's archetypal definition from canonical knowledge — textbook-grade material that would appear in any complex-systems handbook or domain-specific introduction. Sources are not required for this step; the catalog assumes the agent recognizes the archetype by name. If the agent does not, block (the candidate may not satisfy the inclusion criterion).
3. Draft `system.yaml` with every required field from [system.schema.json](../../schemas/system.schema.json):
   - `id`, `slug`, `name`, `status: profiled` (the schema enum is `candidate | profiling | profiled | deprecated` — use `profiled` for a completed canonical type entry).
   - `taxonomy_refs` — exactly one `system-domain:*`, one or more `system-class:*`.
   - `boundary` — what is in/out of scope at the type level, and the criterion for an instance to count as one of this type. (Example: for `metabolic-network`, "the set of biochemical reactions catalyzed in a single cellular compartment of a single organism, plus the metabolites consumed and produced.")
   - `components` — list of kinds of constituent entities with cardinality hints. (Example for `metabolic-network`: enzymes, substrate metabolites, cofactors, transporters; cardinality 10²–10⁴ reactions for typical organisms.)
   - `interaction_types` — list of dominant interaction modes (e.g. predation, signaling, electrical, informational).
   - `scales` — object with `spatial` and `temporal` fields (the schema sets `additionalProperties: false` and declares only these two); each an ordered list of characteristic scales for the *type* (i.e. the range across instances). Organizational-scale content, when relevant, belongs in `notes.md` or `components` — extending `scales` requires a schema change, which is out of scope for this skill.
   - `canonical_examples` — array of `{name, note?}` objects. ≥3 well-known instances with optional one-line context. For genuinely-singular types (`the-internet`, `earth-system`), omit or list the single instance with a `note` explaining the singularity.
   - `source_refs` — optional. Empty by default for type-level entries. Cite when the entry's prose makes a specific quantitative or contested claim that should be grounded.
   - `created_at`, `updated_at`.
4. Draft `notes.md` — prose sections: Overview, Characteristic Instances (more discursive than `canonical_examples`), Organizational Neighbors (what's just below and just above this in Boulding-style ordering), Open Questions, Known-ill-defined aspects.
5. Draft `links.yaml` — optional. Include only if useful. `sources:` list of `src-NNNNNN` IDs (foundational textbooks or canonical reviews); `related_systems:` list of `sys-NNNNNN` IDs of organizational neighbors; `datasets:` list of `{name, url, license}` for any authoritative public datasets that aggregate measurements across instances of this type.
6. Run `uv run coc validate registry/systems/sys-NNNNNN--<slug>/`.

## Output shape

- `system.yaml` — valid against [system.schema.json](../../schemas/system.schema.json). Each `scales.*` entry includes magnitude ranges where possible (e.g. `1 m–10^6 m`), not just labels. `canonical_examples` populated with ≥3 instances unless the type is genuinely singular.
- `notes.md` — markdown, no YAML frontmatter. Use header-level sections.
- `links.yaml` — optional. Lists only; no nested prose.

## Block or fail when

- The candidate is an *instance*, not a type (e.g. C. elegans, the NYSE, the Amazon rainforest) — block; the candidate belongs in some other type-level entry's `canonical_examples`. Identify which type it exemplifies and note in the block reason.
- The candidate spans multiple organizational levels (e.g. "civilization", "the Mediterranean diet") — block; conceptual blends are downstream analyses, not catalog entries.
- The type's boundary cannot be defined without circularity ("the system is everything inside the system") — block with specific clarifying questions.
- Two or more `system-class` slugs fit equally well and the choice is non-obvious — propose a multi-class entry or block for reviewer judgement.
- An existing **non-deprecated** `sys-*` record covers the same type — block; propose a merge or supersede task.
- The entry needs to make a specific quantitative or contested claim and the cited `source_refs` use prefixed forms (`doi:`, `arxiv:`, `url:`) with no matching `registry/sources/src-*/` — block with reason `source-not-acquired`. plan-backlog Tier 0.75 owns acquisition; this skill is a consumer, not an acquirer. (Bare type-level entries with no quantitative claims do not require sources at all and never block on this clause.)

## References

- [schemas/system.schema.json](../../schemas/system.schema.json)
- [taxonomy/source/system-domains.yaml](../../taxonomy/source/system-domains.yaml)
- [taxonomy/source/system-classes.yaml](../../taxonomy/source/system-classes.yaml)
- [registry/systems/sys-000001--amazon-rainforest/](../../registry/systems/sys-000001--amazon-rainforest/) — reference shape.
