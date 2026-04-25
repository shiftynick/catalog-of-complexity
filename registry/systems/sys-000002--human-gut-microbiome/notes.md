# Human gut microbiome

## Overview

The human gut microbiome is a host-associated microbial ecosystem spanning the
gastrointestinal tract. In practice, most quantitative and metagenomic studies
profile it through fecal samples, which are an imperfect but widely used proxy
for the predominantly colonic community. Qin et al. (2010) established an early
large-scale metagenomic reference point by assembling a 3.3 million gene
catalogue from fecal samples of 124 European individuals and reported that each
individual carried at least 160 prevalent bacterial species. Sender et al.
(2016) provide the quantitative boundary cue that most bacterial cells in the
human body are concentrated in the colon rather than being evenly distributed
across the gastrointestinal tract. Prochazkova et al. (2024) show that this
system is not static: day-to-day variation tracks transit time, pH, stool
moisture, and metabolite turnover.

## History

Early gut microbiome work relied heavily on culture and 16S-based community
descriptions. Metagenomic sequencing shifted the field toward treating the gut
microbiome as a functional gene reservoir and interaction network rather than
only a taxonomic list. The MetaHIT catalogue in Qin et al. (2010) became a key
reference because it anchored the system in a shared gene inventory and a
minimal gut metagenome framing. Later quantitative reassessments such as Sender
et al. (2016) tightened the boundary between the general human microbiome and
the gut-dominant bacterial load by showing that the colon is the main reservoir
for bacterial abundance in a reference adult.

## Controversies

The system boundary is operationally useful but not perfectly clean. Fecal
sampling overrepresents distal gut output relative to microbial communities in
the small intestine and mucosa. There is also an ongoing conceptual tension
between "gut microbiota" as the living community and "gut microbiome" as either
the community plus genes, or the community plus genes and metabolites. This
record uses the broader systems framing because many system-level studies link
organisms, genes, metabolites, and host physiological constraints in the same
analysis.

## Open Questions

- How should lumen-associated and mucosa-associated communities be represented
  when their composition and host coupling differ materially?
- When should fecal measurements be treated as adequate proxies for the whole
  gut microbiome rather than as colon-weighted observations?
- How should virome, mycobiome, and archaeome subcommunities be represented
  when most longitudinal datasets remain bacteria-dominant?

## Known-ill-defined aspects

This system is best treated as a mixed boundary rather than a purely spatial
one. Membership depends on both location and functional residence within the
host gut environment. The exact distal limit of "gut" versus broader
"gastrointestinal" framing also varies across studies. For downstream
observation extraction, each metric should record whether the underlying source
sampled feces, lumen contents, biopsy material, or another proxy.

## Sources

- Qin J, Li R, Raes J, et al. A human gut microbial gene catalogue established
  by metagenomic sequencing. Nature 464, 59-65 (2010). DOI:
  10.1038/nature08821.
- Sender R, Fuchs S, Milo R. Revised Estimates for the Number of Human and
  Bacteria Cells in the Body. PLOS Biology 14(8):e1002533 (2016). DOI:
  10.1371/journal.pbio.1002533.
- Prochazkova N, Laursen MF, La Barbera G, et al. Gut physiology and
  environment explain variations in human gut microbiome composition and
  metabolism. Nature Microbiology 9, 3210-3225 (2024). DOI:
  10.1038/s41564-024-01856-x.

## Deprecation

Deprecated 2026-04-25 under tsk-20260425-000017 per the AGENTS.md "What
counts as a system worth cataloging" inclusion criterion. The human gut
microbiome is a host-specific, niche-specific *instance* of the
microbiome class, not a type-level archetype. The replacement type
slug is `microbiome` (resolved in
[taxonomy/source/system-classes.yaml](../../../taxonomy/source/system-classes.yaml);
queued in [config/priority-systems.yaml](../../../config/priority-systems.yaml)).

The prose above — boundary cues, components, interaction types, scales,
controversies, open questions — is preserved here so it can inform the
`canonical_examples` of the eventual type-level `microbiome` system
entry, alongside the rhizosphere microbiome (sys-000006, deprecated in
companion task tsk-20260425-000020). Do not delete this directory: the
material is the source for the host-associated branch of the eventual
type-level entry's examples.
