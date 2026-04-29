# Prior Art and Comparative Analysis Sources for the Complex Systems Catalog Project

**Prepared:** 2026-04-29  
**Purpose:** Provide a reusable reference list of closely related prior art, data repositories, conceptual frameworks, metric taxonomies, ontologies, and methodological analogs for a project aimed at building a quantitative cross-domain catalog / atlas / “periodic table” of complex systems.

---

## 1. Project Target Being Compared Against

The working project concept:

> Build a comprehensive catalog of complex systems; quantify each system across metrics, attributes, constraints, potentials, relationships, scales, and failure modes; then use the resulting dataset to discover cross-system generalizations, universality classes, tradeoff frontiers, failure-mode families, analogies, gaps, and a possible “periodic table” or latent space of complexity.

The most relevant prior art does **not** appear to be one single equivalent project. Instead, it forms a landscape of partial overlaps:

- **General systems theory** supplies cross-domain conceptual foundations.
- **Emergence / cosmic evolution literature** supplies chronological emergence spines.
- **Complexity-measure surveys** supply metric candidates.
- **Network repositories** supply graph-centric data precedents.
- **Economic-complexity atlases** supply strong latent-space methodology analogs.
- **Universality / scaling / resilience work** supplies examples of cross-system invariants.
- **Model zoos and simulation libraries** supply benchmark model systems.
- **Formal ontologies** supply vocabulary and schema design precedents.
- **Practitioner frameworks** supply intervention and systems-change classifications.

The likely novelty of this project is the **synthesis**: a cross-domain, metric-rich knowledge graph of complex systems, not just a concept encyclopedia, not just a network repository, not just a list of emergence stages, and not just a collection of simulations.

---

## 2. How to Use This Reference

Use this document when asking:

1. **Has someone already tried this?**  
   Compare the project against the closest source clusters below.

2. **Which sources should influence schema design?**  
   Start with Boulding, Miller, Simon, Bar-Yam, BFO, GO, SBO, ICON, KONECT, and the Atlas of Economic Complexity.

3. **Which sources provide actual data?**  
   Start with ICON, KONECT, Network Repository, SNAP, NetLogo, ComSES, and the Atlas of Economic Complexity.

4. **Which sources provide discovery methods?**  
   Start with the Atlas of Economic Complexity, Tempesta/Jensen, Gao/Barzel/Barabási, West, Bar-Yam, and Chaisson.

5. **Which sources are most important for the project’s “periodic table” framing?**  
   Start with Morowitz, Chaisson, Economic Complexity/Product Space, Tempesta/Jensen, and MaRS/OECD’s “Periodic Table of Systems Change” as a terminology/metaphor comparison.

---

## 3. Prior-Art Landscape Summary

| Cluster | Closest sources | What they provide | Main gap relative to this project |
|---|---|---|---|
| General systems taxonomies | Boulding, Miller, Simon | Cross-domain system levels, hierarchy, openness, modularity, matter-energy-information processing | Mostly conceptual; not a metric-rich empirical catalog |
| Emergence / cosmic evolution | Morowitz, Chaisson | Emergence sequence from universe to life/culture; one cross-domain metric candidate | Mostly narrative or single-axis; not many metrics or relationships |
| Complexity metric surveys | Lloyd, Ladyman/Lambert/Wiesner, Bar-Yam | Metric families, feature definitions, scale-dependent complexity | Catalogs measures more than systems |
| Complexity concept references | Complexity Explained, Springer Encyclopedia | Terminology and conceptual coverage | Not structured as quantified system records |
| Network repositories | ICON, KONECT, Network Repository, SNAP | Large collections of graph datasets and network statistics | Graph-centric; limited dynamics, constraints, agency, resources, failure modes |
| Economic complexity | Atlas of Economic Complexity, Product Space, ECI/PCI | Latent capability inference from observed relationships; map-like complexity space | Domain-specific to countries/products/trade |
| Universality/scaling/resilience | Tempesta/Jensen, Gao/Barzel/Barabási, West | Cross-system invariants, universality classes, scaling laws, resilience reductions | Focused on specific mathematical phenomena rather than full system catalog |
| Simulation/model libraries | NetLogo, ComSES, FuturICT / Living Earth Simulator | Model systems, agent-based models, simulation infrastructure ideas | Models are not normalized into cross-domain empirical system ontology |
| Ontologies | BFO, Gene Ontology, Systems Biology Ontology | Controlled vocabulary, hierarchy, semantic annotation practice | Domain-general or biology-specific; not a complex-systems atlas |
| Practitioner frameworks | Cynefin, OECD/MaRS systems-change frameworks | Complexity-aware decision/intervention frameworks | Intervention-oriented; not a catalog of complex systems themselves |

---

## 4. Closest Match by Project Component

