# Ecological niche system — notes

## Overview

The ecological niche is a foundational ecological abstraction with a long
history. Grinnell (1917) framed niche as the habitat-and-conditions space of a
species. Elton (1927) reframed it as a species' functional role in its
community (its "profession"). Hutchinson (1957) synthesized both into the
n-dimensional hypervolume formulation that remains canonical: a niche is a
region in a high-dimensional space of environmental and resource axes within
which a population can persist with non-negative growth rate. The
fundamental-vs-realized distinction (also Hutchinson) — the niche an organism
could occupy in the absence of competitors and natural enemies, versus the
narrower niche it actually occupies — underpins most modern niche modelling.

The catalog treats the niche as a **type-level archetype**, not as an
instance. Concrete niches (Darwin's finch beak/seed niches, Anolis perch
niches) are listed under `canonical_examples`. The archetype is what survives
across instances: a set of environmental axes with tolerance / utilization
functions, a focal species or strategy, and a community of biotic interactors
that narrows the fundamental niche to a realized one.

## Characteristic instances

- **Darwin's finch radiation (Galápagos).** ~15 species partition seed-size
  axes; beak depth scales with seed-hardness. Documented natural-selection
  responses to drought-driven niche shifts (Grant & Grant). Canonical case
  for resource-axis partitioning.
- **Anolis lizards (Caribbean).** Repeated convergent evolution of the same
  ecomorphs (trunk-ground, trunk-crown, twig, etc.) on independent islands;
  Losos's work makes them the canonical case for niche convergence and
  conservatism.
- **Marine rocky-intertidal zonation.** Connell's barnacle experiments and
  Paine's keystone-predator work on Pisaster/Mytilus established that biotic
  interactions narrow vertical zonation away from the fundamental
  (physiological) limits.
- **Phytoplankton (Tilman's R\* theory).** One of the few mechanistic
  predictions of coexistence from resource-competition niche differentiation;
  silicate-limited diatoms vs. phosphate-limited green algae.
- **Soil microbial niches.** Increasingly studied via metagenomics; niches
  defined along carbon source, redox state, moisture, and pH axes, with
  enormous functional redundancy and overlapping niches.

## Organizational neighbors

- **Below.** Population — niche dynamics emerge from population-level birth,
  death, dispersal, and competition rates of one focal species.
- **Lateral.** Food web, ecosystem — the niche is one species' position in
  the larger ecological network; food webs and ecosystems describe the
  network and matter-cycle layers within which niches are embedded.
- **Above.** Biome / biogeographic region — the regional template of niches
  available to species; sets the upper bound on what realized niches the
  community can support.
- **Cross-cutting.** Adaptive radiation, character displacement, community
  assembly are processes that shape niches; they live as analyses, not
  separate type entries.

## Open questions

- **Niche dimensionality.** How many axes are practically necessary? Empirical
  niche models often use 5-15; theoretical work suggests effective
  dimensionality may be much lower due to trait correlations.
- **Niche conservatism vs. evolution.** When does niche overlap drive rapid
  divergence (character displacement) versus phylogenetic conservatism? The
  evolutionary timescale on which niches shift is poorly characterized
  cross-clades.
- **Niche-construction feedbacks.** Organisms modify their environment
  (beavers, trees, corals); the modified environment alters the niche. How
  pervasive is this effect, and when does it dominate over abiotic forcing?
- **The "empty niche" question.** Whether the metaphor of niches as
  pre-existing slots into which species fit is meaningful or a category
  error — modern community-assembly theory tends toward the latter, but
  invasion biology often invokes "empty niches" successfully.
- **Climate-driven niche tracking.** As climate envelopes shift faster than
  many species can disperse or evolve, how often does the fundamental niche
  outpace realized occupancy, and what predicts collapse vs. tracking?

## Known-ill-defined aspects

- The boundary of a niche is rarely sharp. Tolerance curves taper rather than
  truncate; what counts as the "edge" of the niche depends on the persistence
  threshold (e.g. λ ≥ 1 over what window?).
- The Grinnellian (habitat) vs. Eltonian (functional role) framings remain
  partly distinct; modern usage often blends them, but mechanistic models
  typically pick one.
- Niche width is metric-dependent: variance along axes, hypervolume,
  occupied-axis count all give different numbers and don't always order
  species the same way.
- Whether the realized niche is even uniquely defined under multispecies
  competition is debated — apparent competition and indirect interactions
  can make the realized-niche concept context-dependent.
