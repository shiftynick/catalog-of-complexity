# Rhizosphere microbiome

## Overview

The rhizosphere is the thin zone of soil under the direct chemical and physical
influence of living plant roots. Hiltner coined the term in 1904 to describe
the elevated microbial activity around legume roots; modern usage spans the
rhizoplane (root surface), the rhizosphere soil (exudate-influenced soil
millimetres from the root), and their coupling to root tissues at the
endosphere boundary. Philippot et al. (2013) provide the canonical current
framing as a microbial ecology system where selection is driven largely by
root exudates, rhizodeposition, and soil physical heterogeneity. Berendsen et
al. (2012) emphasize the functional coupling: community composition and
activity feed back into plant growth, nutrient status, and disease
susceptibility, making the rhizosphere microbiome a candidate target for
plant health management.

## History

Early rhizosphere work was dominated by culture-based studies of plant growth
promoting rhizobacteria and of specific pathogens. 16S and ITS amplicon
sequencing in the 2000s revealed host- and soil-type-specific community
patterns. Metagenomic and metatranscriptomic studies in the 2010s shifted
emphasis toward functional guilds (nitrogen cyclers, phosphate solubilizers,
carbon consumers) and toward the "cry for help" hypothesis in which stressed
plants recruit beneficial microbes via altered exudation. The system is now
commonly partitioned into bulk soil, rhizosphere soil, rhizoplane, and
endosphere in a nested-compartment sampling design.

## Controversies

- The operational boundary between rhizosphere and bulk soil varies across
  studies: some use a distance cutoff (e.g. soil within 1-2 mm of a root),
  others use a shake-off protocol, others use chemical criteria like elevated
  root-derived carbon. This record treats the boundary as mixed: primarily
  chemical (exudate gradient) with a spatial-scale guide (millimetres).
- Whether mycorrhizal fungi should be counted within the rhizosphere
  microbiome or treated as a distinct mycorrhizosphere system is unsettled.
  This record includes the interface but flags the ambiguity.
- The degree to which plants actively "select" their microbiome versus
  passively recruit from the available soil pool is an open quantitative
  question and a live source of contention in plant-microbe engineering work.

## Open Questions

- How should the rhizosphere microbiome be represented across host species,
  soil types, and climates when each combination produces a substantially
  different community and function?
- What are appropriate canonical metrics of "health" or "function" for this
  system given that community composition is only weakly predictive of
  outcomes like nutrient acquisition or pathogen suppression?
- How strongly do laboratory and greenhouse studies generalize to field
  rhizospheres given that spatial and temporal heterogeneity in soils is a
  first-order driver of community assembly?

## Known-ill-defined aspects

Membership of the rhizosphere microbiome is fundamentally an interface
concept. Operational definitions differ by sampling method, scale, and host
context. Downstream observation extraction should record, per metric, the
sampling protocol (bulk soil vs rhizosphere soil vs rhizoplane vs combined),
the host plant and growth stage, and the soil type or environmental context.
Measurements that conflate these compartments should be tagged as mixed-scope
rather than attributed to the rhizosphere sensu stricto.

## Sources

- Philippot L, Raaijmakers JM, Lemanceau P, van der Putten WH. Going back to
  the roots: the microbial ecology of the rhizosphere. Nature Reviews
  Microbiology 11(11):789-799 (2013). DOI: 10.1038/nrmicro3109.
- Berendsen RL, Pieterse CMJ, Bakker PAHM. The rhizosphere microbiome and
  plant health. Trends in Plant Science 17(8):478-486 (2012). DOI:
  10.1016/j.tplants.2012.04.001.

## Deprecation

Deprecated 2026-04-25 under tsk-20260425-000020 per the AGENTS.md "What
counts as a system worth cataloging" inclusion criterion. The
rhizosphere microbiome is a niche-specific *instance* of the microbiome
class — operationally defined by attachment to plant roots and the
exudate-influenced soil zone — not a type-level archetype. The
replacement type slug is `microbiome` (resolved in
[taxonomy/source/system-classes.yaml](../../../taxonomy/source/system-classes.yaml);
queued in [config/priority-systems.yaml](../../../config/priority-systems.yaml)).

The prose above — boundary cues (rhizoplane vs rhizosphere soil vs bulk
soil), components (rhizoplane bacteria, mycorrhizal partners, protistan
predators, phages, exudate pools), interaction types (root exudation,
predation, quorum sensing, mutualistic nutrient exchange, antagonism),
and the spatial/temporal scale ladder — is preserved here so it can
inform the `canonical_examples` of the eventual type-level `microbiome`
system entry. The rhizosphere case will sit alongside the human gut
microbiome (sys-000002, deprecated in companion task
tsk-20260425-000017) as the two seed exemplars of distinct
niche realizations of the same archetype: a host-associated gut
microbiome and an environment-interface root microbiome. Do not delete
this directory: the material is the source for the plant/soil branch of
the eventual type-level entry's examples.