| Project component | Closest prior art to compare against | Notes |
|---|---|---|
| Emergence spine | Morowitz; Chaisson | Use to seed foundational systems and temporal emergence transitions |
| System hierarchy | Boulding; Miller; Simon | Use for levels, nesting, near-decomposability, openness, subsystem logic |
| Metric ontology | Lloyd; Ladyman/Lambert/Wiesner; Bar-Yam | Use to avoid collapsing complexity into one score |
| Network data layer | ICON; KONECT; SNAP; Network Repository | Use as graph dataset precedents and potential data sources |
| Latent-space / periodic-table methodology | Atlas of Economic Complexity; Product Space | Strong methodological analog for inferring hidden capabilities/classes from observed data |
| Cross-system invariants | West; Tempesta/Jensen; Gao/Barzel/Barabási | Use for hypotheses about universality classes, scaling laws, resilience patterns |
| Simulation benchmarks | NetLogo; ComSES; FuturICT / Living Earth Simulator | Use for model systems and dynamic process benchmarks |
| Controlled vocabulary | BFO; Gene Ontology; Systems Biology Ontology | Use for schema/ontology design practices |
| Intervention classification | Cynefin; OECD/MaRS systems-change frameworks | Use for governance/intervention/failure-response modules |

---

## 5. Source Register

### A. General Systems Theory and Cross-Domain System Taxonomies

#### S01 — Kenneth E. Boulding, “General Systems Theory—The Skeleton of Science”

