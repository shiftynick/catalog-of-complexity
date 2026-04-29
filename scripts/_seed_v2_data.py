"""Long-tail catalog data for the v0.2 bootstrap seed.

Source-of-truth for `config/bootstrap_seed_v2.yaml` — the file is regenerated
by `scripts/build_seed_v2.py`. Each catalog section in
`docs/framework/02-candidate-systems-catalog.md` maps to one constant
below, organized as:

    SECTION_<n> = dict(
        section="3",
        domain="<system-domain slug>",
        default_kind="class",       # most entries
        entries=[
            # (slug, name, [class_slugs], priority, kind_override?)
            ("ant-colony", "Ant colony", ["superorganism"], "P0", None),
            ...
        ],
    )

`class_slugs` reference `taxonomy/source/system-classes.yaml`. When no
class fits, leave the list empty — the entry is still valid (the
domain-level taxonomy_ref alone satisfies the schema's minItems: 1).
The status `bootstrap-stub` flags the entry for upgrade.

A SKIP set excludes slugs already present in the v0.1 hand-authored seed
(`config/bootstrap_seed.yaml`) — the bootstrap script is also slug-idempotent
so SKIP is belt-and-suspenders.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# Slugs already covered by config/bootstrap_seed.yaml (v0.1). Generator skips
# any entry whose slug is in this set so the v0.2 file is purely additive.
# --------------------------------------------------------------------------
V01_SLUGS: set[str] = {
    "cosmic-large-scale-structure",
    "stellar-system",
    "turbulent-fluid",
    "phase-transition-system",
    "chemical-element-system",
    "prebiotic-metabolism",
    "cell",
    "eukaryotic-cell",
    "multicellular-organism",
    "gene-regulatory-network",
    "metabolic-network",
    "microbiome",
    "immune-system",
    "nervous-system",
    "brain",
    "ant-colony",
    "ecosystem",
    "food-web",
    "language",
    "city",
    "market",
    "power-grid",
    "internet",
    "open-source-ecosystem",
    "scientific-community",
    "ai-system",
    "earth-system",
    "simple-pendulum",
    "ideal-gas",
    "clockwork-mechanism",
    "random-noise-field",
    "linear-supply-chain",
}


# --------------------------------------------------------------------------
# Per-domain stub templates. The generator merges these defaults into each
# entry, overridden by anything the entry-level dict supplies. Designed to
# satisfy the schema's minimum-content constraints with honest placeholders
# that flag the bootstrap-stub status without polluting search.
# --------------------------------------------------------------------------
STUB_PLACEHOLDER = "[bootstrap-stub: pending profile-system upgrade]"

DOMAIN_STUB_TEMPLATES: dict[str, dict] = {
    "physical": dict(
        boundary={
            "type": "spatial",
            "description": "Type-level physical archetype; spatial boundary refined in profile-system upgrade.",
        },
        components=[STUB_PLACEHOLDER],
        interaction_types=[STUB_PLACEHOLDER],
        scales={},
    ),
    "biological": dict(
        boundary={
            "type": "spatial",
            "description": "Type-level biological archetype; refine boundary in profile-system upgrade.",
        },
        components=[STUB_PLACEHOLDER],
        interaction_types=[STUB_PLACEHOLDER],
        scales={},
    ),
    "ecological": dict(
        boundary={
            "type": "spatial",
            "description": "Type-level ecological archetype; refine boundary in profile-system upgrade.",
        },
        components=[STUB_PLACEHOLDER],
        interaction_types=[STUB_PLACEHOLDER],
        scales={},
    ),
    "social": dict(
        boundary={
            "type": "mixed",
            "description": "Type-level social archetype; spatial-and-functional boundary refined in profile-system upgrade.",
        },
        components=[STUB_PLACEHOLDER],
        interaction_types=[STUB_PLACEHOLDER],
        scales={},
    ),
    "economic": dict(
        boundary={
            "type": "functional",
            "description": "Type-level economic archetype; functional boundary refined in profile-system upgrade.",
        },
        components=[STUB_PLACEHOLDER],
        interaction_types=[STUB_PLACEHOLDER],
        scales={},
    ),
    "technological": dict(
        boundary={
            "type": "functional",
            "description": "Type-level technological archetype; functional boundary refined in profile-system upgrade.",
        },
        components=[STUB_PLACEHOLDER],
        interaction_types=[STUB_PLACEHOLDER],
        scales={},
    ),
    "computational": dict(
        boundary={
            "type": "functional",
            "description": "Type-level computational archetype; refine boundary in profile-system upgrade.",
        },
        components=[STUB_PLACEHOLDER],
        interaction_types=[STUB_PLACEHOLDER],
        scales={},
    ),
    "cognitive": dict(
        boundary={
            "type": "functional",
            "description": "Type-level cognitive/epistemic archetype; refine boundary in profile-system upgrade.",
        },
        components=[STUB_PLACEHOLDER],
        interaction_types=[STUB_PLACEHOLDER],
        scales={},
    ),
}


# --------------------------------------------------------------------------
# Catalog data, by section. Each entry tuple:
#     (slug, name, [class_slugs], priority, kind_override or None)
# Default kind is "class". Override to "transition", "model", "boundary_case"
# or "subsystem" where appropriate.
# --------------------------------------------------------------------------

# ----- §3 Morowitz emergence anchors -----
SECTION_3 = dict(
    section="3",
    domain="physical",  # overridden per-entry where biological/social
    default_kind="class",
    entries=[
        # cosmological / physical (already in v0.1 except the few below)
        ("primordium", "Primordium / early universe", ["cosmic-structure"], "P0", "transition"),
        ("planetary-structure", "Planetary structure", ["planetary-system"], "P0", None),
        ("geosphere", "Geospheres (collective)", ["geosphere"], "P0", None),
        # biological emergence transitions
        ("animal-bodyplan", "Animal body plan", ["multicellular-organism"], "P0", "transition"),
        ("chordate-bodyplan", "Chordate body plan", ["multicellular-organism"], "P0", "transition"),
        ("vertebrate", "Vertebrate", ["multicellular-organism"], "P0", "transition"),
        ("aquatic-terrestrial-transition", "Fish-to-amphibian (aquatic-terrestrial) transition", ["multicellular-organism"], "P0", "transition"),
        ("amniote", "Reptile / amniote", ["multicellular-organism"], "P0", "transition"),
        ("mammal", "Mammal", ["multicellular-organism"], "P0", "transition"),
        ("primate", "Primate", ["multicellular-organism"], "P0", "transition"),
        ("great-ape", "Great ape", ["multicellular-organism"], "P0", "transition"),
        ("hominid", "Hominid / hominization", ["multicellular-organism"], "P0", "transition"),
        ("toolmaking", "Toolmaking", ["cultural-system"], "P0", "transition"),
        ("agriculture-emergence", "Agriculture (emergence)", ["cultural-system"], "P0", "transition"),
        ("urbanization-emergence", "Urbanization (emergence)", ["city"], "P0", "transition"),
        ("reflective-thought", "Philosophy / reflective thought", ["cultural-system", "knowledge-system"], "P0", "transition"),
        ("meaning-making-system", "Meaning-making (religion, cosmology, value systems)", ["cultural-system"], "P0", None),
    ],
)
# Override: many §3 entries are biological/cultural — assign per-entry
SECTION_3_DOMAIN_BY_SLUG: dict[str, str] = {
    "primordium": "physical",
    "planetary-structure": "physical",
    "geosphere": "ecological",
    "animal-bodyplan": "biological",
    "chordate-bodyplan": "biological",
    "vertebrate": "biological",
    "aquatic-terrestrial-transition": "biological",
    "amniote": "biological",
    "mammal": "biological",
    "primate": "biological",
    "great-ape": "biological",
    "hominid": "biological",
    "toolmaking": "social",
    "agriculture-emergence": "social",
    "urbanization-emergence": "social",
    "reflective-thought": "cognitive",
    "meaning-making-system": "social",
}


# ----- §4.1 Cosmic systems -----
SECTION_4_1 = dict(
    section="4.1",
    domain="physical",
    default_kind="class",
    entries=[
        ("galaxy-cluster", "Galaxy cluster", ["cosmic-structure"], "P0", None),
        ("galaxy", "Galaxy", ["cosmic-structure"], "P0", None),
        ("spiral-galaxy", "Spiral galaxy", ["cosmic-structure"], "P1", None),
        ("elliptical-galaxy", "Elliptical galaxy", ["cosmic-structure"], "P1", None),
        ("dwarf-galaxy", "Dwarf galaxy", ["cosmic-structure"], "P1", None),
        ("star-forming-region", "Star-forming region / molecular cloud", ["cosmic-structure"], "P1", None),
        ("star-cluster", "Star cluster", ["cosmic-structure"], "P1", None),
        ("binary-star-system", "Binary star system", ["stellar-system"], "P1", None),
        ("accretion-disk", "Accretion disk", [], "P1", None),
        ("black-hole-accretion", "Black hole accretion environment", [], "P1", None),
        ("supernova-remnant", "Supernova remnant", [], "P1", None),
        ("interstellar-medium", "Interstellar medium", [], "P1", None),
        ("magnetized-plasma", "Magnetized plasma system", [], "P1", None),
        ("pulsar-magnetosphere", "Pulsar magnetosphere", [], "P2", None),
        ("planet-moon-system", "Planet-moon system", ["stellar-system"], "P2", None),
        ("ring-system", "Planetary ring system", [], "P2", None),
        ("asteroid-belt", "Asteroid belt", [], "P2", None),
        ("cometary-system", "Cometary system", [], "P2", None),
        ("exoplanetary-system", "Exoplanetary system", ["stellar-system"], "P2", None),
    ],
)


# ----- §4.2 Physical dynamical systems -----
SECTION_4_2 = dict(
    section="4.2",
    domain="physical",
    default_kind="class",
    entries=[
        ("plasma", "Plasma", [], "P0", None),
        ("convective-system", "Convective system", ["turbulent-fluid"], "P1", None),
        ("reaction-diffusion-system", "Reaction-diffusion system", ["chemical-reaction-network"], "P1", None),
        ("nonlinear-oscillator", "Nonlinear oscillator", [], "P1", None),
        ("coupled-oscillator-network", "Coupled oscillator network", ["kuramoto-oscillator"], "P1", None),
        ("granular-medium", "Granular medium", ["granular-medium"], "P1", None),
        ("avalanche-system", "Avalanche system", ["self-organized-critical-system"], "P1", None),
        ("sand-dune-system", "Sand dune system", [], "P1", None),
        ("river-sediment-transport", "River sediment transport", [], "P1", None),
        ("wildfire-dynamics", "Wildfire dynamics", [], "P1", None),
        ("flame-front", "Flame front", [], "P1", None),
        ("earthquake-fault-network", "Earthquake fault network", ["self-organized-critical-system"], "P1", None),
        ("percolation-system", "Percolation system", [], "P1", None),
        ("spin-glass", "Spin glass", [], "P1", None),
        ("magnetic-domain-system", "Magnetic domain system", [], "P1", None),
        ("crystal-growth", "Crystal growth system", [], "P1", None),
        ("glass-formation", "Glass formation", [], "P1", None),
        ("superconducting-system", "Superconducting system", ["phase-transition-system"], "P2", None),
        ("fracture-network", "Fracture network", [], "P2", None),
        ("self-organized-critical-system", "Self-organized critical system", ["self-organized-critical-system"], "P2", None),
    ],
)


# ----- §5 Chemical and material systems -----
SECTION_5 = dict(
    section="5",
    domain="physical",
    default_kind="class",
    entries=[
        ("atomic-system", "Atomic system", ["atomic-system"], "P0", None),
        ("molecular-system", "Molecular system", ["molecular-system"], "P0", None),
        ("chemical-reaction-network", "Chemical reaction network", ["chemical-reaction-network"], "P0", None),
        ("autocatalytic-set", "Autocatalytic chemical set", ["autocatalytic-set"], "P0", None),
        ("combustion-system", "Combustion system", ["chemical-reaction-network"], "P1", None),
        ("catalytic-network", "Catalytic network", ["chemical-reaction-network"], "P1", None),
        ("polymerization-system", "Polymerization system", ["chemical-reaction-network"], "P1", None),
        ("protein-folding-system", "Protein folding system", ["protein-folding-system"], "P1", None),
        ("enzyme-network", "Enzyme network", ["metabolic-network"], "P1", None),
        ("colloid", "Colloid", [], "P1", None),
        ("emulsion", "Emulsion", [], "P1", None),
        ("aerosol", "Aerosol", [], "P1", None),
        ("crystal-lattice", "Crystal lattice", ["crystal-lattice"], "P1", None),
        ("materials-microstructure", "Materials microstructure", [], "P1", None),
        ("corrosion-system", "Corrosion system", [], "P1", None),
        ("mineral-formation", "Mineral formation system", [], "P1", None),
        ("atmospheric-chemistry", "Atmospheric chemistry system", ["chemical-reaction-network"], "P1", None),
        ("industrial-chemical-production", "Industrial chemical production system", ["chemical-reaction-network"], "P2", None),
        ("pharmaceutical-synthesis", "Pharmaceutical synthesis network", ["chemical-reaction-network"], "P2", None),
        ("battery-chemistry", "Battery chemistry system", [], "P2", None),
        ("semiconductor-fabrication", "Semiconductor fabrication process", [], "P2", None),
        ("nanomaterial-self-assembly", "Nanomaterial self-assembly", [], "P2", None),
        ("photochemical-system", "Photochemical system", ["chemical-reaction-network"], "P2", None),
    ],
)


# ----- §6.1 Planetary systems -----
SECTION_6_1 = dict(
    section="6.1",
    domain="physical",
    default_kind="class",
    entries=[
        ("planetary-climate-system", "Planetary climate system", ["climate-system"], "P0", None),
        ("planetary-interior-system", "Planetary interior system", ["planetary-system"], "P0", None),
        ("plate-tectonic-system", "Plate tectonic system", ["planetary-system"], "P1", None),
        ("mantle-convection", "Mantle convection", ["planetary-system"], "P1", None),
        ("planetary-dynamo", "Planetary dynamo / magnetic-field generation", ["planetary-system"], "P1", None),
        ("volcanic-system", "Volcanic system", [], "P1", None),
        ("hydrothermal-vent-system", "Hydrothermal vent system", [], "P1", None),
        ("impact-cratering-system", "Impact-cratering system", [], "P1", None),
        ("planetary-atmosphere-evolution", "Planetary atmosphere evolution", [], "P1", None),
        ("planetary-habitability", "Planetary habitability system", [], "P1", None),
        ("mars-system", "Mars climate / geological system", ["planetary-system"], "P2", None),
        ("venus-system", "Venus atmosphere system", [], "P2", None),
        ("gas-giant-atmosphere", "Gas giant atmosphere system", [], "P2", None),
        ("icy-moon-subsurface-ocean", "Icy moon subsurface ocean system", [], "P2", None),
    ],
)


# ----- §6.2 Earth geospheres and cycles -----
SECTION_6_2 = dict(
    section="6.2",
    domain="ecological",
    default_kind="class",
    entries=[
        ("atmosphere", "Atmosphere", ["geosphere"], "P0", None),
        ("hydrosphere", "Hydrosphere", ["geosphere"], "P0", None),
        ("lithosphere", "Lithosphere", ["geosphere"], "P0", None),
        ("biosphere", "Biosphere", ["biosphere", "geosphere"], "P0", None),
        ("cryosphere", "Cryosphere", ["geosphere"], "P0", None),
        ("pedosphere", "Pedosphere / soil system", ["geosphere"], "P0", None),
        ("global-climate-system", "Global climate system", ["climate-system"], "P1", None),
        ("ocean-circulation", "Ocean circulation", ["ocean-circulation-cell"], "P1", None),
        ("jet-stream-system", "Jet stream system", [], "P1", None),
        ("monsoon-system", "Monsoon system", [], "P1", None),
        ("hurricane-system", "Hurricane / cyclone system", [], "P1", None),
        ("enso", "El Nino-Southern Oscillation", [], "P1", None),
        ("carbon-cycle", "Carbon cycle", ["biogeochemical-cycle"], "P1", None),
        ("nitrogen-cycle", "Nitrogen cycle", ["biogeochemical-cycle"], "P1", None),
        ("phosphorus-cycle", "Phosphorus cycle", ["biogeochemical-cycle"], "P1", None),
        ("sulfur-cycle", "Sulfur cycle", ["biogeochemical-cycle"], "P1", None),
        ("water-cycle", "Water cycle", ["biogeochemical-cycle"], "P1", None),
        ("glacial-system", "Glacial system", [], "P1", None),
        ("river-network", "River network", ["river-network"], "P1", None),
        ("delta-system", "Delta system", [], "P1", None),
        ("watershed", "Watershed", ["river-network"], "P1", None),
        ("desert-system", "Desert system", ["ecosystem"], "P1", None),
        ("mountain-building-system", "Mountain-building system", [], "P1", None),
        ("coastal-erosion", "Coastal erosion system", [], "P2", None),
        ("permafrost-system", "Permafrost system", [], "P2", None),
        ("urban-heat-island", "Urban heat island system", [], "P2", None),
    ],
)


# ----- §7.1 Molecular and cellular systems -----
SECTION_7_1 = dict(
    section="7.1",
    domain="biological",
    default_kind="class",
    entries=[
        ("genome", "Genome", ["genome"], "P0", None),
        ("metabolism", "Metabolism (cellular)", ["metabolic-network"], "P0", None),
        ("protein-interaction-network", "Protein interaction network", ["protein-interaction-network"], "P0", None),
        ("epigenetic-system", "Epigenetic system", [], "P1", None),
        ("rna-regulatory-system", "RNA regulatory system", ["gene-regulatory-network"], "P1", None),
        ("signal-transduction-network", "Signal transduction network", ["signal-transduction-network"], "P1", None),
        ("cell-membrane-system", "Cell membrane system", [], "P1", None),
        ("cytoskeleton", "Cytoskeleton", [], "P1", None),
        ("mitochondrial-system", "Mitochondrial system", [], "P1", None),
        ("chloroplast-system", "Chloroplast system", [], "P1", None),
        ("microbial-colony", "Microbial colony", [], "P1", None),
        ("biofilm", "Biofilm", [], "P1", None),
        ("quorum-sensing-system", "Quorum sensing system", [], "P1", None),
        ("viral-replication-system", "Viral replication system", [], "P1", None),
        ("phage-bacteria-ecosystem", "Phage-bacteria ecosystem", [], "P1", None),
        ("horizontal-gene-transfer-network", "Horizontal gene transfer network", [], "P1", None),
        ("crispr-immune-system", "CRISPR immune system (microbial)", ["immune-system"], "P1", None),
        ("synthetic-biology-circuit", "Synthetic biology circuit", ["gene-regulatory-network"], "P2", None),
        ("engineered-metabolic-pathway", "Engineered metabolic pathway", ["metabolic-network"], "P2", None),
        ("organoid", "Organoid", ["multicellular-organism"], "P2", None),
        ("lab-grown-tissue", "Lab-grown tissue system", ["multicellular-organism"], "P2", None),
    ],
)


# ----- §7.2 Organism-level systems -----
SECTION_7_2 = dict(
    section="7.2",
    domain="biological",
    default_kind="class",
    entries=[
        ("developmental-system", "Development / morphogenesis", ["developmental-system"], "P0", None),
        ("endocrine-system", "Endocrine system", ["endocrine-system"], "P1", None),
        ("circulatory-system", "Circulatory system", ["circulatory-system"], "P1", None),
        ("respiratory-system", "Respiratory system", [], "P1", None),
        ("digestive-system", "Digestive system", [], "P1", None),
        ("reproductive-system", "Reproductive system", [], "P1", None),
        ("musculoskeletal-system", "Musculoskeletal system", [], "P1", None),
        ("microbiome-host-system", "Microbiome-host system", ["microbiome", "multicellular-organism"], "P1", None),
        ("brain-body-regulatory-system", "Brain-body regulatory system", [], "P1", None),
        ("aging-system", "Aging system", ["aging-system"], "P1", None),
        ("cancer-system", "Cancer (somatic evolution)", ["cancer-system"], "P1", None),
        ("wound-healing", "Wound healing", [], "P1", None),
        ("embryogenesis", "Embryogenesis", ["developmental-system"], "P1", None),
        ("plant-vascular-system", "Plant vascular system", [], "P1", None),
        ("plant-root-network", "Plant root network", [], "P1", None),
        ("mycorrhizal-system", "Mycorrhizal plant-fungal system", [], "P1", None),
        ("athletic-performance-system", "Human athletic performance system", [], "P2", None),
        ("sleep-regulation-system", "Sleep regulation system", [], "P2", None),
        ("stress-response-system", "Stress response system", [], "P2", None),
        ("disease-progression-system", "Disease progression system", [], "P2", None),
    ],
)


# ----- §7.3 Evolutionary systems -----
SECTION_7_3 = dict(
    section="7.3",
    domain="biological",
    default_kind="class",
    entries=[
        ("evolutionary-system", "Biological evolution", ["evolutionary-system"], "P0", None),
        ("natural-selection-system", "Natural selection system", ["evolutionary-system"], "P0", None),
        ("speciation-system", "Speciation system", ["speciation-system"], "P0", None),
        ("adaptive-radiation", "Adaptive radiation", ["coevolutionary-system"], "P1", None),
        ("coevolutionary-system", "Coevolution", ["coevolutionary-system"], "P1", None),
        ("predator-prey-evolution", "Predator-prey evolution", ["coevolutionary-system"], "P1", None),
        ("host-pathogen-evolution", "Host-pathogen evolution", ["coevolutionary-system"], "P1", None),
        ("sexual-selection", "Sexual selection", ["evolutionary-system"], "P1", None),
        ("domestication", "Domestication", [], "P1", None),
        ("evolutionary-arms-race", "Evolutionary arms race", ["coevolutionary-system"], "P1", None),
        ("mass-extinction-recovery", "Mass extinction and recovery system", [], "P1", None),
        ("phylogenetic-diversification", "Phylogenetic diversification", ["speciation-system"], "P1", None),
        ("niche-construction", "Niche construction", [], "P1", None),
        ("experimental-evolution", "Experimental evolution system", ["evolutionary-system"], "P2", None),
        ("directed-evolution", "Directed evolution", [], "P2", None),
        ("artificial-selection", "Artificial selection system", [], "P2", None),
        ("antibiotic-resistance-evolution", "Evolution of antibiotic resistance", [], "P2", None),
        ("pesticide-resistance-evolution", "Evolution of pesticide resistance", [], "P2", None),
    ],
)


# ----- §8 Ecological systems -----
SECTION_8 = dict(
    section="8",
    domain="ecological",
    default_kind="class",
    entries=[
        ("ecological-niche", "Ecological niche system", ["niche-system"], "P0", None),
        ("forest-ecosystem", "Forest ecosystem", ["ecosystem", "forest-biome"], "P1", None),
        ("rainforest", "Rainforest", ["ecosystem", "forest-biome"], "P1", None),
        ("boreal-forest", "Boreal forest", ["ecosystem", "forest-biome"], "P1", None),
        ("grassland-ecosystem", "Grassland ecosystem", ["ecosystem"], "P1", None),
        ("savannah-ecosystem", "Savannah ecosystem", ["ecosystem"], "P1", None),
        ("desert-ecosystem", "Desert ecosystem", ["ecosystem"], "P1", None),
        ("wetland-ecosystem", "Wetland ecosystem", ["ecosystem"], "P1", None),
        ("coral-reef", "Coral reef ecosystem", ["ecosystem"], "P1", None),
        ("kelp-forest", "Kelp forest", ["ecosystem"], "P1", None),
        ("estuary", "Estuary", ["ecosystem"], "P1", None),
        ("river-ecosystem", "River ecosystem", ["ecosystem", "river-network"], "P1", None),
        ("lake-ecosystem", "Lake ecosystem", ["ecosystem"], "P1", None),
        ("deep-sea-vent-ecosystem", "Deep-sea vent ecosystem", ["ecosystem"], "P1", None),
        ("polar-ecosystem", "Polar ecosystem", ["ecosystem"], "P1", None),
        ("soil-ecosystem", "Soil ecosystem", ["ecosystem"], "P1", None),
        ("microbial-ecosystem", "Microbial ecosystem", ["ecosystem", "microbiome"], "P1", None),
        ("island-ecosystem", "Island ecosystem", ["ecosystem"], "P1", None),
        ("pollination-network", "Pollination network", ["food-web"], "P1", None),
        ("seed-dispersal-network", "Seed dispersal network", [], "P1", None),
        ("parasite-host-network", "Parasite-host network", ["food-web"], "P1", None),
        ("predator-prey-network", "Predator-prey network", ["food-web"], "P1", None),
        ("invasive-species-system", "Invasive species system", [], "P1", None),
        ("keystone-species-system", "Keystone species system", ["keystone-species-system"], "P1", None),
        ("trophic-cascade-system", "Trophic cascade system", ["food-web"], "P1", None),
        ("succession-system", "Succession system", [], "P1", None),
        ("fisheries-system", "Fisheries system", ["ecosystem"], "P1", None),
        ("agricultural-ecosystem", "Agricultural ecosystem", ["ecosystem"], "P2", None),
        ("urban-ecosystem", "Urban ecosystem", ["ecosystem"], "P2", None),
        ("managed-forest", "Managed forest", ["forest-biome"], "P2", None),
        ("conservation-reserve-network", "Conservation reserve network", [], "P2", None),
        ("ecological-restoration-system", "Ecological restoration system", [], "P2", None),
    ],
)


# ----- §9 Collective animal systems -----
SECTION_9 = dict(
    section="9",
    domain="biological",
    default_kind="class",
    entries=[
        ("bee-colony", "Bee colony", ["superorganism"], "P0", None),
        ("termite-colony", "Termite colony", ["superorganism"], "P0", None),
        ("wasp-colony", "Wasp colony", ["superorganism"], "P1", None),
        ("flocking-birds", "Flocking birds", ["animal-collective"], "P1", None),
        ("schooling-fish", "Schooling fish", ["animal-collective"], "P1", None),
        ("herding-mammals", "Herding mammals", ["animal-collective"], "P1", None),
        ("primate-troop", "Primate troop", ["animal-collective"], "P1", None),
        ("wolf-pack", "Wolf pack", ["animal-collective"], "P1", None),
        ("elephant-herd", "Elephant herd", ["animal-collective"], "P1", None),
        ("cetacean-pod", "Cetacean pod", ["animal-collective"], "P1", None),
        ("migratory-swarm", "Migratory swarm", ["animal-collective"], "P1", None),
        ("locust-swarm", "Locust swarm", ["animal-collective"], "P1", None),
        ("social-insect-nest-architecture", "Social insect nest architecture", ["superorganism"], "P1", None),
        ("collective-foraging-system", "Collective foraging system", ["animal-collective"], "P1", None),
        ("collective-predator-avoidance", "Collective predator avoidance system", ["animal-collective"], "P1", None),
        ("animal-migration-network", "Animal migration network", [], "P2", None),
        ("animal-communication-system", "Animal communication system", [], "P2", None),
        ("cooperative-breeding-system", "Cooperative breeding system", [], "P2", None),
    ],
)


# ----- §10 Cognitive, neural, psychological -----
SECTION_10 = dict(
    section="10",
    domain="cognitive",
    default_kind="class",
    entries=[
        ("cognitive-system", "Mind / cognition", ["cognitive-system"], "P0", None),
        ("language-cognition", "Language cognition system", ["cognitive-system", "language-system"], "P0", None),
        ("attention-system", "Attention system", ["cognitive-system"], "P1", None),
        ("memory-system", "Memory system", ["cognitive-system"], "P1", None),
        ("perception-system", "Perception system", ["cognitive-system"], "P1", None),
        ("motor-control-system", "Motor control system", ["cognitive-system"], "P1", None),
        ("emotion-regulation-system", "Emotion regulation system", ["cognitive-system"], "P1", None),
        ("decision-making-system", "Decision-making system", ["cognitive-system"], "P1", None),
        ("learning-system", "Learning system", ["cognitive-system"], "P1", None),
        ("consciousness-system", "Consciousness as a system-level phenomenon", ["cognitive-system"], "P1", None),
        ("dreaming-system", "Dreaming system", ["cognitive-system"], "P1", None),
        ("social-cognition", "Social cognition", ["cognitive-system"], "P1", None),
        ("theory-of-mind", "Theory of mind", ["cognitive-system"], "P1", None),
        ("collective-attention", "Collective attention", ["collective-intelligence-system"], "P1", None),
        ("group-decision-making", "Group decision-making", ["collective-intelligence-system"], "P1", None),
        ("distributed-cognition", "Distributed cognition", ["collective-intelligence-system"], "P1", None),
        ("human-ai-cognitive-coupling", "Human-AI cognitive coupling", ["collective-intelligence-system", "ai-system"], "P2", None),
        ("online-collective-intelligence", "Online collective intelligence", ["collective-intelligence-system"], "P2", None),
        ("expertise-formation-system", "Expertise formation system", [], "P2", None),
        ("addiction-system", "Addiction system", [], "P2", None),
        ("mental-health-system", "Mental health system", [], "P2", None),
        ("belief-formation-system", "Belief formation system", ["belief-network"], "P2", None),
    ],
)


# ----- §11 Language, culture, symbolic -----
SECTION_11 = dict(
    section="11",
    domain="cognitive",
    default_kind="class",
    entries=[
        ("culture", "Culture", ["cultural-system"], "P0", None),
        ("symbolic-communication", "Symbolic communication", ["language-system"], "P0", None),
        ("writing-system", "Writing system", ["cultural-system", "language-system"], "P1", None),
        ("oral-tradition", "Oral tradition", ["cultural-system"], "P1", None),
        ("myth-system", "Myth system", ["cultural-system"], "P1", None),
        ("religion-system", "Religion", ["cultural-system"], "P1", None),
        ("ritual-system", "Ritual system", ["cultural-system"], "P1", None),
        ("philosophy-system", "Philosophy", ["cultural-system", "knowledge-system"], "P1", None),
        ("science-system", "Science", ["knowledge-system"], "P1", None),
        ("mathematics-system", "Mathematics", ["knowledge-system"], "P1", None),
        ("legal-codes", "Legal codes", ["legal-system"], "P1", None),
        ("moral-system", "Moral system", ["cultural-system"], "P1", None),
        ("norm-system", "Norm system", ["cultural-system"], "P1", None),
        ("aesthetic-system", "Aesthetic system", ["cultural-system"], "P1", None),
        ("music-tradition", "Music tradition", ["cultural-system"], "P1", None),
        ("art-movement", "Art movement", ["cultural-system"], "P1", None),
        ("education-system", "Education system", ["cultural-system", "knowledge-system"], "P1", None),
        ("knowledge-transmission-system", "Knowledge transmission system", ["knowledge-system"], "P1", None),
        ("memetic-system", "Memetic system", ["cultural-system"], "P1", None),
        ("fashion-system", "Fashion system", ["cultural-system"], "P1", None),
        ("cuisine-system", "Cuisine system", ["cultural-system"], "P1", None),
        ("sports-culture", "Sports culture", ["cultural-system"], "P1", None),
        ("internet-meme-ecosystem", "Internet meme ecosystem", ["cultural-system", "information-ecosystem"], "P2", None),
        ("fan-community", "Fan community", ["cultural-system"], "P2", None),
        ("open-knowledge-community", "Open knowledge community", ["knowledge-system"], "P2", None),
        ("standards-body", "Standards body", ["governance-system"], "P2", None),
        ("academic-discipline", "Academic discipline", ["knowledge-system"], "P2", None),
        ("scientific-paradigm", "Scientific paradigm", ["knowledge-system"], "P2", None),
        ("conspiracy-belief-network", "Conspiracy belief network", ["belief-network"], "P2", None),
        ("ideological-movement", "Ideological movement", ["cultural-system", "belief-network"], "P2", None),
    ],
)


# ----- §12 Human social -----
SECTION_12 = dict(
    section="12",
    domain="social",
    default_kind="class",
    entries=[
        ("human-society", "Human society", [], "P0", None),
        ("civilization", "Civilization", ["civilization"], "P0", None),
        ("institution", "Institution", ["bureaucratic-organization", "governance-system"], "P0", None),
        ("family-system", "Family system", ["kinship-system"], "P1", None),
        ("kinship-network", "Kinship network", ["kinship-system"], "P1", None),
        ("tribe-band-society", "Tribe / band society", [], "P1", None),
        ("village", "Village", ["city"], "P1", None),
        ("neighborhood", "Neighborhood", ["city"], "P1", None),
        ("city-state", "City-state", ["city", "civilization"], "P1", None),
        ("nation-state", "Nation-state", ["governance-system", "civilization"], "P1", None),
        ("empire", "Empire", ["civilization", "governance-system"], "P1", None),
        ("diaspora-network", "Diaspora network", ["social-network"], "P1", None),
        ("social-class-system", "Social class system", [], "P1", None),
        ("caste-system", "Caste system", [], "P1", None),
        ("ethnic-group-system", "Ethnic group system", [], "P1", None),
        ("religious-community", "Religious community", ["cultural-system"], "P1", None),
        ("political-party", "Political party", ["governance-system"], "P1", None),
        ("social-movement", "Social movement", ["social-network"], "P1", None),
        ("bureaucracy", "Bureaucracy", ["bureaucratic-organization"], "P1", None),
        ("corporation", "Corporation", ["firm"], "P1", None),
        ("labor-union", "Labor union", [], "P1", None),
        ("university", "University", ["knowledge-system"], "P1", None),
        ("hospital-system", "Hospital system", ["healthcare-system"], "P1", None),
        ("criminal-justice-system", "Criminal justice system", ["legal-system"], "P1", None),
        ("military-organization", "Military organization", ["bureaucratic-organization", "conflict-system"], "P1", None),
        ("intelligence-agency", "Intelligence agency", ["bureaucratic-organization"], "P1", None),
        ("ngo-network", "NGO network", ["social-network"], "P1", None),
        ("philanthropic-ecosystem", "Philanthropic ecosystem", [], "P1", None),
        ("online-community", "Online community", ["social-network", "information-ecosystem"], "P2", None),
        ("multiplayer-gaming-community", "Multiplayer gaming community", ["social-network"], "P2", None),
        ("remote-work-organization", "Remote-work organization", ["bureaucratic-organization"], "P2", None),
        ("creator-economy-community", "Creator economy community", ["social-network", "information-ecosystem"], "P2", None),
        ("startup-ecosystem", "Startup ecosystem", ["firm"], "P2", None),
        ("standards-setting-community", "Standards-setting community", ["governance-system"], "P2", None),
        ("professional-network", "Professional network", ["social-network"], "P2", None),
    ],
)


# ----- §13 Governance, law, political -----
SECTION_13 = dict(
    section="13",
    domain="social",
    default_kind="class",
    entries=[
        ("governance-system", "Governance system", ["governance-system"], "P0", None),
        ("legal-system", "Legal system", ["legal-system"], "P0", None),
        ("state-system", "State system", ["government", "governance-system"], "P0", None),
        ("democracy", "Democracy", ["government", "governance-system"], "P1", None),
        ("autocracy", "Autocracy", ["government", "governance-system"], "P1", None),
        ("federal-system", "Federal system", ["government"], "P1", None),
        ("polycentric-governance", "Polycentric governance system", ["governance-system"], "P1", None),
        ("international-law-system", "International law system", ["legal-system"], "P1", None),
        ("treaty-system", "Treaty system", [], "P1", None),
        ("regulatory-system", "Regulatory system", ["governance-system"], "P1", None),
        ("tax-system", "Tax system", [], "P1", None),
        ("public-administration", "Public administration", ["bureaucratic-organization"], "P1", None),
        ("electoral-system", "Electoral system", ["governance-system"], "P1", None),
        ("judicial-system", "Judicial system", ["legal-system"], "P1", None),
        ("policing-system", "Policing system", ["legal-system"], "P1", None),
        ("prison-system", "Prison system", ["legal-system"], "P1", None),
        ("welfare-state", "Welfare state", ["government"], "P1", None),
        ("public-health-governance", "Public health governance", ["healthcare-system", "governance-system"], "P1", None),
        ("disaster-response-governance", "Disaster response governance", ["governance-system"], "P1", None),
        ("climate-governance", "Climate governance", ["governance-system"], "P1", None),
        ("internet-governance", "Internet governance", ["governance-system"], "P1", None),
        ("financial-regulation", "Financial regulation", ["governance-system"], "P1", None),
        ("commons-governance", "Commons governance", ["governance-system"], "P1", None),
        ("platform-governance", "Platform governance", ["governance-system"], "P2", None),
        ("dao-governance", "DAO governance", ["governance-system"], "P2", None),
        ("ai-governance", "AI governance system", ["governance-system", "ai-system"], "P2", None),
        ("cybersecurity-governance", "Cybersecurity governance", ["governance-system", "cybersecurity-system"], "P2", None),
        ("science-policy-interface", "Science-policy interface", ["governance-system", "knowledge-system"], "P2", None),
        ("geopolitical-alliance", "Geopolitical alliance system", ["conflict-system"], "P2", None),
        ("sanctions-regime", "Sanctions regime", [], "P2", None),
    ],
)


# ----- §14 Economic, financial -----
SECTION_14 = dict(
    section="14",
    domain="economic",
    default_kind="class",
    entries=[
        ("economy", "Economy", [], "P0", None),
        ("money-system", "Money system", ["monetary-system"], "P0", None),
        ("trade-network", "Trade network", ["trade-network"], "P0", None),
        ("stock-market", "Stock market", ["market-exchange", "financial-system"], "P1", None),
        ("bond-market", "Bond market", ["market-exchange", "financial-system"], "P1", None),
        ("banking-system", "Banking system", ["financial-system"], "P1", None),
        ("central-banking-system", "Central banking system", ["financial-system", "monetary-system"], "P1", None),
        ("credit-system", "Credit system", ["financial-system"], "P1", None),
        ("insurance-system", "Insurance system", ["financial-system"], "P1", None),
        ("labor-market", "Labor market", ["market-exchange"], "P1", None),
        ("housing-market", "Housing market", ["market-exchange"], "P1", None),
        ("commodity-market", "Commodity market", ["market-exchange"], "P1", None),
        ("energy-market", "Energy market", ["market-exchange"], "P1", None),
        ("supply-chain", "Supply chain", ["supply-chain"], "P1", None),
        ("global-logistics", "Global logistics system", ["supply-chain"], "P1", None),
        ("firm-ecosystem", "Firm ecosystem", ["firm"], "P1", None),
        ("industrial-cluster", "Industrial cluster", [], "P1", None),
        ("innovation-ecosystem", "Innovation ecosystem", [], "P1", None),
        ("startup-funding-ecosystem", "Startup funding ecosystem", [], "P1", None),
        ("venture-capital-system", "Venture capital system", ["financial-system"], "P1", None),
        ("auction-system", "Auction system", ["market-exchange"], "P1", None),
        ("pricing-system", "Pricing system", [], "P1", None),
        ("informal-economy", "Informal economy", [], "P1", None),
        ("black-market", "Black market", ["market-exchange"], "P1", None),
        ("platform-marketplace", "Platform marketplace", ["market-exchange", "information-ecosystem"], "P2", None),
        ("cryptocurrency-ecosystem", "Cryptocurrency ecosystem", ["financial-system"], "P2", None),
        ("decentralized-finance", "Decentralized finance system", ["financial-system"], "P2", None),
        ("gig-economy", "Gig economy", [], "P2", None),
        ("creator-economy", "Creator economy", ["information-ecosystem"], "P2", None),
        ("advertising-market", "Advertising market", ["information-ecosystem"], "P2", None),
        ("attention-economy", "Attention economy", ["information-ecosystem"], "P2", None),
        ("prediction-market", "Prediction market", ["market-exchange"], "P2", None),
        ("carbon-market", "Carbon market", ["market-exchange"], "P2", None),
    ],
)


# ----- §15 Infrastructure -----
SECTION_15 = dict(
    section="15",
    domain="technological",
    default_kind="class",
    entries=[
        ("infrastructure-system", "Infrastructure system", [], "P0", None),
        ("transportation-network", "Transportation network", ["transportation-network"], "P0", None),
        ("communication-network", "Communication network", ["communication-network"], "P0", None),
        ("road-network", "Road network", ["transportation-network"], "P1", None),
        ("rail-network", "Rail network", ["transportation-network"], "P1", None),
        ("air-traffic-system", "Air traffic system", ["transportation-network"], "P1", None),
        ("maritime-shipping-system", "Maritime shipping system", ["transportation-network"], "P1", None),
        ("port-system", "Port system", ["transportation-network"], "P1", None),
        ("airport-system", "Airport system", ["transportation-network"], "P1", None),
        ("public-transit-system", "Public transit system", ["transportation-network"], "P1", None),
        ("water-supply-system", "Water supply system", ["water-supply-system"], "P1", None),
        ("wastewater-system", "Wastewater system", ["water-supply-system"], "P1", None),
        ("waste-management-system", "Waste management system", [], "P1", None),
        ("electrical-distribution-grid", "Electrical distribution grid", ["power-grid"], "P1", None),
        ("natural-gas-network", "Natural gas network", [], "P1", None),
        ("oil-pipeline-network", "Oil pipeline network", [], "P1", None),
        ("renewable-energy-grid", "Renewable energy grid", ["power-grid"], "P1", None),
        ("battery-storage-network", "Battery storage network", [], "P1", None),
        ("food-distribution-system", "Food distribution system", ["supply-chain"], "P1", None),
        ("cold-chain-logistics", "Cold chain logistics", ["supply-chain"], "P1", None),
        ("emergency-response-system", "Emergency response system", [], "P1", None),
        ("healthcare-delivery-system", "Healthcare delivery system", ["healthcare-system"], "P1", None),
        ("hospital-network", "Hospital network", ["healthcare-system"], "P1", None),
        ("manufacturing-system", "Manufacturing system", ["industrial-system"], "P1", None),
        ("construction-ecosystem", "Construction ecosystem", [], "P1", None),
        ("space-launch-ecosystem", "Space launch ecosystem", [], "P1", None),
        ("smart-grid", "Smart grid", ["power-grid"], "P2", None),
        ("autonomous-vehicle-traffic", "Autonomous vehicle traffic system", ["transportation-network", "ai-system"], "P2", None),
        ("drone-logistics", "Drone logistics system", ["transportation-network"], "P2", None),
        ("satellite-constellation", "Satellite constellation", ["communication-network"], "P2", None),
        ("sensor-network", "Sensor network", [], "P2", None),
        ("iot-system", "Internet-of-things system", ["distributed-software-system"], "P2", None),
        ("smart-city", "Smart city", ["city"], "P2", None),
    ],
)


# ----- §16 Software, digital, internet -----
SECTION_16 = dict(
    section="16",
    domain="technological",
    default_kind="class",
    entries=[
        ("world-wide-web", "World Wide Web", ["internet-system", "information-ecosystem"], "P0", None),
        ("software-ecosystem", "Software ecosystem", ["software-ecosystem"], "P0", None),
        ("operating-system", "Operating system", ["distributed-software-system"], "P1", None),
        ("large-codebase", "Large codebase", ["software-ecosystem"], "P1", None),
        ("distributed-system", "Distributed system", ["distributed-software-system"], "P1", None),
        ("cloud-computing-platform", "Cloud computing platform", ["distributed-software-system"], "P1", None),
        ("data-center", "Data center", ["distributed-software-system"], "P1", None),
        ("database-system", "Database system", ["distributed-software-system"], "P1", None),
        ("search-engine", "Search engine", ["distributed-software-system", "information-ecosystem"], "P1", None),
        ("social-media-platform", "Social media platform", ["information-ecosystem"], "P1", None),
        ("recommender-system", "Recommender system", ["ai-system", "information-ecosystem"], "P1", None),
        ("version-control-ecosystem", "Version-control ecosystem", ["software-ecosystem"], "P1", None),
        ("package-manager-ecosystem", "Package manager ecosystem", ["software-ecosystem"], "P1", None),
        ("programming-language-ecosystem", "Programming language ecosystem", ["software-ecosystem", "language-system"], "P1", None),
        ("api-ecosystem", "API ecosystem", ["software-ecosystem", "protocol-stack"], "P1", None),
        ("microservice-architecture", "Microservice architecture", ["distributed-software-system"], "P1", None),
        ("kubernetes-ecosystem", "Kubernetes ecosystem", ["distributed-software-system"], "P1", None),
        ("ci-cd-pipeline", "CI/CD pipeline", ["software-ecosystem"], "P1", None),
        ("cybersecurity-ecosystem", "Cybersecurity ecosystem", ["cybersecurity-system"], "P1", None),
        ("malware-ecosystem", "Malware ecosystem", ["cybersecurity-system"], "P1", None),
        ("botnet", "Botnet", ["cybersecurity-system"], "P1", None),
        ("spam-ecosystem", "Spam ecosystem", ["information-ecosystem"], "P1", None),
        ("content-moderation-system", "Content moderation system", ["information-ecosystem", "governance-system"], "P1", None),
        ("online-advertising-system", "Online advertising system", ["information-ecosystem"], "P1", None),
        ("streaming-platform-ecosystem", "Streaming platform ecosystem", ["information-ecosystem"], "P1", None),
        ("multiplayer-game-ecosystem", "Multiplayer game ecosystem", ["distributed-software-system"], "P1", None),
        ("blockchain-network", "Blockchain network", ["distributed-software-system"], "P2", None),
        ("smart-contract-ecosystem", "Smart contract ecosystem", ["distributed-software-system"], "P2", None),
        ("dao", "Decentralized autonomous organization", ["governance-system", "distributed-software-system"], "P2", None),
        ("federated-social-network", "Federated social network", ["information-ecosystem"], "P2", None),
        ("data-marketplace", "Data marketplace", ["market-exchange"], "P2", None),
        ("digital-identity-system", "Digital identity system", [], "P2", None),
        ("observability-system", "Cloud-native observability system", ["distributed-software-system"], "P2", None),
        ("devops-organization", "DevOps organization", ["bureaucratic-organization", "software-ecosystem"], "P2", None),
        ("legacy-software-maintenance", "Legacy software maintenance system", ["software-ecosystem"], "P2", None),
        ("technical-debt-system", "Technical debt accumulation system", ["software-ecosystem"], "P2", None),
    ],
)


# ----- §17 AI and Human-AI -----
SECTION_17 = dict(
    section="17",
    domain="computational",
    default_kind="class",
    entries=[
        ("ml-model-lifecycle", "Machine learning model lifecycle", ["ai-system"], "P0", None),
        ("neural-network-training", "Neural network training system", ["ai-system", "artificial-neural-network"], "P1", None),
        ("foundation-model-ecosystem", "Foundation model ecosystem", ["ai-system"], "P1", None),
        ("llm-deployment-ecosystem", "LLM deployment ecosystem", ["ai-system"], "P1", None),
        ("human-feedback-system", "Human feedback system", ["ai-system"], "P1", None),
        ("reinforcement-learning-system", "Reinforcement learning system", ["ai-system"], "P1", None),
        ("multi-agent-ai-system", "Multi-agent AI system", ["multi-agent-ai-system", "ai-system"], "P1", None),
        ("ai-toolchain-ecosystem", "AI toolchain ecosystem", ["software-ecosystem", "ai-system"], "P1", None),
        ("model-evaluation-ecosystem", "Model evaluation ecosystem", ["ai-system"], "P1", None),
        ("ai-safety-governance", "AI safety governance system", ["ai-system", "governance-system"], "P1", None),
        ("ai-software-development-system", "AI-assisted software development system", ["ai-system", "software-ecosystem"], "P1", None),
        ("rag-system", "Retrieval-augmented generation system", ["ai-system"], "P1", None),
        ("agentic-workflow-system", "Agentic workflow system", ["multi-agent-ai-system"], "P1", None),
        ("synthetic-data-ecosystem", "Synthetic data ecosystem", ["ai-system"], "P1", None),
        ("ai-benchmark-ecosystem", "AI benchmark ecosystem", ["ai-system"], "P1", None),
        ("ai-misinformation-system", "AI-enabled misinformation system", ["ai-system", "information-ecosystem"], "P1", None),
        ("human-ai-collaboration", "Human-AI collaboration system", ["multi-agent-ai-system", "collective-intelligence-system"], "P1", None),
        ("autonomous-lab-system", "Autonomous lab system", ["ai-system", "knowledge-system"], "P2", None),
        ("ai-scientific-discovery-system", "AI-mediated scientific discovery system", ["ai-system", "knowledge-system"], "P2", None),
        ("ai-tutor-ecosystem", "AI tutor ecosystem", ["ai-system"], "P2", None),
        ("ai-customer-support-ecosystem", "AI customer-support ecosystem", ["ai-system"], "P2", None),
        ("ai-coding-assistant-ecosystem", "AI coding assistant ecosystem", ["ai-system"], "P2", None),
        ("model-supply-chain", "AI model supply chain", ["ai-system", "supply-chain"], "P2", None),
        ("compute-market-for-ai", "Compute market for AI", ["market-exchange"], "P2", None),
        ("gpu-cluster-operations", "GPU cluster operations system", ["distributed-software-system"], "P2", None),
    ],
)


# ----- §18 Knowledge, science, innovation -----
SECTION_18 = dict(
    section="18",
    domain="cognitive",
    default_kind="class",
    entries=[
        ("technological-innovation-system", "Technological innovation system", ["knowledge-system"], "P0", None),
        ("research-community", "Research community", ["knowledge-system"], "P1", None),
        ("peer-review-system", "Peer review system", ["knowledge-system"], "P1", None),
        ("academic-publishing-system", "Academic publishing system", ["knowledge-system"], "P1", None),
        ("citation-network", "Citation network", ["knowledge-system", "social-network"], "P1", None),
        ("laboratory-ecosystem", "Laboratory ecosystem", ["knowledge-system"], "P1", None),
        ("university-system", "University system", ["knowledge-system"], "P1", None),
        ("scientific-instrumentation-ecosystem", "Scientific instrumentation ecosystem", ["knowledge-system"], "P1", None),
        ("standards-ecosystem", "Standards ecosystem", ["governance-system"], "P1", None),
        ("patent-system", "Patent system", ["legal-system", "knowledge-system"], "P1", None),
        ("rd-pipeline", "R&D pipeline", ["knowledge-system"], "P1", None),
        ("engineering-design-system", "Engineering design system", ["knowledge-system"], "P1", None),
        ("technology-adoption-system", "Technology adoption system", [], "P1", None),
        ("knowledge-graph", "Knowledge graph", ["knowledge-system"], "P1", None),
        ("library-archive-system", "Library / archive system", ["knowledge-system"], "P1", None),
        ("knowledge-commons", "Wikipedia-like knowledge commons", ["knowledge-system"], "P1", None),
        ("open-source-science-ecosystem", "Open-source science ecosystem", ["knowledge-system"], "P1", None),
        ("reproducibility-crisis-system", "Reproducibility crisis as a system", ["knowledge-system"], "P2", None),
        ("scientific-fraud-detection-system", "Scientific fraud detection system", ["knowledge-system"], "P2", None),
        ("grant-funding-ecosystem", "Grant funding ecosystem", ["knowledge-system", "financial-system"], "P2", None),
        ("interdisciplinary-field-formation", "Interdisciplinary field formation", ["knowledge-system"], "P2", None),
        ("paradigm-shift-system", "Paradigm shift system", ["knowledge-system"], "P2", None),
        ("educational-credentialing-system", "Educational credentialing system", ["knowledge-system"], "P2", None),
    ],
)


# ----- §19 Health, medicine, epidemiological -----
SECTION_19 = dict(
    section="19",
    domain="biological",  # mostly biological/medical; some healthcare-system entries are social
    default_kind="class",
    entries=[
        ("epidemic-system", "Epidemic / pandemic system", ["epidemic-system", "contagion-system"], "P0", None),
        ("healthcare-system", "Healthcare system", ["healthcare-system"], "P0", None),
        ("disease-transmission-network", "Disease transmission network", ["contagion-system", "epidemic-system"], "P1", None),
        ("public-health-system", "Public health system", ["healthcare-system", "governance-system"], "P1", None),
        ("vaccination-system", "Vaccination system", ["healthcare-system", "immune-system"], "P1", None),
        ("pharmaceutical-development-system", "Pharmaceutical development system", ["healthcare-system"], "P1", None),
        ("clinical-trial-ecosystem", "Clinical trial ecosystem", ["healthcare-system"], "P1", None),
        ("health-insurance-system", "Health insurance system", ["healthcare-system", "financial-system"], "P1", None),
        ("mental-health-care-system", "Mental health care system", ["healthcare-system"], "P1", None),
        ("chronic-disease-management-system", "Chronic disease management system", ["healthcare-system"], "P1", None),
        ("antimicrobial-resistance-system", "Antimicrobial resistance system", ["evolutionary-system"], "P1", None),
        ("cancer-ecology-system", "Cancer ecology / evolution system", ["cancer-system", "evolutionary-system"], "P1", None),
        ("nutrition-system", "Nutrition system", [], "P1", None),
        ("aging-population-system", "Aging population system", [], "P1", None),
        ("medical-misinformation-system", "Medical misinformation system", ["information-ecosystem"], "P2", None),
        ("telemedicine-ecosystem", "Telemedicine ecosystem", ["healthcare-system"], "P2", None),
        ("personalized-medicine-ecosystem", "Personalized medicine ecosystem", ["healthcare-system"], "P2", None),
        ("hospital-supply-chain", "Hospital supply chain", ["supply-chain", "healthcare-system"], "P2", None),
        ("global-disease-surveillance", "Global disease surveillance system", ["epidemic-system", "healthcare-system"], "P2", None),
        ("one-health-system", "One Health human-animal-environment disease system", ["epidemic-system"], "P2", None),
    ],
)


# ----- §20 Media, information, attention -----
SECTION_20 = dict(
    section="20",
    domain="social",
    default_kind="class",
    entries=[
        ("information-ecosystem", "Information ecosystem", ["information-ecosystem"], "P0", None),
        ("news-media-system", "News media system", ["information-ecosystem"], "P1", None),
        ("social-media-information-flow", "Social media information flow", ["information-ecosystem", "contagion-system"], "P1", None),
        ("search-ranking-ecosystem", "Search ranking ecosystem", ["information-ecosystem", "ai-system"], "P1", None),
        ("recommendation-ecosystem", "Recommendation ecosystem", ["information-ecosystem", "ai-system"], "P1", None),
        ("advertising-ecosystem", "Advertising ecosystem", ["information-ecosystem"], "P1", None),
        ("propaganda-system", "Propaganda system", ["information-ecosystem"], "P1", None),
        ("rumor-spreading-system", "Rumor-spreading system", ["contagion-system"], "P1", None),
        ("misinformation-system", "Misinformation / disinformation system", ["information-ecosystem", "contagion-system"], "P1", None),
        ("public-opinion-formation", "Public opinion formation", ["belief-network"], "P1", None),
        ("collective-attention-cycles", "Collective attention cycles", ["information-ecosystem"], "P1", None),
        ("virality-system", "Virality system", ["contagion-system"], "P1", None),
        ("meme-ecosystem", "Meme ecosystem", ["cultural-system", "information-ecosystem"], "P1", None),
        ("influencer-network", "Influencer network", ["social-network", "information-ecosystem"], "P1", None),
        ("journalism-ecosystem", "Journalism ecosystem", ["information-ecosystem"], "P1", None),
        ("book-publishing-ecosystem", "Book publishing ecosystem", ["information-ecosystem"], "P1", None),
        ("film-tv-ecosystem", "Film/television ecosystem", ["information-ecosystem"], "P1", None),
        ("generative-media-ecosystem", "Generative media ecosystem", ["information-ecosystem", "ai-system"], "P2", None),
        ("synthetic-content-ecosystem", "Synthetic-content ecosystem", ["information-ecosystem", "ai-system"], "P2", None),
        ("online-radicalization-system", "Online radicalization system", ["information-ecosystem", "belief-network"], "P2", None),
        ("algorithmic-amplification-system", "Algorithmic amplification system", ["information-ecosystem", "ai-system"], "P2", None),
    ],
)


# ----- §21 Security, conflict, adversarial -----
SECTION_21 = dict(
    section="21",
    domain="social",
    default_kind="class",
    entries=[
        ("war-system", "War system", ["conflict-system"], "P0", None),
        ("security-ecosystem", "Security ecosystem", ["cybersecurity-system", "conflict-system"], "P0", None),
        ("arms-race", "Arms race", ["conflict-system", "coevolutionary-system"], "P1", None),
        ("military-command-system", "Military command system", ["bureaucratic-organization", "conflict-system"], "P1", None),
        ("insurgency-counterinsurgency", "Insurgency / counterinsurgency system", ["conflict-system"], "P1", None),
        ("terrorism-counterterrorism", "Terrorism / counterterrorism system", ["conflict-system"], "P1", None),
        ("cybersecurity-attack-defense", "Cybersecurity attack-defense system", ["cybersecurity-system", "conflict-system"], "P1", None),
        ("intelligence-ecosystem", "Intelligence ecosystem", [], "P1", None),
        ("espionage-network", "Espionage network", [], "P1", None),
        ("geopolitical-conflict-system", "Geopolitical conflict system", ["conflict-system"], "P1", None),
        ("nuclear-deterrence-system", "Nuclear deterrence system", ["conflict-system"], "P1", None),
        ("border-control-system", "Border-control system", [], "P1", None),
        ("criminal-network", "Criminal network", ["social-network"], "P1", None),
        ("organized-crime-ecosystem", "Organized crime ecosystem", [], "P1", None),
        ("money-laundering-network", "Money-laundering network", ["financial-system"], "P1", None),
        ("fraud-ecosystem", "Fraud ecosystem", ["financial-system"], "P1", None),
        ("botnet-warfare-system", "Botnet warfare system", ["cybersecurity-system"], "P2", None),
        ("information-warfare-system", "Information warfare system", ["information-ecosystem", "conflict-system"], "P2", None),
        ("sanctions-evasion-system", "Sanctions-evasion system", [], "P2", None),
        ("supply-chain-attack-system", "Supply-chain attack system", ["supply-chain", "cybersecurity-system"], "P2", None),
        ("ai-cyber-conflict-system", "AI-enabled cyber conflict system", ["ai-system", "cybersecurity-system"], "P2", None),
    ],
)


# ----- §22 Urban systems -----
SECTION_22 = dict(
    section="22",
    domain="social",
    default_kind="class",
    entries=[
        ("urbanization-system", "Urbanization system", ["city"], "P0", None),
        ("metropolitan-region", "Metropolitan region", ["city"], "P1", None),
        ("neighborhood-system", "Neighborhood system", ["city"], "P1", None),
        ("housing-system", "Housing system", ["city"], "P1", None),
        ("zoning-planning-system", "Zoning / planning system", ["governance-system"], "P1", None),
        ("urban-transportation-system", "Urban transportation system", ["transportation-network", "city"], "P1", None),
        ("urban-water-system", "Urban water system", ["water-supply-system", "city"], "P1", None),
        ("urban-energy-system", "Urban energy system", ["power-grid", "city"], "P1", None),
        ("urban-food-system", "Urban food system", ["supply-chain", "city"], "P1", None),
        ("informal-settlement", "Informal settlement", ["city"], "P1", None),
        ("real-estate-development-ecosystem", "Real estate development ecosystem", [], "P1", None),
        ("public-space-usage-system", "Public space usage system", ["city"], "P1", None),
        ("urban-crime-system", "Urban crime system", ["city", "social-network"], "P1", None),
        ("urban-economic-agglomeration", "Urban economic agglomeration", ["city"], "P1", None),
        ("gentrification-system", "Gentrification system", ["city"], "P1", None),
        ("migration-to-city-system", "Migration-to-city system", ["city"], "P1", None),
        ("urban-resilience-system", "Urban resilience system", ["city"], "P1", None),
        ("megacity", "Megacity", ["city"], "P2", None),
        ("city-region-supply-chain", "City-region supply chain", ["supply-chain", "city"], "P2", None),
        ("urban-climate-adaptation-system", "Urban climate adaptation system", ["city"], "P2", None),
        ("urban-digital-twin", "Urban digital twin", ["city", "ai-system"], "P2", None),
    ],
)


# ----- §23 Global human-Earth -----
SECTION_23 = dict(
    section="23",
    domain="ecological",  # most are coupled human-Earth, span ecological+social
    default_kind="class",
    entries=[
        ("global-civilization", "Global civilization", ["civilization"], "P0", None),
        ("global-climate-human-system", "Global climate-human system", ["earth-system", "climate-system"], "P0", None),
        ("global-food-system", "Global food system", ["supply-chain"], "P1", None),
        ("global-energy-system", "Global energy system", ["power-grid"], "P1", None),
        ("global-financial-system", "Global financial system", ["financial-system"], "P1", None),
        ("global-trade-system", "Global trade system", ["trade-network"], "P1", None),
        ("global-migration-system", "Global migration system", [], "P1", None),
        ("global-public-health-system", "Global public health system", ["healthcare-system", "governance-system"], "P1", None),
        ("global-scientific-community", "Global scientific community", ["knowledge-system"], "P1", None),
        ("global-internet-ecosystem", "Global internet ecosystem", ["internet-system"], "P1", None),
        ("global-governance-system", "Global governance system", ["governance-system"], "P1", None),
        ("global-supply-chain-system", "Global supply-chain system", ["supply-chain"], "P1", None),
        ("global-inequality-system", "Global inequality system", [], "P1", None),
        ("global-education-system", "Global education system", ["knowledge-system"], "P1", None),
        ("global-risk-system", "Global risk system", [], "P1", None),
        ("planetary-boundaries-system", "Planetary boundaries system", ["planetary-boundary-system"], "P1", None),
        ("energy-transition-system", "Energy transition system", ["power-grid"], "P2", None),
        ("climate-adaptation-system", "Climate adaptation system", ["climate-system"], "P2", None),
        ("carbon-accounting-system", "Carbon accounting system", [], "P2", None),
        ("global-ai-governance-system", "Global AI governance system", ["governance-system", "ai-system"], "P2", None),
        ("space-economy-ecosystem", "Space economy ecosystem", [], "P2", None),
        ("disaster-risk-reduction-system", "Disaster-risk reduction system", ["governance-system"], "P2", None),
    ],
)
SECTION_23_DOMAIN_BY_SLUG: dict[str, str] = {
    "global-civilization": "social",
    "global-climate-human-system": "ecological",
    "global-food-system": "economic",
    "global-energy-system": "technological",
    "global-financial-system": "economic",
    "global-trade-system": "economic",
    "global-migration-system": "social",
    "global-public-health-system": "social",
    "global-scientific-community": "cognitive",
    "global-internet-ecosystem": "technological",
    "global-governance-system": "social",
    "global-supply-chain-system": "economic",
    "global-inequality-system": "social",
    "global-education-system": "social",
    "global-risk-system": "social",
    "planetary-boundaries-system": "ecological",
    "energy-transition-system": "technological",
    "climate-adaptation-system": "ecological",
    "carbon-accounting-system": "economic",
    "global-ai-governance-system": "computational",
    "space-economy-ecosystem": "technological",
    "disaster-risk-reduction-system": "social",
}


# ----- §24 Abstract / model systems -----
SECTION_24 = dict(
    section="24",
    domain="computational",
    default_kind="model",
    entries=[
        ("cellular-automaton", "Cellular automata", ["cellular-automaton"], "P3", None),
        ("game-of-life", "Conway's Game of Life", ["cellular-automaton"], "P3", None),
        ("ising-model", "Ising model", ["ising-model"], "P3", None),
        ("potts-model", "Potts model", ["ising-model"], "P3", None),
        ("sandpile-model", "Sandpile model", ["self-organized-critical-system"], "P3", None),
        ("percolation-model", "Percolation model", [], "P3", None),
        ("random-graph-model", "Random graph", ["random-graph"], "P3", None),
        ("small-world-network", "Small-world network", ["random-graph"], "P3", None),
        ("scale-free-network", "Scale-free network", ["random-graph"], "P3", None),
        ("preferential-attachment-model", "Preferential attachment model", ["random-graph"], "P3", None),
        ("kuramoto-model", "Kuramoto oscillator model", ["kuramoto-oscillator"], "P3", None),
        ("lorenz-system", "Lorenz system", ["lorenz-system"], "P3", None),
        ("logistic-map", "Logistic map", ["lorenz-system"], "P3", None),
        ("reaction-diffusion-model", "Reaction-diffusion model", ["chemical-reaction-network"], "P3", None),
        ("turing-pattern-system", "Turing pattern system", [], "P3", None),
        ("schelling-segregation-model", "Schelling segregation model", ["agent-based-model"], "P3", None),
        ("boids-model", "Boids / flocking model", ["agent-based-model"], "P3", None),
        ("sugarscape-model", "Sugarscape", ["agent-based-model"], "P3", None),
        ("nk-fitness-landscape", "NK fitness landscape", ["evolutionary-system"], "P3", None),
        ("prisoners-dilemma-network", "Prisoner's dilemma network", ["agent-based-model"], "P3", None),
        ("evolutionary-game-system", "Evolutionary game system", ["evolutionary-system"], "P3", None),
        ("voter-model", "Voter model", ["agent-based-model"], "P3", None),
        ("sir-model", "Epidemic SIR/SEIR model", ["contagion-system"], "P3", None),
        ("lotka-volterra-model", "Predator-prey Lotka-Volterra model", ["food-web"], "P3", None),
        ("agent-based-market-model", "Agent-based market model", ["agent-based-model", "market-exchange"], "P3", None),
        ("queueing-network", "Queueing network", [], "P3", None),
        ("network-cascade-model", "Network cascade model", ["contagion-system"], "P3", None),
        ("diffusion-of-innovation-model", "Diffusion-of-innovation model", ["contagion-system"], "P3", None),
        ("threshold-contagion-model", "Threshold contagion model", ["contagion-system"], "P3", None),
        ("system-dynamics-stock-flow-model", "System dynamics stock-flow model", [], "P3", None),
    ],
)


# ----- §25 Boundary / control cases -----
# Most entries already covered in v0.1; add the missing ones.
SECTION_25 = dict(
    section="25",
    domain="physical",
    default_kind="boundary_case",
    entries=[
        ("two-body-orbital", "Two-body orbital system", ["stellar-system"], "C", None),
        ("perfect-crystal", "Perfect crystal", ["crystal-lattice"], "C", None),
        ("single-purpose-machine", "Single-purpose machine", ["clockwork-mechanism"], "C", None),
        ("static-hierarchy", "Static hierarchy", ["bureaucratic-organization"], "C", None),
        ("purely-random-graph", "Purely random graph", ["random-graph"], "C", None),
        ("fully-connected-graph", "Fully connected graph", ["random-graph"], "C", None),
        ("tree-hierarchy", "Tree hierarchy", [], "C", None),
        ("single-agent-optimization-problem", "Single-agent optimization problem", ["agent-based-model"], "C", None),
        ("closed-thermodynamic-equilibrium", "Closed thermodynamic equilibrium system", [], "C", None),
    ],
)
SECTION_25_DOMAIN_BY_SLUG: dict[str, str] = {
    "two-body-orbital": "physical",
    "perfect-crystal": "physical",
    "single-purpose-machine": "technological",
    "static-hierarchy": "social",
    "purely-random-graph": "computational",
    "fully-connected-graph": "computational",
    "tree-hierarchy": "computational",
    "single-agent-optimization-problem": "computational",
    "closed-thermodynamic-equilibrium": "physical",
}


# Master section list
ALL_SECTIONS: list[dict] = [
    SECTION_3,
    SECTION_4_1,
    SECTION_4_2,
    SECTION_5,
    SECTION_6_1,
    SECTION_6_2,
    SECTION_7_1,
    SECTION_7_2,
    SECTION_7_3,
    SECTION_8,
    SECTION_9,
    SECTION_10,
    SECTION_11,
    SECTION_12,
    SECTION_13,
    SECTION_14,
    SECTION_15,
    SECTION_16,
    SECTION_17,
    SECTION_18,
    SECTION_19,
    SECTION_20,
    SECTION_21,
    SECTION_22,
    SECTION_23,
    SECTION_24,
    SECTION_25,
]

# Per-section per-slug domain overrides
PER_SECTION_DOMAIN_OVERRIDES: dict[str, dict[str, str]] = {
    "3": SECTION_3_DOMAIN_BY_SLUG,
    "23": SECTION_23_DOMAIN_BY_SLUG,
    "25": SECTION_25_DOMAIN_BY_SLUG,
}
