---
name: profile-system
description: Define a type-level complex-system archetype's canonical record — boundary, components, interaction types, scales, taxonomy placement, canonical examples, and the v0.2 structural facets (system_kind, substrate, origin, primary_function, main_feedbacks, dominant_constraints, emergent_properties, failure_modes, primary_resources). Two trigger modes — new-entry (no sys-* dir yet) and stub-upgrade (existing `bootstrap-stub` entry being raised to `candidate`). Type-level only; specific instances belong in `canonical_examples`, not as separate entries. See AGENTS.md "What counts as a system worth cataloging".
status: active
inputs:
  - 'system_slug — kebab-case slug naming the type (e.g. `metabolic-network`, `market`, `multicellular-organism`). Should match a `system-class` slug.'
  - 'candidate_description — prose from the scouting pass, priority-list entry, or the existing bootstrap-stub `summary`.'
  - 'domain_slug — `system-domain:*` taxonomy slug.'
  - 'class_slugs — one or more `system-class:*` slugs.'
  - 'canonical_examples — list of 3+ well-known instances of this type (e.g. for `metabolic-network`: E. coli core metabolism, human RBC metabolism, methanogen archaea metabolism). Genuinely-singular types may have <3 with a justifying note.'
  - 'mode — implicit, derived from registry state at run time: `new` if no `registry/systems/sys-*--<slug>/` exists; `upgrade` if one exists with `status: bootstrap-stub`. Reject if a non-stub entry already exists (block — needs reviewer judgement).'
outputs:
  - '`registry/systems/sys-NNNNNN--<slug>/system.yaml` — canonical type-level profile (schema-validated; status `candidate` after this skill, since review has not happened yet).'
  - '`registry/systems/sys-NNNNNN--<slug>/notes.md` — discursive context (history, characteristic instances, organizational neighbors, open questions).'
  - '`registry/systems/sys-NNNNNN--<slug>/links.yaml` — optional structured cross-refs to foundational refs, related systems, authoritative datasets. Required only when the entry makes specific quantitative or contested claims.'
stop_conditions:
  - '`system.yaml` validates against `schemas/system.schema.json` with `status: candidate` (a downstream `review-records` task promotes to `profiled`).'
  - 'All taxonomy refs resolve.'
  - '`boundary`, `components`, `interaction_types`, `scales` are populated with specifics (not the v0.2 `[bootstrap-stub: ...]` placeholder).'
  - 'v0.2 optional facets are populated where the archetype makes them meaningful: `system_kind`, `substrate`, `origin`, `primary_function`, `main_feedbacks`, `dominant_constraints`, `emergent_properties`, `failure_modes`, `primary_resources`. Populate at least four of those nine; explicitly omit any that genuinely do not apply (e.g. `failure_modes` for a `boundary_case` like ideal-gas).'
  - '`canonical_examples` lists ≥3 instances, OR the entry documents in `notes.md` why the type is genuinely singular.'
---

## When to use

Use this skill to turn a type-level archetype into a substantive canonical
type entry. There are **two triggers**:

1. **New entry** — `scout-systems` or a `plan-backlog` priority seed has
   identified an archetype that has no `registry/systems/sys-*--<slug>/`
   directory yet. This skill allocates a fresh sys-NNNNNN id and writes
   the full record from canonical knowledge.

2. **Stub upgrade** — bootstrap v0.2 imported the long-tail catalog into
   `registry/systems/sys-*` with `status: bootstrap-stub` and placeholder
   boundary/components/interaction_types. plan-backlog Tier 3 (profile
   debt, gated to `bootstrap` and `metrics-fill` phases) emits
   `profile-system` tasks for these stubs. This skill rewrites the
   existing `system.yaml` in place — preserving the original `id` and
   `created_at` — replacing placeholders with substantive content.

Do **not** use this skill to:

- Profile a specific instance (e.g. *E. coli*, the NYSE, the Amazon
  rainforest). Instances are listed in the type-level entry's
  `canonical_examples` field; they are not separate registry entries.
  See AGENTS.md "What counts as a system worth cataloging".
- Add observations — that is `extract-observations`.
- Invent taxonomy slugs — propose them via `review-records` and use
  `--unblock-on-taxonomy`.

## Preconditions

- `domain_slug` and every `class_slug` resolve in
  `taxonomy/source/*.yaml`.
- For **new** mode: no `registry/systems/sys-*--<slug>/` exists.
- For **upgrade** mode: exactly one `registry/systems/sys-*--<slug>/`
  exists, and its `system.yaml` has `status: bootstrap-stub`. If the
  status is `candidate`, `profiling`, `profiled`, or `deprecated`, this
  skill does not run — block with reason `not-a-stub` (the entry has
  already been touched by a curator or earlier upgrade pass; needs
  reviewer judgement).
- The candidate satisfies the inclusion criterion in AGENTS.md (type
  not instance; distinct organizational level; recognizable
  characteristic structure; ≥3 well-known examples or genuinely
  singular; cross-applicable measurability). If unclear, block and
  request reviewer judgement.
