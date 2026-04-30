# Biosphere — notes

## Overview

The biosphere is the integrated planetary-scale system formed by all of
Earth's living organisms together with the parts of the atmosphere,
hydrosphere, lithosphere, and cryosphere with which life is in active
exchange. The term as a *system concept* (rather than as a synonym for
"life on Earth") was developed by Vladimir Vernadsky (1926), who treated
life collectively as a geological force comparable in magnitude to
tectonics or weathering. James Lovelock and Lynn Margulis later
extended the framing into the Gaia hypothesis, emphasising that
biotically mediated feedbacks regulate atmospheric and ocean chemistry
far from abiotic equilibrium.

The catalog includes biosphere alongside `ecosystem` because they are
distinct organizational levels: an ecosystem is a bounded patch where
biotic and abiotic components are functionally coupled at scales from
ponds to biomes; the biosphere is the *global integral* of all
ecosystems plus the planetary biogeochemical machinery that connects
them. The latter exhibits emergent properties — atmospheric oxygen
maintenance, planetary carbon-cycle regulation, latitudinal diversity
gradients — that are not visible at the ecosystem level.

## Singularity and canonical examples

There is exactly one known biosphere. Following the convention used for
`sys-000027--earth-system`, canonical examples list temporal **states**
of the singular system (Archean, Proterozoic post-GOE, Phanerozoic,
Holocene) rather than separate instances. Conjectured analogs include:

- A possible Martian biosphere (extant or extinct microbial subsurface)
- A possible Europan or Enceladean subsurface ocean biosphere
- Closed engineered analogs (Biosphere 2 in Arizona, BIOS-3 in
  Krasnoyarsk) — these are research-scale demonstrations of
  near-closure, not parallel biospheres

These are mentioned for completeness; the catalog entry is grounded in
the Earth case.

## Spatial subdivisions

The single biosphere has well-recognized substructures useful for
metric population:

- Marine biosphere — open-ocean phytoplankton, microbial loop, benthos.
  Hosts ~50 % of global net primary production.
- Terrestrial biosphere — forests, grasslands, soils, surface microbial
  communities; roughly the other ~50 % of NPP and the bulk of standing
  biomass (~450 Gt C of the ~550 Gt C total).
- Deep biosphere — subsurface microbes in continental and oceanic
  crust; ~10–20 % of total cell count, very low metabolic rates,
  long-residence carbon.
- Atmospheric / aerosolized biosphere — bacteria, fungal spores, and
  algae transported through the troposphere; small biomass but
  long-range coupling.
- Cryospheric biosphere — psychrophiles in sea ice, snow, glaciers,
  permafrost; sensitive to climate forcing.

Several of these populate distinct candidate-systems-catalog entries
in their own right (forest ecosystem, coral reef, soil ecosystem,
etc.); biosphere is the umbrella under which all are integrated.

## Organizational neighbors

- **Just below**: `ecosystem` (sys-000017) — bounded biotic-abiotic
  patches; biosphere is their planetary union plus inter-ecosystem
  fluxes.
- **Just above**: `earth-system` (sys-000027) — adds the technosphere
  and the deeper geophysical machinery; biosphere is the biotic core
  of the Earth system.
- **Lateral / coupled**: atmosphere, hydrosphere (oceans), lithosphere,
  cryosphere, pedosphere — geosphere classmates with which the
  biosphere is in continuous biogeochemical exchange.
- **Component level**: food webs, microbial communities, individual
  populations and metabolisms aggregated up through ecosystems.

## Open questions

- Strength of Gaia-style regulation. Whether biotic feedbacks
  *actively* stabilize planetary conditions (Lovelock-Margulis strong
  Gaia) or whether stability is an emergent statistical artifact
  (Watson-Lovelock Daisyworld; Tyrrell critique) remains contested.
- Quantitative deep-biosphere extent. Estimates of subsurface microbial
  biomass span an order of magnitude; metabolic rates are very low and
  hard to measure.
- Anthropocene transition. Whether the present biosphere should be
  treated as a continuation of the Holocene state or as a qualitatively
  new state requiring its own catalog entry. Currently catalogued as
  the canonical example "Holocene biosphere"; the technosphere-coupled
  state is captured in `sys-000027--earth-system` (Anthropocene).
- Origin and uniqueness. Whether life arose more than once on Earth
  (shadow biosphere hypothesis); whether other biospheres exist or
  ever existed in the solar system.

## Known-ill-defined aspects

- The vertical and lateral boundary is fuzzy. Subsurface microbes in
  oceanic crust extend kilometers down at metabolic rates so low that
  "active life" becomes a continuum question. Aerosolized microbes are
  transient. Operationally, the catalog uses "active biological
  metabolism coupled to surface biogeochemical cycling" as the
  inclusion criterion; counts and fluxes inherit this fuzziness.
- The "Gaia regulation" claim is partly testable, partly definitional.
  Care is needed when populating `main_feedbacks` and
  `emergent_properties` to distinguish established mechanisms
  (photosynthetic O2 production) from contested ones (purposive global
  homeostasis).
- The boundary with `earth-system` (sys-000027) is conventional.
  Biosphere excludes the technosphere; earth-system includes it. The
  two records will share many observations differing only in scope.
