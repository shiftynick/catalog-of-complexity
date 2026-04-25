# Amazon rainforest — research notes

Free-form notes and working hypotheses about this system. Canonical structure
lives in `system.yaml`; this file is for discursive content that doesn't
belong in structured fields.

## Open questions

- What basin/biome framing is most defensible as the default boundary?
- Which observations require re-scoping when the source uses the hydrological
  basin vs. the biome delineation?
- How should we represent the human-ecological coupling — as a separate
  component, or as an interaction type?

## Deprecation

Deprecated 2026-04-25 by review-records task tsk-20260425-000016 under the
type-level inclusion criterion in [AGENTS.md](../../../AGENTS.md) ("What
counts as a system worth cataloging"). The Amazon rainforest is a specific
named biome — an *instance* of forest-biome / ecosystem types — not a
type-level archetype. Per the new policy, the periodic-table-of-complexity
catalog holds one entry per archetypal kind, with named biomes recorded as
canonical examples under the type entries.

**Replacement type slug(s)** that supersede this entry:

- `system-class:forest-biome` — already present in
  [taxonomy/source/system-classes.yaml](../../../taxonomy/source/system-classes.yaml).
  When that type-level entry lands, the prose and references on this record
  can be lifted into its `canonical_examples` and notes.md.
- `ecosystem` — listed in [config/priority-systems.yaml](../../../config/priority-systems.yaml);
  a `system-class:ecosystem` addition to system-classes.yaml is pending and
  will be filed via a paired `review-records` task before any
  `profile-system` for it runs.

**Audit posture.** Per the task notes (no-delete policy), the structured
record and this prose remain on disk for history. Downstream
`extract-observations` filters deprecated systems from its scope, so the
single existing observation against this id (obs-11111111, value-less stub)
is unaffected but no new observations should land here. Companion
deprecations from the same review-records batch retire sys-000002
(gut microbiome → microbiome), sys-000004 (C. elegans →
multicellular-organism), sys-000005 (neocortex → nervous-system), and
sys-000006 (rhizosphere micro → microbiome). sys-000003 (vertebrate
adaptive immune system) is the lone bootstrap entry kept as type-ish for
re-evaluation later.
