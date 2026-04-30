# Cryosphere — notes

## Overview

The cryosphere is the planetary-scale envelope of frozen water (and, on
cold worlds, other frozen volatiles) at and near a planetary surface. On
Earth it integrates continental ice sheets, mountain glaciers and ice
caps, ice shelves, sea ice, lake and river ice, seasonal snow cover,
and the subsurface ground ice held in permafrost. The term itself
gained currency in the second half of the 20th century, paralleling
"hydrosphere" and "atmosphere", to name the slow-responding solid-water
component of the climate system that distinguishes glaciated from
non-glaciated states. Earth-system science treats it as one of the
"five spheres" alongside atmosphere, hydrosphere, lithosphere, and
biosphere; the IPCC reports devote a dedicated chapter to it.

The cryosphere is included in the catalog as a type-level archetype
because the same kind of system — a frozen-volatile reservoir whose
mass balance depends on energy balance, precipitation, gravity-driven
flow, and basal coupling to substrate — recurs on other planetary
bodies. Mars carries water-ice and CO2-ice polar caps with extensive
subsurface ground ice; Europa, Ganymede, and Enceladus carry kilometres
to tens of kilometres of water-ice shells over liquid oceans; Titan
combines a water-ice crust at ~94 K with a hydrocarbon (methane /
ethane) "cryosphere" in which the working volatile is itself an
organic. Treating cryosphere as a class lets the same boundary,
component, and dynamical concepts apply to all of these.

## Characteristic instances

- **Earth's modern cryosphere.** Antarctica (~26.5 × 10^6 km^3 of ice)
  and Greenland (~2.85 × 10^6 km^3) dominate the standing mass; the
  rest is ~158,000 mountain glaciers and ice caps, ~14 × 10^6 km^2 of
  Arctic March-maximum sea ice, ~18 × 10^6 km^2 of Antarctic
  September-maximum sea ice, ~50 × 10^6 km^2 of seasonal Northern-
  Hemisphere snow cover, and ~22 × 10^6 km^2 of Northern-Hemisphere
  permafrost. This is the canonical Cenozoic-glaciation reference state.
- **Last Glacial Maximum (~21 ka).** Laurentide, Cordilleran, and
  Fennoscandian ice sheets added ~50 × 10^6 km^3 of land ice; sea level
  was ~120 m below present. Used as the canonical full-glacial state in
  paleoclimate model intercomparisons.
- **Snowball / Slushball Earth (Cryogenian, ~720–635 Ma).** Hypothesised
  near-global ice cover triggered by runaway ice-albedo feedback. The
  canonical bifurcation state of the cryosphere, demonstrating that
  the same dynamical system admits qualitatively distinct climate
  attractors.
- **Mars.** Permanent water-and-CO2 polar caps (the south residual cap
  is CO2-rich; both have water-rich underlying layers), seasonal CO2
  frost down to mid-latitudes, and massive subsurface H2O ground ice
  imaged by SHARAD radar across the mid-latitudes. A canonical
  multi-volatile, low-pressure cryosphere.
- **Icy moons.** Europa's outer ice shell (~10–30 km thick) overlies a
  probable subsurface liquid water ocean. Enceladus's south-polar ice
  shell is locally fractured ("tiger stripes") and hosts active plumes.
  Ganymede has a thick ice mantle with multiple high-pressure ice
  phases. These extend the cryosphere concept to bodies where the
  cryosphere itself is a liquid-ocean lid.
- **Titan.** Surface water-ice crust at ~94 K plus a methane/ethane
  cycle with surface lakes, seas, and rivers — a hydrologic cycle
  whose working fluid is hydrocarbon rather than water. Often
  described as a "cryosphere" in extended use.

## Spatial subdivisions

For metric population the Earth cryosphere is naturally split into
sub-systems with different dynamics and timescales:

- **Land ice** — ice sheets, ice caps, glaciers, ice shelves. Slow
  (10^3–10^5 yr response), gravity-flow-dominated, the dominant
  long-term sea-level lever.
- **Sea ice** — perennial and seasonal floating ice. Fast (sub-annual
  to decadal), strongly thermodynamically and dynamically coupled to
  ocean and atmosphere; major albedo and ocean-circulation lever.
- **Snow cover** — annual; high albedo, short residence, dominant
  hemispheric albedo modulator.
- **Permafrost / ground ice** — frozen subsurface; large stored carbon
  pool, slow thermal response, abrupt-thaw failure modes via
  thermokarst.
- **Lake / river ice** — seasonal; ecologically important, weak
  global-energy-budget effect.

Several of these have their own candidate-systems-catalog entries
(glacial systems, permafrost systems) at lower priority; cryosphere
is the umbrella under which they integrate.

## Organizational neighbors

- **Just below**: glacier, ice sheet, sea ice, permafrost — bounded
  components of the integrated cryosphere; some are catalogued
  separately at lower priority.
- **Just above**: `earth-system` (sys-000027) — the integrated
  Earth-system; the cryosphere is its slow-response solid-water
  compartment.
- **Lateral / coupled**: `atmosphere` (sys-000126),
  `biosphere` (sys-000129), and the hydrosphere and lithosphere
  geosphere classmates with which the cryosphere continuously
  exchanges mass and energy. The climate system (`system-class:climate-system`
  in the taxonomy) is the dynamical superset that links all of them.
- **Component biota**: psychrophiles, polar megafauna, cold-adapted
  vegetation — the "cryospheric biosphere" called out in the biosphere
  notes.

## Open questions

- **Marine-ice-sheet instability magnitude and timing.** The West
  Antarctic Ice Sheet and parts of East Antarctica sit on
  retrograde-sloping beds below sea level. How fast a grounding-line
  retreat could proceed under contemporary forcing — and how much sea
  level it would commit — is a leading uncertainty in 21st- to
  23rd-century projections.
- **Permafrost-carbon feedback strength.** Total frozen-soil organic
  carbon (~1500 PgC across NH permafrost) is well-bounded; the
  fraction released as CO2 vs. CH4, and the timing of abrupt vs.
  gradual thaw pathways, are not.
- **Snowball-Earth bifurcation structure.** Whether the Cryogenian
  state was a hard ("snowball") or partial ("slushball") global
  glaciation, and what mechanisms broke the runaway, remain debated.
- **Icy-moon ice-shell thickness.** Europa's shell thickness estimates
  range 10–30+ km; this controls habitability arguments for any
  subsurface ocean. JUICE and Europa Clipper missions are designed to
  narrow this.

## Known-ill-defined aspects

- The boundary between **cryosphere and hydrosphere** is a phase
  boundary on a continuum: meltwater on a glacier surface, slush in
  sea-ice melt ponds, brine in firn, and subglacial water all sit at
  the interface. Operationally the catalog uses "solid phase of the
  dominant volatile" but counts and fluxes inherit the fuzziness.
- The boundary between **cryosphere and lithosphere** in permafrost
  regions is similarly soft: ice-cemented regolith, ground ice, and
  ice wedges interleave with mineral substrate. Convention treats
  ground ice as cryosphere when its mass balance is dominated by
  thermal regime rather than mineral processes.
- Extending the term to **non-water volatiles** (CO2 frost on Mars,
  methane on Titan, N2 on Triton) is convenient and increasingly
  standard but not universal; some authors restrict "cryosphere" to
  water ice. The catalog adopts the broad convention because it
  preserves the dynamical analogy.
- The **"cryosphere as system" claim** is partly definitional. Earth
  has had cryospheres only intermittently over its ~4.5 Gy history
  (notably Cryogenian, late Paleozoic, late Cenozoic); cryosphere is
  thus a recurring system state more than a permanent compartment.