- **`source_refs` is optional** for type-level entries (the entry's
  bare existence is canonical knowledge). Only when the entry makes
  specific quantitative or contested claims do `source_refs` become
  required, and only then does the prefixed-ref / `source-not-acquired`
  block clause below apply.

## Procedure

1. **Resolve mode + id.**
   - List `registry/systems/sys-*--<slug>/` directories.
     - **0 matches** → new mode. Allocate `sys-NNNNNN--<slug>` where N
       is the next unused zero-padded 6-digit integer.
     - **1 match with status: bootstrap-stub** → upgrade mode. Reuse
       the existing `id` and the existing `created_at` (rewrite all
       other fields in place; bump `updated_at` to the current
       UTC timestamp).
     - **1 match with any other status** → block with reason
       `not-a-stub`.
     - **2+ matches** → block with reason `slug-collision`.

2. **Draft the type's archetypal definition from canonical knowledge** —
   textbook-grade material that would appear in any complex-systems
   handbook or domain-specific introduction. Sources are not required
   for this step; the catalog assumes the agent recognizes the
   archetype by name. If the agent does not, block (the candidate may
   not satisfy the inclusion criterion). For upgrade mode, the existing
   stub's `summary` cites the catalog section
   (`docs/framework/02-candidate-systems-catalog.md §X.Y`) — read that
   section as additional context.

