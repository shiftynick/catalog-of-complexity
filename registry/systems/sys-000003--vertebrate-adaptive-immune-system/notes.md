# Vertebrate adaptive immune system

## Overview

The vertebrate adaptive immune system is the lymphocyte-mediated arm of jawed-
vertebrate immunity. Unlike germline-encoded innate defenses, it relies on
somatic rearrangement of antigen-receptor gene segments (V(D)J recombination) to
generate an estimated ~10^9–10^11 distinct B- and T-cell receptor specificities
per individual. Rare antigen-specific clones are selected and expanded after
encountering cognate antigen, producing antibody and cytotoxic responses that
mature in affinity and are retained as long-lived memory. Chaplin (2010)
provides a compact synthesis of the innate/adaptive division and the cellular
and molecular components of the adaptive response. Janeway's Immunobiology
(Murphy & Weaver, 9th ed., 2017) is the canonical textbook treatment of the
underlying mechanisms, from receptor diversity generation through effector
function and tolerance.

## History

The distinction between innate and adaptive immunity crystallized over the 20th
century through work on antibody specificity, clonal-selection theory
(Burnet, 1957), thymic dependence of cellular immunity, MHC restriction
(Zinkernagel and Doherty, 1974), and the discovery of V(D)J recombination
(Tonegawa, 1976). Subsequent decades added somatic hypermutation, class
switching, regulatory T cells, and an expanded map of helper-T-cell subsets.
The system is now framed as a repertoire-selection machine whose state can be
profiled at receptor-sequence resolution.

## Controversies

The boundary between adaptive and innate immunity is less sharp than the
textbook division suggests. Innate-like lymphocytes (γδ T cells, NKT cells,
MAIT cells, B-1 cells) use somatically rearranged receptors but behave with
near-germline specificities and short activation kinetics. Trained innate
immunity produces memory-like behavior without clonal selection. Whether such
populations should be counted inside this system depends on analytical goals;
this record keeps the defining criterion as dependence on somatic
diversification plus clonal selection, which includes innate-like lymphocytes
but excludes trained innate memory.

## Open Questions

- How should the adaptive immune repertoire be represented as a system-level
  state vector? Receptor-sequence distributions, clonal-abundance rank curves,
  and functional response breadths each capture different facets.
- How do mucosal adaptive responses (gut, lung, reproductive tract) interact
  with systemic lymphoid organs and with resident microbial communities such
  as [sys-000002--human-gut-microbiome](../sys-000002--human-gut-microbiome/)?
- How does the repertoire age, and how much of immunosenescence is cell-
  intrinsic versus niche- or repertoire-structural?
- How should tolerance failures be cataloged as system-level failure modes
  rather than individual diseases?

## Known-ill-defined aspects

Adaptive immunity's boundary is functional rather than spatial. Its components
are distributed across lymphoid organs, blood, lymph, mucosal tissues, and
every peripheral site lymphocytes traffic through. Measurement proxies matter:
peripheral blood sampling, tissue biopsies, single-cell receptor sequencing,
serological titers, and functional recall assays do not interrogate the same
subsystem. Downstream observation extraction should record both the measured
compartment and the assay class so cross-study aggregation remains defensible.

## Sources

- Chaplin DD. Overview of the immune response. J Allergy Clin Immunol
  125(2 Suppl 2):S3-23 (2010). DOI: 10.1016/j.jaci.2009.12.980.
- Murphy K, Weaver C. Janeway's Immunobiology, 9th edition. Garland Science
  (2017). ISBN 9780815345053.
