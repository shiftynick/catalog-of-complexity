# Microbiome

## Overview

A microbiome is the multi-taxon microbial community resident in a defined
niche - host tissue (gut, skin, oral cavity, root rhizosphere, sponge or coral
host) or environmental matrix (marine surface water, sediment column, deep
subsurface rock, built-environment surface) - bounded by the physical and
ecological interface separating resident microbiota from outside organisms.
Members include bacterial, archaeal, fungal, viral, and protistan populations
together with the microbial metabolite pools coupling the community to host
or matrix chemistry. The constitutive interactions are trophic cross-feeding,
syntrophy, competition for substrates and niches, phage predation, host or
niche signaling, niche modification, and horizontal gene transfer.

McFall-Ngai and colleagues (2013) framed the microbiome as a unifying concept
across hosts and environments and argued for treating multicellular life as
inherently host-microbe ecosystems. Costello and colleagues (2012) framed the
microbiome as a community subject to ecological assembly, succession, and
resilience dynamics shared with macro-ecological communities, and identified
neutral and niche processes as observable at the OTU level.

## Characteristic Instances

The canonical examples in `system.yaml` are deliberately broad. The human
gut microbiome is the highest-density and best-sequenced host-associated
case; the rhizosphere microbiome is the best-studied plant-associated case;
the marine surface (epipelagic) microbiome is the best-studied open-ocean
case. Beyond these, the oral, skin, sponge- and coral-associated, ruminant
rumen, deep-subsurface sediment, and built-environment microbiomes are
well-studied additional instances. Two existing registry entries -
`sys-000002--human-gut-microbiome` and `sys-000006--rhizosphere-microbiome` -
were profiled at instance level under an earlier scoping rule and are now
status `deprecated`; this type-level entry supersedes them at the catalog
level while their slugs remain reserved for canonical-examples references.

## Organizational Neighbors

Below the microbiome lives the individual microbial cell, profiled at the
type level under `system-class:unicellular-organism`. The microbiome
aggregates multiple unicellular populations across many species into a
community-level system. Just above sit ecosystem-scale entries that include
microbiomes plus their hosts and abiotic context: the host as a holobiont
(host plus all its microbiomes) sits adjacent under `multicellular-organism`
in host-associated cases, and habitat- or biome-level entries
(`forest-biome`, ocean-basin biogeochemical systems) sit above for
environmental microbiomes. The microbiome is not the same as the
host-microbe holobiont: the microbiome is the microbial-community subsystem
of that larger system.

## Open Questions

- How should microbiome state be represented at the community-system level?
  OTU/ASV abundance vectors, functional-gene complement, metabolic-flux
  potential, and community-level traits each capture different facets and
  are imperfectly inter-translatable.
- How do host-associated microbiomes interact with host adaptive immunity
  (see [sys-000003--vertebrate-adaptive-immune-system](../sys-000003--vertebrate-adaptive-immune-system/))?
  The mucosal-immunity / commensal-microbe interface is a major site of
  bidirectional control whose system-level dynamics are still being mapped.
- What sets the boundary of one microbiome versus another along a gradient
  (e.g. proximal versus distal gut, rhizosphere versus bulk soil, surface
  versus mesopelagic ocean)? Empirical splits often follow assay
  granularity rather than community structure.
- Which assembly outcomes are deterministic (niche-driven) versus stochastic
  (drift, founder-effect, phage-driven turnover)? The Costello et al. (2012)
  framing organizes the question but does not resolve it.

## Known-ill-defined aspects

The microbiome's boundary is functional and ecological rather than purely
spatial: a niche edge (gut wall, root surface, pycnocline, sediment-water
interface) is sharp at first approximation but blurred by transient
microorganisms, dispersal, and gradient overlap. Measurement proxies matter
- 16S amplicon sequencing, shotgun metagenomics, metatranscriptomics,
metabolomics, and culture-dependent assays do not interrogate the same
subsystem and can disagree on community composition by orders of magnitude.
Host-associated microbiomes additionally vary by sampling compartment
(luminal versus mucosa-associated, surface versus deep skin layers) more
than between healthy individuals. Downstream observation extraction should
record the niche compartment, the assay class, and the bioinformatic
pipeline so cross-study aggregation remains defensible.

## Sources

- McFall-Ngai M, Hadfield MG, Bosch TCG, Carey HV, Domazet-Loso T, et al.
  Animals in a bacterial world, a new imperative for the life sciences.
  Proceedings of the National Academy of Sciences 110(9):3229-3236 (2013).
  DOI: 10.1073/pnas.1218525110.
- Costello EK, Stagaman K, Dethlefsen L, Bohannan BJM, Relman DA. The
  application of ecological theory toward an understanding of the human
  microbiome. Science 336(6086):1255-1262 (2012). DOI:
  10.1126/science.1224203.