3. **Draft `system.yaml`** with every required field plus the v0.2
   optional facets. Required fields from
   [system.schema.json](../../schemas/system.schema.json):
   - `id`, `slug`, `name`, `status: candidate` (this skill always
     writes `candidate`; a downstream `review-records` task promotes
     to `profiled`).
   - `taxonomy_refs` — exactly one `system-domain:*`, one or more
     `system-class:*`.
   - `boundary` — what is in/out of scope at the type level, and the
     criterion for an instance to count as one of this type. (Example:
     for `metabolic-network`, "the set of biochemical reactions
     catalyzed in a single cellular compartment of a single organism,
     plus the metabolites consumed and produced.")
   - `components` — list of kinds of constituent entities with
     cardinality hints. (Example for `metabolic-network`: enzymes,
     substrate metabolites, cofactors, transporters; cardinality
     10²–10⁴ reactions for typical organisms.)
   - `interaction_types` — list of dominant interaction modes (e.g.
     predation, signaling, electrical, informational).
   - `scales` — object with `spatial` and `temporal` fields; each an
     ordered list of characteristic scales for the *type* (the range
     across instances), with magnitude hints where possible (e.g.
     `cell ~10^-5 m`, `organism lifespan ~10^7 to 10^9 s`).
   - `canonical_examples` — array of `{name, note?}` objects. ≥3
     well-known instances with optional one-line context. For
     genuinely-singular types (`the-internet`, `earth-system`), omit
     or list the single instance with a `note` explaining the
     singularity.
   - `created_at` (preserve in upgrade mode), `updated_at`.

4. **Populate v0.2 optional facets** from
   [system.schema.json](../../schemas/system.schema.json) where the
   archetype makes them meaningful. Aim for at least four of the nine
   below; explicitly omit any that genuinely do not apply
   (e.g. `failure_modes` for `boundary_case` entries like ideal-gas).
   - `system_kind` — `class | transition | subsystem | model | boundary_case`.
     Default `class`. Use `transition` for emergence transitions
     (multicellularity, language). Use `model` for abstract/simulated
     systems (cellular automata, Ising). Use `boundary_case` for
     control anchors (simple-pendulum, ideal-gas). For upgrade mode
     the existing stub usually has this set already — preserve it
     unless the catalog clearly says otherwise.
   - `substrate` — single free-text string describing what the system is
     made of (e.g. "lipids, proteins, nucleic acids, water, ions" for
     a cell; "humans + built environment + infrastructure +
     institutions" for a city).
   - `origin` — `natural | designed | evolved | emergent | hybrid`.
   - `boundary_clarity` — `crisp | fuzzy | contested | multi-boundary`.
     Independent of `boundary.type`.
   - `primary_function` — one-sentence description of what the system
     does or maintains. Useful for cross-domain analogy queries.
   - `lifecycle_stage` — `formation | growth | maturity | senescence | collapse-or-renewal`.
     Most enduring archetypes are `maturity`.
   - `main_feedbacks` — list of salient feedback loops (positive and
     negative). Free-text descriptions; the typology is in
     `docs/framework/01-discovery-framework.md` §4.16, §5.4.
   - `dominant_constraints` — list of what limits the system's possible
     behavior: physical, energetic, informational, ecological, legal,
     social, computational, economic. From metric ontology §13.
   - `emergent_properties` — list of macro-level patterns not present
     at component level.
   - `failure_modes` — list of how the system tends to break. Use the
     failure-family vocabulary in `docs/framework/01-discovery-framework.md`
     §4.4 where possible (cascade, fragmentation, runaway-feedback,
     capture, lock-in, senescence, etc.).
   - `primary_resources` — list of what the system consumes/transforms
     to maintain function: energy, matter, information, attention,
     computation, capital, labor, trust, legitimacy, time, coordination
     bandwidth.

   For `priority` (P0/P1/P2/P3/C): in upgrade mode, preserve the
   existing value (set by bootstrap from the catalog priority tag);
   in new mode, set from the candidate-description / scouting-task
   notes if specified, else leave unset.

   `source_refs` — optional. Empty by default for type-level entries.
   Cite when the entry's prose makes a specific quantitative or
   contested claim that should be grounded.

5. **Draft `notes.md`** — prose sections: Overview, Characteristic
   Instances (more discursive than `canonical_examples`),
   Organizational Neighbors (what's just below and just above this in
   Boulding-style ordering), Open Questions, Known-ill-defined aspects.
   In upgrade mode this file does not exist yet; create it.

6. **Draft `links.yaml`** — optional. Include only if useful.
   `sources:` list of `src-NNNNNN` IDs; `related_systems:` list of
   `sys-NNNNNN` IDs of organizational neighbors; `datasets:` list of
   `{name, url, license}` for any authoritative public datasets that
   aggregate measurements across instances of this type.

7. **Validate.** `uv run coc validate registry/systems/sys-NNNNNN--<slug>/`.

## Output shape

- `system.yaml` — valid against
  [system.schema.json](../../schemas/system.schema.json). Each
  `scales.*` entry includes magnitude ranges where possible (e.g.
  `1 m–10^6 m`), not just labels. `canonical_examples` populated with
  ≥3 instances unless the type is genuinely singular. v0.2 facets
  populated where meaningful (≥4 of the 9 listed in step 4).
- `notes.md` — markdown, no YAML frontmatter. Use header-level sections.
- `links.yaml` — optional. Lists only; no nested prose.

## Reference shapes

Look at these v0.1 hand-authored entries when in doubt about depth and
phrasing:

- [registry/systems/sys-000007--cell/system.yaml](../../registry/systems/sys-000007--cell/system.yaml)
  — biological-domain reference; rich substrate, origin, feedbacks,
  failure modes, canonical examples.
- [registry/systems/sys-000016--ant-colony/system.yaml](../../registry/systems/sys-000016--ant-colony/system.yaml)
  — biological collective; superorganism class, stigmergic feedbacks.
- [registry/systems/sys-000017--ecosystem/system.yaml](../../registry/systems/sys-000017--ecosystem/system.yaml)
  — ecological reference; multi-class taxonomy, regime-shift failure
  modes.
- [registry/systems/sys-000020--city/system.yaml](../../registry/systems/sys-000020--city/system.yaml)
  — social/hybrid reference; mixed boundary type, scaling-law
  emergent properties.
- [registry/systems/sys-000028--simple-pendulum/system.yaml](../../registry/systems/sys-000028--simple-pendulum/system.yaml)
  — boundary_case reference; correctly-empty `failure_modes` and
  `main_feedbacks`.

## Block or fail when

- The candidate is an *instance*, not a type (e.g. C. elegans, the
  NYSE, the Amazon rainforest) — block; the candidate belongs in some
  other type-level entry's `canonical_examples`. Identify which type
  it exemplifies and note in the block reason.
- The candidate spans multiple organizational levels (e.g.
  "civilization", "the Mediterranean diet") — block; conceptual blends
  are downstream analyses, not catalog entries.
- The type's boundary cannot be defined without circularity ("the
  system is everything inside the system") — block with specific
  clarifying questions.
- Two or more `system-class` slugs fit equally well and the choice is
  non-obvious — propose a multi-class entry or block for reviewer
  judgement.
- For upgrade mode: the existing entry's status is **not**
  `bootstrap-stub` (it's `candidate`, `profiling`, `profiled`, or
  `deprecated`) — block with reason `not-a-stub`. The entry has
  already been touched.
- For new mode: an existing **non-deprecated** `sys-*` record covers
  the same type — block; propose a merge or supersede task.
- The entry needs to make a specific quantitative or contested claim
  and the cited `source_refs` use prefixed forms (`doi:`, `arxiv:`,
  `url:`) with no matching `registry/sources/src-*/` — block with
  reason `source-not-acquired`. plan-backlog Tier 0.75 owns
  acquisition; this skill is a consumer, not an acquirer. (Bare
  type-level entries with no quantitative claims do not require
  sources at all and never block on this clause.)

## References

- [schemas/system.schema.json](../../schemas/system.schema.json) — v0.2
  field reference.
- [taxonomy/source/system-domains.yaml](../../taxonomy/source/system-domains.yaml)
- [taxonomy/source/system-classes.yaml](../../taxonomy/source/system-classes.yaml)
- [taxonomy/source/system-kinds.yaml](../../taxonomy/source/system-kinds.yaml)
- [docs/framework/01-discovery-framework.md](../../docs/framework/01-discovery-framework.md)
  §4.4 (failure modes), §4.16 (feedbacks), §5 (per-system facets).
- [docs/framework/02-candidate-systems-catalog.md](../../docs/framework/02-candidate-systems-catalog.md)
  — every bootstrap-stub's summary cites a specific section here as
  source of canonical knowledge.