- **Author:** Kenneth E. Boulding  
- **Year:** 1956  
- **Type:** Foundational paper  
- **Category:** General systems theory  
- **Source:** [INFORMS / Management Science](https://pubsonline.informs.org/doi/10.1287/mnsc.2.3.197)  
- **Also indexed at:** [JSTOR](https://www.jstor.org/stable/2627132)

**Why it matters:**  
Boulding is an early attempt to organize systems thinking across disciplines without replacing all special sciences. This is directly relevant to the project’s ambition to compare systems without flattening them into empty abstractions.

**Compare against this project:**

- Cross-domain scope: **high**
- Quantitative dataset: **low**
- Taxonomic usefulness: **high**
- Direct “periodic table” similarity: **moderate**
- Main reuse: conceptual caution, system levels, scope discipline

---

#### S02 — James Grier Miller, *Living Systems*

- **Author:** James Grier Miller  
- **Year:** 1978  
- **Type:** Book / theory  
- **Category:** Living systems theory  
- **Source:** [Internet Archive bibliographic page](https://archive.org/details/livingsystems0000mill_e7d6)  
- **Bibliographic page:** [Google Books](https://books.google.com/books/about/Living_Systems.html?id=Dbq1e2rmjVAC)  
- **Accessible excerpts/commentary:** [Panarchy.org](https://www.panarchy.org/miller/livingsystems.html), [CoEvolving](https://coevolving.com/blogs/a-general-theory-of-living-systems-james-grier-miller/)

**Why it matters:**  
Miller’s Living Systems Theory describes living systems across nested levels such as cell, organ, organism, group, organization, society, and supranational system, using recurring matter-energy and information-processing subsystems.

**Compare against this project:**

- Cross-scale system hierarchy: **very high**
- Subsystem ontology relevance: **very high**
- Quantified comparative dataset: **low**
- Main reuse: nested levels, subsystem patterns, matter-energy-information schema

---

#### S03 — Herbert A. Simon, “The Architecture of Complexity”

- **Author:** Herbert A. Simon  
- **Year:** 1962  
- **Type:** Foundational paper  
- **Category:** Hierarchy, modularity, near-decomposability  
- **Source:** [PDF copy](https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/ArchitectureOfComplexity.HSimon1962.pdf)  
- **Publisher/index:** [Springer chapter page](https://link.springer.com/chapter/10.1007/978-1-4899-0718-9_31)

**Why it matters:**  
Simon’s ideas of hierarchy, stable intermediate forms, and near-decomposability are central to comparing complex systems across biology, organizations, cities, software, infrastructure, and institutions.

**Compare against this project:**

- Metric relevance: hierarchy depth, modularity, decomposability, subsystem coupling
- Direct data layer: **low**
- Conceptual relevance: **very high**
- Main reuse: structural metrics and evolution of complex architectures

---

### B. Emergence, Cosmic Evolution, and Complexity Spines

#### S04 — Harold J. Morowitz, *The Emergence of Everything: How the World Became Complex*

- **Author:** Harold J. Morowitz  
- **Year:** 2002  
- **Type:** Book  
- **Category:** Emergence sequence / big-history complexity  
- **Official source:** [Oxford University Press](https://global.oup.com/academic/product/the-emergence-of-everything-9780195173314)  
- **Accessible copy found during research:** [PDF copy](https://sackett.net/EmergenceOfEverything.pdf)

**Why it matters:**  
Morowitz provides a chronological emergence spine from the early universe through stars, chemistry, planets, life, humans, language, agriculture, cities, philosophy, and meaning-making. It is one of the closest conceptual seed lists for the project’s foundational catalog.

**Compare against this project:**

- Candidate-system seed value: **very high**
- Quantitative metric coverage: **low**
- Scope overlap: **high**
- Main reuse: P0 emergence anchors and foundational system list

---

#### S05 — Eric J. Chaisson, energy rate density / cosmic evolution work

- **Author:** Eric J. Chaisson  
- **Key paper:** “Energy Rate Density as a Complexity Metric and Evolutionary Driver”  
- **Year:** 2010 / 2011  
- **Type:** Paper / metric proposal  
- **Category:** Cross-domain complexity metric  
- **Source:** [Wiley page](https://onlinelibrary.wiley.com/doi/10.1002/cplx.20323)  
- **Accessible PDF copy:** [PDF copy](https://pdodds.w3.uvm.edu/files/papers/others/2010/chaisson2010a.pdf)  
- **Related:** [Harvard DASH entry for follow-up paper](https://dash.harvard.edu/entities/publication/73120379-1f2a-6bd4-e053-0100007fdf3b)

**Why it matters:**  
Chaisson is one of the clearest attempts to compare galaxies, stars, planets, life, society, and machines with a single cross-domain metric: energy rate density.

**Compare against this project:**

- Cross-domain quantification: **very high**
- Metric breadth: **low** because it is intentionally single-axis
- Main reuse: baseline cross-domain metric and cautionary comparison against one-number complexity

---

### C. Complexity Metric Taxonomies and Definitions

#### S06 — Seth Lloyd, “Measures of Complexity: A Nonexhaustive List”

- **Author:** Seth Lloyd  
- **Year:** 2001  
- **Type:** Survey / metric taxonomy  
- **Category:** Complexity measures  
- **Source:** [MIT PDF](https://web.mit.edu/esd.83/www/notebook/Complexity.PDF)  
- **Alternate PDF:** [UC Davis PDF](https://csc.ucdavis.edu/~cmg/Group/readings/SL-MeasOfComplexity.pdf)

**Why it matters:**  
Lloyd’s list makes clear that “complexity” has many measures and that the multiplicity of measures can be productive rather than merely confusing.

**Compare against this project:**

- Metric ontology relevance: **very high**
- System catalog relevance: **moderate**
- Main reuse: metric families, terminology, and justification for multi-axis complexity profiles

---

#### S07 — James Ladyman, James Lambert, and Karoline Wiesner, “What is a Complex System?”

- **Authors:** James Ladyman, James Lambert, Karoline Wiesner  
- **Year:** 2012 / 2013  
- **Type:** Paper / definition analysis  
- **Category:** Complex-system definition and features  
- **Source:** [PhilSci Archive PDF](https://philsci-archive.pitt.edu/9044/4/LLWultimate.pdf)  
- **Related book sample:** [Karoline Wiesner PDF sample](https://www.karowiesner.org/uploads/7/2/9/8/72983511/what_is_a_complex_system_reading_sample_1.pdf)

**Why it matters:**  
This is a rigorous analysis of what properties are associated with complex systems, including emergence, self-organization, nonlinearity, feedback, history, memory, modularity, robustness, and adaptation.

**Compare against this project:**

- Definition/boundary value: **very high**
- Metric candidate value: **high**
- Data layer: **low**
- Main reuse: inclusion criteria and top-level metric categories

---

#### S08 — Yaneer Bar-Yam / multiscale complexity profile work

- **Authors:** Yaneer Bar-Yam and collaborators  
- **Key ideas:** Complexity profile, scale-dependent complexity, multiscale information theory  
- **Type:** Theory / metric framework  
- **Category:** Scale-dependent complexity  
- **Source:** [NECSI page on multiscale information theory](https://necsi.edu/multiscale-information-theory-and-the-marginal-utility-of-information)  
- **Related formal paper:** [Siegenfeld & Bar-Yam, “A Formal Definition of Scale-dependent Complexity and the Multi-scale Law of Requisite Variety”](https://arxiv.org/abs/2206.04896)

**Why it matters:**  
This work treats complexity as scale-dependent rather than as a single scalar. That maps directly to project metrics such as natural modeling scale, coarse-grainability, hierarchy, cross-scale coupling, and environment-system requisite variety.

**Compare against this project:**

- Multiscale metric relevance: **very high**
- Schema relevance: **high**
- Main reuse: scale profiles, multi-scale law of requisite variety, tradeoff between fine-scale and large-scale complexity

---

### D. Complexity Concept Repositories and Encyclopedias

#### S09 — Complexity Explained

- **Project:** Complexity Explained  
- **Type:** Collaborative educational reference  
- **Category:** Complexity concepts / vocabulary  
- **Source:** [Complexity Explained](https://complexityexplained.github.io/)

**Why it matters:**  
This project explains core ideas such as interactions, emergence, self-organization, dynamics, adaptation, and complex-systems methods in an accessible, organized form.

**Compare against this project:**

- Controlled vocabulary value: **high**
- Data/metric layer: **low**
- Main reuse: concept definitions and user-facing explanatory language

---

#### S10 — *Encyclopedia of Complexity and Systems Science*

- **Editor:** Robert A. Meyers  
- **First edition:** 2009  
- **Type:** Encyclopedia / reference work  
- **Category:** Broad complexity science reference  
- **Source:** [Springer](https://link.springer.com/book/10.1007/978-0-387-30440-3)

**Why it matters:**  
This is a broad reference for complexity theory, tools, measures, applications, and system classes across science and engineering.

**Compare against this project:**

- Terminology and bibliography value: **very high**
- Structured dataset value: **low**
- Main reuse: source mining, concept coverage validation, bibliographic expansion

---

### E. Network Science Datasets and Repositories

#### S11 — ICON: Colorado Index of Complex Networks

- **Project:** Colorado Index of Complex Networks  
- **Type:** Network dataset index  
- **Category:** Network science data repository  
- **Source:** [ICON](https://icon.colorado.edu/)  
- **About page:** [ICON About](https://icon.colorado.edu/aboutus)

**Why it matters:**  
ICON indexes research-quality network datasets across domains of network science. It is one of the closest existing data-layer precedents, but it is network-first rather than full-system-first.

**Compare against this project:**

- Data-source value: **very high**
- Cross-domain value: **high**
- Non-network system attributes: **low**
- Main reuse: graph datasets, graph taxonomy, benchmark network examples

---

#### S12 — KONECT: Koblenz Network Collection

- **Project:** KONECT  
- **Type:** Network dataset collection and analysis platform  
- **Category:** Network science repository  
- **Source:** [KONECT](https://konect.cc/)  
- **Paper:** [KONECT: The Koblenz Network Collection](https://dl.acm.org/doi/10.1145/2487788.2488173)  
- **Registry entry:** [re3data KONECT entry](https://www.re3data.org/repository/r3d100011612)

**Why it matters:**  
KONECT collects network datasets, analyzes them, and makes analyses available online. It provides a useful precedent for standardized network records and automated statistics.

**Compare against this project:**

- Data-source value: **very high**
- Automated-analysis precedent: **high**
- Complex-system ontology breadth: **low to moderate**
- Main reuse: network data ingestion, standardized graph metrics, dataset metadata practices

---

#### S13 — Network Repository

- **Project:** Network Repository  
- **Type:** Interactive network and graph data repository  
- **Category:** Graph data and analytics  
- **Source:** [Network Repository](https://networkrepository.com/)  
- **Data listing:** [Network Repository data page](https://networkrepository.com/network-data.php)  
- **Paper:** [The Network Data Repository with Interactive Graph Analytics and Visualization](https://ojs.aaai.org/index.php/AAAI/article/download/9277/9136)

**Why it matters:**  
Network Repository provides real-world graph datasets, benchmark graphs, interactive visualization, and graph analytics.

**Compare against this project:**

- Data-source value: **very high**
- Interactive analytic precedent: **high**
- Full complex-system attributes: **low**
- Main reuse: graph data platform patterns, interactive exploration ideas

---

#### S14 — SNAP: Stanford Large Network Dataset Collection

- **Project:** Stanford Network Analysis Project / SNAP  
- **Type:** Network dataset collection and tools  
- **Category:** Large-scale network data  
- **Source:** [SNAP data collection](https://snap.stanford.edu/data/)  
- **Main project:** [SNAP](https://snap.stanford.edu/)  
- **Paper:** [SNAP: A General Purpose Network Analysis and Graph Mining Library](https://arxiv.org/abs/1606.07550)

**Why it matters:**  
SNAP provides large real-world networks across social, web, road, internet, citation, collaboration, and communication domains.

**Compare against this project:**

- Network benchmark value: **very high**
- Cross-domain network coverage: **high**
- System-level attributes beyond graph structure: **low**
- Main reuse: canonical network datasets and graph analytics tooling

---

### F. Economic Complexity and Latent-Space Methodology

#### S15 — Atlas of Economic Complexity

- **Project:** The Atlas of Economic Complexity  
- **Institution:** Harvard Growth Lab  
- **Type:** Data atlas / latent capability mapping  
- **Category:** Economic complexity  
- **Source:** [Atlas of Economic Complexity](https://atlas.hks.harvard.edu/)  
- **Country rankings:** [Economic Complexity rankings](https://atlas.hks.harvard.edu/rankings)  
- **Product rankings:** [Product Complexity rankings](https://atlas.hks.harvard.edu/rankings/product)  
- **Book:** [The Atlas of Economic Complexity, MIT Press](https://direct.mit.edu/books/oa-monograph/3014/The-Atlas-of-Economic-ComplexityMapping-Paths-to)

**Why it matters:**  
This is one of the strongest methodological analogs. It infers hidden productive capabilities from observed country-product relationships and represents economic systems in a map-like latent space.

**Compare against this project:**

- Latent-space methodology: **very high**
- Cross-system analogy value: **very high**
- Domain breadth: **limited to economic/product space**
- Main reuse: embedding methods, diversity/ubiquity logic, capability inference, nearest-neighbor and opportunity-space framing

---

#### S16 — Product Space / Hidalgo-Hausmann economic complexity work

- **Key authors:** César Hidalgo, Ricardo Hausmann, collaborators  
- **Type:** Research program  
- **Category:** Latent capability inference / product relatedness  
- **Source:** [Atlas background PDF](https://oec.world/pdf/AtlasOfEconomicComplexity_Part_I.pdf)

**Why it matters:**  
The product-space idea is methodologically similar to what a “complex systems space” might become: a map where proximity reflects shared hidden requirements, capabilities, constraints, or transition paths.

**Compare against this project:**

- Methodological analogy: **very high**
- Direct complex-systems coverage: **moderate**
- Main reuse: latent relatedness graph, capability inference, pathway prediction, opportunity frontiers

---

### G. Universality, Scaling, and Resilience Patterns

#### S17 — Piergiulio Tempesta and Henrik Jeldtoft Jensen, universality classes and information-theoretic measures

- **Authors:** Piergiulio Tempesta, Henrik Jeldtoft Jensen  
- **Year:** 2020  
- **Type:** Research article  
- **Category:** Universality classes / information theory  
- **Source:** [Scientific Reports](https://www.nature.com/articles/s41598-020-60188-y)  
- **Open version:** [PubMed Central](https://pmc.ncbi.nlm.nih.gov/articles/PMC7136250/)  
- **Preprint:** [arXiv](https://arxiv.org/abs/1903.07698)

**Why it matters:**  
This work explicitly connects complex-system universality classes to phase-space growth rates and information-theoretic measures.

**Compare against this project:**

- Universality-class relevance: **very high**
- Metric relevance: **high**
- Catalog/data layer: **low**
- Main reuse: mathematical hypotheses for grouping systems by state-space growth and entropy class

---

#### S18 — Jianxi Gao, Baruch Barzel, and Albert-László Barabási, “Universal Resilience Patterns in Complex Networks”

- **Authors:** Jianxi Gao, Baruch Barzel, Albert-László Barabási  
- **Year:** 2016  
- **Type:** Research article  
- **Category:** Network resilience / universal reduction  
- **Source:** [PubMed](https://pubmed.ncbi.nlm.nih.gov/26887493/)  
- **PDF copy:** [Barabási Lab PDF](https://barabasi.com/media/pub_imports/files/687.pdf)  
- **Publication record:** [CEU research record](https://research.ceu.edu/en/publications/universal-resilience-patterns-in-complex-networks/)

**Why it matters:**  
This work tries to extract universal resilience behavior from heterogeneous complex networks by reducing high-dimensional dynamics to lower-dimensional resilience patterns.

**Compare against this project:**

- Resilience metric relevance: **very high**
- Cross-domain reduction precedent: **very high**
- Full catalog scope: **moderate**
- Main reuse: resilience metric design, network-dynamics reduction, cross-system response curves

---

#### S19 — Geoffrey West / scaling laws across organisms, cities, economies, and companies

- **Author:** Geoffrey West and collaborators  
- **Key book:** *Scale: The Universal Laws of Growth, Innovation, Sustainability, and the Pace of Life in Organisms, Cities, Economies, and Companies*  
- **Year:** 2017  
- **Type:** Book / research program  
- **Category:** Cross-system scaling laws  
- **Source:** [Santa Fe Institute overview](https://www.santafe.edu/news-center/news/geoffrey-wests-long-anticipated-book-scale-emerges)  
- **Book page:** [Amazon listing](https://www.amazon.com/Scale-Universal-Innovation-Sustainability-Organisms/dp/1594205582)

**Why it matters:**  
West’s work seeks shared scaling laws across biological and human systems, especially organisms, cities, companies, and economies.

**Compare against this project:**

- Cross-system invariant relevance: **very high**
- Metric relevance: **high**
- Data-catalog scope: **moderate**
- Main reuse: scaling-law hypotheses, allometric comparisons, city/organism/company analogies

---

### H. Model Libraries, Simulation Repositories, and System Zoos

#### S20 — NetLogo Models Library

- **Project:** NetLogo Models Library  
- **Type:** Agent-based model library  
- **Category:** Simulation / model zoo  
- **Source:** [NetLogo Models Library](https://ccl.northwestern.edu/netlogo/models/)  
- **Main site:** [NetLogo](https://www.netlogo.org/)  
- **Related paper:** [Modeling Emergent Phenomena with NetLogo](https://ccl.northwestern.edu/papers/MEE/)

**Why it matters:**  
NetLogo provides a large library of agent-based models for emergence, ecology, markets, social systems, networks, segregation, epidemics, and other complex-system patterns.

**Compare against this project:**

- Model-system seed value: **very high**
- Empirical-system catalog value: **moderate**
- Main reuse: benchmark model entries, simulated dynamics, toy-system comparison cases

---

#### S21 — CoMSES Net Computational Model Library

- **Project:** CoMSES Net  
- **Type:** Computational model repository/community  
- **Category:** Agent-based and individual-based models  
- **Source:** [CoMSES Net](https://www.comses.net/)  
- **Model library:** [Computational Model Library](https://www.comses.net/codebases/)

**Why it matters:**  
CoMSES maintains a curated computational model library and emphasizes discoverability, reusability, reproducibility, and metadata for computational models.

**Compare against this project:**

- Model metadata precedent: **very high**
- Data/model reuse: **high**
- Full cross-domain empirical catalog: **moderate**
- Main reuse: model metadata, reproducibility practices, computational system records

---

#### S22 — FuturICT / Living Earth Simulator

- **Project:** FuturICT / Living Earth Simulator  
- **Type:** Proposed large-scale simulation and data infrastructure  
- **Category:** Planetary socio-technical simulation  
- **Source:** [FuturICT Flagship Pilot Project](https://www.sciencedirect.com/science/article/pii/S187705091100679X)  
- **PDF copy:** [FuturICT paper PDF](https://pdodds.w3.uvm.edu/teaching/courses/2009-08UVM-300/docs/others/2011/simini2011a.pdf)  
- **Related preprint:** [FuturICT — New Science and Technology to Manage Our Complex World](https://arxiv.org/pdf/1108.6131)

**Why it matters:**  
FuturICT aimed to integrate ICT, complexity science, social science, big data, simulation, visualization, and participatory platforms to understand global techno-socio-economic systems.

**Compare against this project:**

- Ambition/scope similarity: **high**
- Dataset/schema similarity: **moderate**
- Implementation similarity: **low to moderate**
- Main reuse: cautionary example, planetary-scale integration goals, socio-technical simulation framing

---

### I. Ontologies and Controlled Vocabularies

#### S23 — Basic Formal Ontology (BFO)

- **Project:** Basic Formal Ontology  
- **Type:** Upper ontology  
- **Category:** Ontology / information integration  
- **Source:** [BFO official site](https://bfo-ontology.github.io/)  
- **Paper:** [BFO: Basic Formal Ontology](https://journals.sagepub.com/doi/abs/10.3233/AO-220262)  
- **GitHub:** [BFO GitHub](https://github.com/bfo-ontology/bfo)

**Why it matters:**  
BFO is a domain-general upper ontology designed for information retrieval, analysis, and integration across scientific and other domains.

**Compare against this project:**

- Ontology architecture relevance: **very high**
- Domain-specific metric content: **low**
- Main reuse: upper ontology discipline, continuants/processes distinction, interoperability practices

---

#### S24 — Gene Ontology (GO)

- **Project:** Gene Ontology  
- **Type:** Biological ontology / knowledgebase  
- **Category:** Controlled vocabulary and annotation practice  
- **Source:** [Gene Ontology Resource](https://geneontology.org/)  
- **Ontology documentation:** [GO ontology documentation](https://geneontology.org/docs/ontology-documentation/)  
- **GO annotations:** [GO annotation documentation](https://geneontology.org/docs/go-annotations/)

**Why it matters:**  
GO is a mature example of a disciplined, machine-readable ontology with three major aspects: molecular function, cellular component, and biological process.

**Compare against this project:**

- Ontology practice relevance: **very high**
- Direct domain coverage: **limited to biology**
- Main reuse: annotation model, controlled vocabulary governance, aspect-based classification

---

#### S25 — Systems Biology Ontology (SBO)

- **Project:** Systems Biology Ontology  
- **Type:** Controlled relational vocabulary  
- **Category:** Systems-biology modeling ontology  
- **Source:** [NCBO BioPortal SBO entry](https://bioportal.bioontology.org/ontologies/SBO)  
- **GitHub:** [EBI-BioModels/SBO](https://github.com/EBI-BioModels/SBO)  
- **FAIRsharing entry:** [SBO FAIRsharing](https://fairsharing.org/1156)

**Why it matters:**  
SBO provides semantic terms for systems-biology models, including participant roles, quantitative parameters, mathematical expressions, modeling frameworks, and model metadata.

**Compare against this project:**

- Modeling ontology relevance: **high**
- Systems-biology relevance: **very high**
- Cross-domain coverage: **moderate to low**
- Main reuse: semantic annotation of models, parameter vocabularies, interaction terms

---

### J. Practitioner Frameworks, Decision Contexts, and Systems Change

#### S26 — Cynefin Framework

- **Creator:** Dave Snowden / The Cynefin Company  
- **Type:** Sense-making and decision framework  
- **Category:** Complex vs complicated decision contexts  
- **Official source:** [Cynefin Framework overview](https://thecynefin.co/about-us/about-cynefin-framework/)  
- **Main site:** [The Cynefin Company](https://thecynefin.co/)

**Why it matters:**  
Cynefin distinguishes decision contexts such as clear, complicated, complex, chaotic, and confusion/disorder. It is useful for boundary cases and for separating complex systems from merely complicated ones.

**Compare against this project:**

- Classification relevance: **high**
- Quantitative metric layer: **low**
- Intervention relevance: **high**
- Main reuse: complexity/complicated distinction, intervention logic, decision-context tags

---

#### S27 — OECD / MaRS Solutions Lab, “Periodic Table of Systems Change”

- **Project/source:** OECD report referencing MaRS Solutions Lab’s “Periodic Table of Systems Change”  
- **Type:** Public-sector systems-change framework  
- **Category:** Systems-change interventions  
- **Source:** [OECD report PDF](https://oecd-opsi.org/wp-content/uploads/2018/07/Systems-Approaches-to-Public-Sector-Challenges_Working-with-Change.pdf)  
- **OECD publication page:** [Systems Approaches to Public Sector Challenges](https://www.oecd.org/en/publications/systems-approaches-to-public-sector-challenges_9789264279865-en.html)  
- **OPSI page:** [OECD OPSI publication page](https://oecd-opsi.org/publications/systems-approaches/)

**Why it matters:**  
This is not a periodic table of complex systems. It is a periodic-table-style framework for systems-change methods, including capacity building, solution design, and policy making.

**Compare against this project:**

- “Periodic table” terminology comparison: **high**
- Intervention framework relevance: **high**
- Direct system catalog relevance: **low**
- Main reuse: naming caution, intervention vocabulary, public-sector systems-change methods

---

## 6. Comparison Rubric for Future Sources

When evaluating a new prior-art candidate, score it against these dimensions.

| Dimension | Question | Score guide |
|---|---|---|
| Scope | Does it compare systems across many domains? | 0 = single domain; 5 = broad cross-domain |
| Unit of analysis | Does it treat whole systems as comparable records? | 0 = no; 5 = yes |
| Metric richness | Does it quantify multiple attributes, not just one? | 0 = no metrics; 5 = broad metric ontology |
| System relationships | Does it model nesting, dependency, similarity, ancestry, analogy, or interaction among systems? | 0 = no; 5 = rich graph/ontology |
| Dynamics | Does it capture time, feedback, state transitions, adaptation, or failure? | 0 = static only; 5 = rich dynamics |
| Constraints | Does it capture constraints, resources, boundaries, or feasible state space? | 0 = no; 5 = central focus |
| Data availability | Are reusable datasets or structured records available? | 0 = no; 5 = downloadable / API / well-documented |
| Discovery method | Does it support discovery of classes, invariants, gaps, or tradeoffs? | 0 = no; 5 = yes, explicitly |
| Ontology quality | Does it define a clean vocabulary/schema? | 0 = no; 5 = formal ontology / controlled vocabulary |
| Relevance to periodic-table goal | Could it help build a latent complexity space or classification table? | 0 = no; 5 = directly |

Suggested output format:

```yaml
source_id:
title:
authors_or_project:
year_or_status:
source_type:
url:
cluster:
summary:
closest_project_component:
reusable_assets:
comparison_scores:
  scope:
  unit_of_analysis:
  metric_richness:
  system_relationships:
  dynamics:
  constraints:
  data_availability:
  discovery_method:
  ontology_quality:
  periodic_table_relevance:
main_gap:
notes:
```

---

## 7. High-Priority Sources to Review First

If time is limited, start with these:

1. **Morowitz — *The Emergence of Everything***  
   Best seed for the project’s foundational emergence catalog.

2. **Miller — *Living Systems***  
   Best precedent for recurring cross-scale subsystems in living/social systems.

3. **Simon — “The Architecture of Complexity”**  
   Best foundation for hierarchy, modularity, and near-decomposability.

4. **Lloyd — “Measures of Complexity”**  
   Best compact starting point for metric multiplicity.

5. **Bar-Yam / scale-dependent complexity profile**  
   Best foundation for multiscale complexity and requisite variety.

6. **ICON / KONECT / SNAP / Network Repository**  
   Best practical data sources for graph/network aspects.

7. **Atlas of Economic Complexity / Product Space**  
   Best methodological analog for latent complexity-space discovery.

8. **Tempesta/Jensen — universality classes**  
   Best mathematical analog for complexity-class discovery.

9. **Gao/Barzel/Barabási — universal resilience patterns**  
   Best example of cross-system resilience reduction.

10. **BFO / GO / SBO**  
   Best references for building a disciplined ontology and annotation model.

---

## 8. What Seems Novel About the Proposed Project

The likely novel contribution is not any single ingredient. It is the combination:

```text
complex systems catalog
+ metric ontology
+ system-of-systems relationships
+ constraints/resources/failure modes
+ scale-dependent descriptions
+ evidence/provenance metadata
+ latent embedding / periodic-table analysis
+ cross-domain discovery of classes, gaps, tradeoffs, and invariants
```

Existing sources cover pieces of this:

- Boulding/Miller/Simon: conceptual systems skeleton.
- Morowitz/Chaisson: emergence spine and single cross-domain metric.
- Lloyd/Ladyman/Bar-Yam: metric and definition landscape.
- ICON/KONECT/SNAP/Network Repository: network datasets.
- Atlas of Economic Complexity: latent relatedness/capability map.
- Tempesta/Gao/West: examples of universality, resilience, and scaling patterns.
- NetLogo/ComSES: computational model zoo.
- BFO/GO/SBO: ontology discipline.
- Cynefin/OECD/MaRS: intervention and systems-change framing.

The proposed project would be closer to:

> **An Atlas of Complex Systems: a metric-rich, cross-domain knowledge graph for discovering universality classes, tradeoff frontiers, failure-mode families, evolutionary pathways, analogies, and gaps in complex-system space.**

---

## 9. Suggested Next-Step Deliverables

When this project reaches implementation planning, this prior-art list can support:

1. **Prior-art comparison matrix**  
   Score each source with the rubric in Section 6.

2. **Schema influence map**  
   Map each source to candidate schema fields.

3. **Data-source ingestion plan**  
   Identify which network/model repositories can seed early records.

4. **Metric-source mapping**  
   Link metric categories to Lloyd, Bar-Yam, Chaisson, Gao/Barabási, West, and network-science repositories.

5. **Ontology design pass**  
   Compare proposed classes and relations against BFO/GO/SBO practices.

6. **Novelty statement**  
   Use this document to clearly explain how the project differs from prior work.

---

## 10. Compact Bibliography / Source List

### General systems and hierarchy

- Boulding, Kenneth E. “General Systems Theory—The Skeleton of Science.” *Management Science*, 1956.  
  https://pubsonline.informs.org/doi/10.1287/mnsc.2.3.197

- Miller, James Grier. *Living Systems*. McGraw-Hill, 1978.  
  https://archive.org/details/livingsystems0000mill_e7d6

- Simon, Herbert A. “The Architecture of Complexity.” *Proceedings of the American Philosophical Society*, 1962.  
  https://faculty.sites.iastate.edu/tesfatsi/archive/tesfatsi/ArchitectureOfComplexity.HSimon1962.pdf

### Emergence and cosmic evolution

- Morowitz, Harold J. *The Emergence of Everything: How the World Became Complex*. Oxford University Press, 2002.  
  https://global.oup.com/academic/product/the-emergence-of-everything-9780195173314

- Chaisson, Eric J. “Energy Rate Density as a Complexity Metric and Evolutionary Driver.” *Complexity*, 2010/2011.  
  https://onlinelibrary.wiley.com/doi/10.1002/cplx.20323

### Complexity definitions and measures

- Lloyd, Seth. “Measures of Complexity: A Nonexhaustive List.” *IEEE Control Systems Magazine*, 2001.  
  https://web.mit.edu/esd.83/www/notebook/Complexity.PDF

- Ladyman, James; Lambert, James; Wiesner, Karoline. “What is a Complex System?” 2012/2013.  
  https://philsci-archive.pitt.edu/9044/4/LLWultimate.pdf

- Bar-Yam, Yaneer. Multiscale information theory / complexity profile work.  
  https://necsi.edu/multiscale-information-theory-and-the-marginal-utility-of-information

- Siegenfeld, Alexander F.; Bar-Yam, Yaneer. “A Formal Definition of Scale-dependent Complexity and the Multi-scale Law of Requisite Variety.”  
  https://arxiv.org/abs/2206.04896

### Concepts and encyclopedias

- Complexity Explained.  
  https://complexityexplained.github.io/

- Meyers, Robert A., ed. *Encyclopedia of Complexity and Systems Science*. Springer, 2009.  
  https://link.springer.com/book/10.1007/978-0-387-30440-3

### Network repositories

- Colorado Index of Complex Networks.  
  https://icon.colorado.edu/

- KONECT: Koblenz Network Collection.  
  https://konect.cc/

- Network Repository.  
  https://networkrepository.com/

- SNAP: Stanford Large Network Dataset Collection.  
  https://snap.stanford.edu/data/

### Economic complexity and latent spaces

- Atlas of Economic Complexity.  
  https://atlas.hks.harvard.edu/

- Product Complexity rankings.  
  https://atlas.hks.harvard.edu/rankings/product

- Hausmann, Ricardo et al. *The Atlas of Economic Complexity*. MIT Press.  
  https://direct.mit.edu/books/oa-monograph/3014/The-Atlas-of-Economic-ComplexityMapping-Paths-to

### Universality, resilience, and scaling

- Tempesta, Piergiulio; Jensen, Henrik Jeldtoft. “Universality Classes and Information-Theoretic Measures of Complexity via Group Entropies.” *Scientific Reports*, 2020.  
  https://www.nature.com/articles/s41598-020-60188-y

- Gao, Jianxi; Barzel, Baruch; Barabási, Albert-László. “Universal Resilience Patterns in Complex Networks.” *Nature*, 2016.  
  https://pubmed.ncbi.nlm.nih.gov/26887493/

- West, Geoffrey. *Scale: The Universal Laws of Growth, Innovation, Sustainability, and the Pace of Life in Organisms, Cities, Economies, and Companies*. 2017.  
  https://www.santafe.edu/news-center/news/geoffrey-wests-long-anticipated-book-scale-emerges

### Model libraries and simulation infrastructures

- NetLogo Models Library.  
  https://ccl.northwestern.edu/netlogo/models/

- NetLogo.  
  https://www.netlogo.org/

- CoMSES Net.  
  https://www.comses.net/

- CoMSES Computational Model Library.  
  https://www.comses.net/codebases/

- FuturICT Flagship Pilot Project.  
  https://www.sciencedirect.com/science/article/pii/S187705091100679X

- FuturICT preprint.  
  https://arxiv.org/pdf/1108.6131

### Ontologies and controlled vocabularies

- Basic Formal Ontology.  
  https://bfo-ontology.github.io/

- Gene Ontology Resource.  
  https://geneontology.org/

- Gene Ontology documentation.  
  https://geneontology.org/docs/ontology-documentation/

- Systems Biology Ontology.  
  https://bioportal.bioontology.org/ontologies/SBO

- EBI-BioModels/SBO GitHub.  
  https://github.com/EBI-BioModels/SBO

### Practitioner frameworks and systems change

- Cynefin Framework.  
  https://thecynefin.co/about-us/about-cynefin-framework/

- OECD. *Systems Approaches to Public Sector Challenges: Working with Change*.  
  https://www.oecd.org/en/publications/systems-approaches-to-public-sector-challenges_9789264279865-en.html

- OECD OPSI PDF including MaRS Solutions Lab “Periodic Table of Systems Change.”  
  https://oecd-opsi.org/wp-content/uploads/2018/07/Systems-Approaches-to-Public-Sector-Challenges_Working-with-Change.pdf
