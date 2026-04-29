# Complex Systems Metric Ontology

**Project:** Periodic Table of Complexity  
**Document type:** Reference / Brainstorming Framework  
**Version:** 0.1  
**Purpose:** Define a comprehensive set of metrics, attributes, constraints, potentials, and relationships for cataloging and comparing complex systems.

---

## 1. Overview

The goal of this document is to provide a structured reference for eventually quantifying complex systems across many dimensions. The intent is not to reduce each system to a single complexity score, but to represent each system as a multi-dimensional profile.

A mature dataset could support discoveries such as:

- universality classes of complex systems
- cross-domain analogies and homologies
- tradeoff frontiers
- failure-mode families
- latent “complexity coordinates”
- structural impossibilities or rare combinations
- system lifecycle patterns
- intervention and control archetypes
- resilience and brittleness signatures
- classifications similar in spirit to a “periodic table” of complex systems

The central design principle:

> A complex system should be represented as a structured, multi-scale, multi-metric object whose behavior depends on components, relationships, constraints, environment, history, and feedback.

---

## 2. Core Representation

A system record might eventually look something like this:

```text
System = {
  identity,
  boundary,
  components,
  relations,
  processes,
  state_variables,
  constraints,
  environment,
  metrics,
  history,
  comparable_systems,
  evidence
}
```

A metric observation should preserve context:

```text
MetricObservation = {
  metric_id,
  value,
  unit,
  normalized_value,
  scale_level,
  temporal_window,
  spatial_scope,
  method,
  data_source,
  confidence,
  uncertainty,
  assumptions,
  applies_to,
  notes
}
```

Important distinction:

```text
unknown ≠ not_applicable ≠ unmeasurable ≠ not_yet_measured
```

This distinction is essential. Otherwise, missing values will become ambiguous and eventually corrupt comparisons.

---

## 3. Identity and Boundary Attributes

These attributes define what the system is and where it begins and ends. They are not necessarily “metrics,” but every later measurement depends on them.

| Attribute | Meaning |
|---|---|
| System name | Canonical name |
| Aliases | Other names |
| Domain | Biology, ecology, software, economics, cognition, infrastructure, society, etc. |
| Substrate | Physical, biological, informational, institutional, energetic, hybrid |
| Origin | Natural, designed, evolved, emergent, hybrid |
| Ontological type | Organism, network, institution, market, ecosystem, machine, protocol, city, culture, etc. |
| Boundary clarity | Crisp, fuzzy, contested, multi-boundary |
| Boundary permeability | Closed, semi-open, highly open |
| Membership dynamics | Fixed, slowly changing, rapidly changing, fluid |
| System age | Time since emergence or construction |
| Lifecycle stage | Formation, growth, maturity, senescence, collapse, renewal |
| Primary function | What it does |
| Stated purpose | What designers or participants say it does |
| Actual function | What it empirically does |
| Observer dependence | Whether the system changes when observed or measured |
| Human involvement | None, indirect, participant, designer, regulator |
| Reflexivity | Whether modeling or predicting the system changes its behavior |

Possible derived attributes:

| Derived attribute | Meaning |
|---|---|
| Boundary ambiguity score | Difficulty of saying what is inside vs outside |
| System artificiality score | Designed ↔ evolved |
| Openness score | Degree of input/output exchange with environment |
| Reflexivity score | Degree to which observation or prediction affects behavior |
| Purpose coherence | Alignment between stated purpose and observed behavior |

---

## 4. Scale and Granularity Metrics

Complex systems are often understandable only at the right scale. A catalog should represent multiple levels of description.

| Metric / Attribute | Meaning |
|---|---|
| Component count | Number of identifiable parts |
| Component type count | Number of distinct component classes |
| Relation count | Number of edges, interactions, or dependencies |
| State variable count | Number of tracked variables |
| Effective dimensionality | Number of dimensions needed to explain system variation |
| Spatial extent | Physical or logical size |
| Temporal extent | Duration over which system persists |
| Characteristic time scale | Typical update, reaction, or turnover time |
| Time-scale diversity | Spread between fastest and slowest relevant processes |
| Scale separation ratio | Macro time scale / micro time scale |
| Hierarchy depth | Number of nested levels |
| Hierarchy breadth | Number of peer units per level |
| Cross-scale coupling | Strength of influence between levels |
| Natural modeling scale | Scale where prediction or control is strongest |
| Coarse-grainability | How well lower-level details compress into higher-level units |
| Emergence level | Micro, meso, macro, or multiscale |
| Macro-causal informativeness | Whether macro descriptions outperform micro descriptions for prediction or intervention |

Potential scale metrics:

```text
scale_count
scale_depth
scale_separation_ratio
cross_scale_feedback_density
macro_predictive_gain
macro_control_gain
coarse_graining_loss
causal_emergence_score
```

---

## 5. Component and Agent Attributes

For systems with agents or heterogeneous components, counting parts is not enough. Components should also be characterized.

| Metric / Attribute | Meaning |
|---|---|
| Agent count | Number of decision-capable entities |
| Agency density | Fraction of components with autonomous action |
| Component heterogeneity | Diversity among component types |
| Functional diversity | Diversity of roles or functions |
| Behavioral diversity | Diversity of behavior patterns |
| Goal diversity | Diversity of objectives |
| Goal alignment | Degree to which agents share objectives |
| Incentive alignment | Whether local incentives support global outcomes |
| Autonomy | Degree of independent action |
| Memory depth | How much history components retain |
| Learning capacity | Whether components update behavior over time |
| Adaptation speed | How quickly components adjust |
| Turnover rate | Replacement rate of components |
| Reproduction / replication rate | Rate of creation of new similar components |
| Mortality / attrition rate | Rate of component disappearance |
| Component substitutability | Whether one component can replace another |
| Keystone component count | Components whose removal has large system effects |
| Specialist/generalist ratio | Narrow-function vs broad-function components |
| Adversarial capacity | Ability of agents to strategically oppose each other |
| Cooperation tendency | Frequency or strength of cooperative behavior |
| Coordination requirement | Amount of coordination needed for function |

Diversity should probably have several subtypes:

```text
taxonomic_diversity
functional_diversity
behavioral_diversity
goal_diversity
resource_diversity
response_diversity
pathway_diversity
```

---

## 6. Network Topology Metrics

Network topology is a natural measurement layer, especially when systems can be represented as graphs.

### 6.1 Basic Graph Structure

| Metric | Meaning |
|---|---|
| Node count | Number of entities |
| Edge count | Number of relationships |
| Edge density | Fraction of possible edges present |
| Directedness | Directed vs undirected |
| Weightedness | Binary vs weighted links |
| Multiplexity | Number of relation types or layers |
| Hyperedge presence | Whether relations connect groups, not just pairs |
| Self-loop frequency | Reflexive interactions |
| Bipartite/multipartite structure | Whether node types form distinct partitions |

### 6.2 Degree and Connectivity

| Metric | Meaning |
|---|---|
| Mean degree | Average number of connections |
| Degree variance | Heterogeneity of connectivity |
| Degree distribution shape | Random, heavy-tailed, scale-free-like, lattice-like, etc. |
| In-degree / out-degree asymmetry | Directional imbalance |
| Hub concentration | Fraction of edges controlled by top nodes |
| Degree centralization | How star-like the network is |
| Assortativity | Whether similar nodes connect to similar nodes |
| Homophily | Attribute-based assortativity |
| Reciprocity | Mutual directed edges |
| Connectivity | Whether the graph remains connected |
| Component count | Number of disconnected subgraphs |
| Giant component fraction | Share of nodes in largest component |
| k-core structure | Dense structural core |
| Rich-club coefficient | Whether hubs connect to each other |

### 6.3 Distance and Reachability

| Metric | Meaning |
|---|---|
| Average path length | Typical number of steps between nodes |
| Diameter | Longest shortest path |
| Radius | Minimum eccentricity |
| Global efficiency | How efficiently information can traverse |
| Local efficiency | Local fault tolerance |
| Reachability ratio | Fraction of node pairs that can influence each other |
| Small-world coefficient | High clustering plus short paths |
| Navigability | Ease of routing without global knowledge |

### 6.4 Clustering and Modularity

| Metric | Meaning |
|---|---|
| Clustering coefficient | Local triangle density |
| Transitivity | Global triangle closure |
| Community count | Number of modules |
| Modularity | Strength of community partition |
| Module size distribution | Balance of modules |
| Inter-module edge fraction | Coupling between modules |
| Intra/inter-module ratio | Modularity strength |
| Boundary node fraction | Nodes connecting modules |
| Overlapping community index | Nodes belonging to multiple modules |
| Modularity stability | Whether modules persist over time |

### 6.5 Motifs and Local Patterns

| Metric | Meaning |
|---|---|
| Motif frequency | Recurring local patterns |
| Feedforward loop count | Common in regulatory systems |
| Feedback loop count | Cyclic regulation |
| Triangle count | Local closure |
| Cycle length distribution | Feedback or recurrence structure |
| Brokerage motifs | Nodes bridging otherwise separate groups |
| Structural hole score | Opportunity or control from bridging gaps |
| Redundancy of paths | Alternative routes between nodes |

---

## 7. Coupling and Dependency Metrics

Topology alone is not enough. The same graph can behave very differently depending on coupling strength, delay, substitutability, and dependency depth.

| Metric / Attribute | Meaning |
|---|---|
| Coupling strength | How strongly components affect each other |
| Coupling density | Fraction of possible influence links that matter dynamically |
| Coupling symmetry | Mutual vs one-way dependence |
| Dependency depth | Longest dependency chain |
| Dependency fan-in | Number of upstream dependencies |
| Dependency fan-out | Number of downstream dependents |
| Critical dependency count | Dependencies whose loss disables function |
| Substitutability | Availability of alternatives |
| Interdependence index | Degree of mutual reliance |
| Tight coupling | Low slack, high immediacy |
| Loose coupling | Delayed, buffered, or optional interaction |
| Coupling latency | Delay between cause and effect |
| Coupling volatility | How much links change over time |
| Synchronization tendency | Components moving in phase |
| Cascade potential | Likelihood a local shock spreads |
| Contagion threshold | Shock size needed for propagation |
| Bottleneck severity | Constraint imposed by narrow channels |
| Chokepoint count | Number of critical bottlenecks |

Possible derived metrics:

```text
cascade_risk = coupling_strength × dependency_depth × low_redundancy

brittleness = tight_coupling × low_substitutability × high_load

systemic_importance(node) = downstream_dependence × low_substitutability
```

---

## 8. Dynamical Behavior Metrics

These metrics describe how the system changes over time.

| Metric / Attribute | Meaning |
|---|---|
| State-space size | Number of possible states |
| Occupied state fraction | Fraction of possible states actually visited |
| Transition rate | How quickly states change |
| Transition entropy | Uncertainty of next state |
| Entropy rate | Long-run unpredictability of state sequence |
| Attractor count | Number of stable regimes |
| Basin size distribution | How much state-space flows to each attractor |
| Basin depth | Difficulty of escaping an attractor |
| Regime count | Distinct behavioral modes |
| Regime stability | Persistence of modes |
| Regime-switch frequency | How often modes change |
| Hysteresis | History-dependent state transitions |
| Path dependence | Degree to which history constrains future |
| Nonlinearity | Whether outputs scale non-proportionally with inputs |
| Sensitivity to initial conditions | Chaos-like dependence |
| Lyapunov exponent | Rate of divergence of nearby trajectories |
| Volatility | Variance over time |
| Autocorrelation | Persistence of previous state |
| Periodicity | Repeating cycles |
| Oscillation amplitude | Size of cycles |
| Damping ratio | How quickly disturbances fade |
| Recovery rate | Return speed after perturbation |
| Criticality proximity | Nearness to phase or tipping transition |
| Critical slowing indicators | Slower recovery, rising autocorrelation, rising variance |
| Noise sensitivity | Response to random perturbation |
| Shock amplification | Output disturbance / input disturbance |
| Shock absorption | Fraction of disturbance contained |

---

## 9. Feedback and Control Metrics

Many complex systems are feedback systems. Some are deliberately controlled; others are only indirectly influenced.

| Metric / Attribute | Meaning |
|---|---|
| Positive feedback loop count | Reinforcing loops |
| Negative feedback loop count | Stabilizing loops |
| Feedback loop strength | Gain of feedback |
| Feedback delay | Time lag in feedback |
| Feedback polarity balance | Reinforcing vs balancing dominance |
| Feedback nesting | Feedback loops inside feedback loops |
| Control node count | Nodes capable of influencing system |
| Driver node fraction | Minimum fraction needed to steer dynamics |
| Sensor node fraction | Nodes needed to observe state |
| Control centralization | Concentration of control authority |
| Control energy | Effort required to move system to target state |
| Intervention latency | Time from intervention to effect |
| Intervention reversibility | Whether intervention can be undone |
| Control precision | How accurately state can be targeted |
| Control robustness | Whether control still works under noise or failure |
| Observability | Ability to infer internal state from outputs |
| Legibility | Human interpretability of system state |
| Governance bandwidth | Decision capacity of control layer |
| Control mismatch | Misalignment between controller timescale and system timescale |

---

## 10. Information-Theoretic Metrics

Many complex systems process, store, compress, distort, or transmit information.

| Metric | Meaning |
|---|---|
| Shannon entropy | Uncertainty or diversity of states |
| Conditional entropy | Remaining uncertainty given another variable |
| Mutual information | Shared information between variables |
| Transfer entropy | Directed information flow |
| Entropy rate | Unpredictability over time |
| Active information storage | How much past state helps predict future state |
| Predictive information | Information useful for forecasting |
| KL divergence | Difference between distributions |
| Jensen-Shannon distance | Symmetric distance between probability profiles |
| Algorithmic complexity proxy | Compressibility of system description |
| Minimum description length | Compactness of explanatory model |
| Effective complexity | Structured complexity excluding pure randomness |
| Statistical complexity | Memory needed for optimal prediction |
| Signal-to-noise ratio | Useful signal vs noise |
| Information bottleneck count | Places where information flow is compressed |
| Semantic diversity | Diversity of meanings/messages |
| Information latency | Delay in information propagation |
| Information decay | Loss of useful signal over distance/time |
| Information asymmetry | Unequal access to system state |
| Misinformation vulnerability | Susceptibility to false signals |
| Transparency | Accessibility of true state to observers |
| Compression ratio | Macro model size / micro model size |
| Predictive compression gain | Prediction retained after compression |

---

## 11. Causality and Influence Metrics

These metrics distinguish causal structure from mere correlation.

| Metric / Attribute | Meaning |
|---|---|
| Causal edge count | Confirmed influence links |
| Causal density | Fraction of possible causal links present |
| Causal asymmetry | Directionality of influence |
| Causal depth | Length of causal chains |
| Causal branching factor | Number of downstream effects |
| Causal concentration | Whether few causes dominate |
| Causal redundancy | Multiple causes for same effect |
| Intervention effect size | Change caused by intervention |
| Counterfactual sensitivity | Difference under alternate conditions |
| Granger influence | Predictive temporal influence |
| Lag structure | Time delay of causal effect |
| Mediation count | Number of intermediate variables |
| Confounding risk | Likelihood of hidden common causes |
| Causal emergence score | Whether macro-level causal model improves over micro-level |
| Causal opacity | Difficulty of identifying true causal structure |

---

## 12. Resource, Energy, and Metabolism Metrics

Every persistent system consumes, transforms, stores, or depends on resources. In some systems, the relevant “resource” may be energy or material; in others, it may be attention, money, bandwidth, trust, or developer time.

| Metric / Attribute | Meaning |
|---|---|
| Energy throughput | Energy consumed per time |
| Material throughput | Matter/resources consumed per time |
| Information throughput | Information processed per time |
| Capital throughput | Money/capital consumed or circulated |
| Attention throughput | Human attention required |
| Trust throughput | Trust required to operate |
| Compute throughput | Computation required |
| Maintenance burden | Resources required to preserve function |
| Repair cost | Cost to restore after damage |
| Coordination cost | Cost of aligning components |
| Transaction cost | Cost of exchange/interactions |
| Search cost | Cost of finding useful states/resources |
| Waste production | Unused byproducts |
| Entropy export | Disorder shifted to environment |
| Storage capacity | Internal reserves |
| Buffer capacity | Ability to absorb fluctuations |
| Slack | Unused capacity available |
| Redundancy cost | Cost of backups/alternatives |
| Efficiency | Useful output / input |
| Load factor | Current use / capacity |
| Overhead ratio | Coordination/maintenance cost / productive output |
| Marginal complexity cost | Added cost per added component/relation |
| Scaling cost exponent | How cost grows with system size |

For software systems, this could map to:

```text
developer_attention
build_time
runtime_compute
dependency_count
operational_overhead
incident_response_cost
technical_debt_interest
```

For institutions, this could map to:

```text
bureaucratic_overhead
trust_requirement
coordination_cost
enforcement_cost
legitimacy_reserve
```

---

## 13. Constraint Metrics

A useful complexity catalog should represent not just what systems are, but what constrains their possible behavior.

| Metric / Attribute | Meaning |
|---|---|
| Constraint count | Number of active constraints |
| Constraint type diversity | Physical, legal, social, computational, energetic, institutional |
| Constraint density | Constraints per component, relation, or process |
| Constraint tightness | How close system is to limits |
| Binding constraint count | Constraints currently limiting behavior |
| Latent constraint count | Constraints that matter only in some regimes |
| Constraint hierarchy | Constraints over constraints |
| Constraint compatibility | Whether constraints conflict |
| Constraint relaxability | Ease of loosening constraints |
| Constraint substitutability | Alternative ways to satisfy requirement |
| Capacity limits | Throughput ceilings |
| Conservation constraints | Mass, energy, money, information, population, etc. |
| Interface constraints | Protocols, standards, APIs, contracts |
| Governance constraints | Rules, laws, norms |
| Cognitive constraints | Limits of perception, memory, attention |
| Environmental constraints | Climate, geography, resource availability |
| Constraint violation cost | Penalty for exceeding constraint |
| Feasible state-space volume | Portion of state-space allowed |
| Constraint-induced modularity | Modularity caused by constraint boundaries |
| Constraint bottleneck index | How much constraints concentrate flow |

This category may become one of the most distinctive parts of the project. Many complexity catalogs measure structure. Fewer measure the geometry of possibility.

---

## 14. Resilience, Robustness, and Fragility Metrics

Resilience should not be treated as one number. It includes avoidance, resistance, absorption, recovery, adaptation, and transformation.

| Metric / Attribute | Meaning |
|---|---|
| Robustness | Maintains function under perturbation |
| Resistance | Degree of initial performance loss |
| Recovery time | Time to restore function |
| Recovery completeness | Fraction of function restored |
| Recovery rate | Slope of return to function |
| Graceful degradation | Whether failure is gradual vs abrupt |
| Failure threshold | Disturbance level causing collapse |
| Safety margin | Distance from threshold |
| Redundancy | Backup components, paths, or functions |
| Functional redundancy | Multiple components performing same role |
| Response diversity | Different ways to respond to shock |
| Adaptive capacity | Ability to reorganize after disturbance |
| Transformability | Ability to become a new viable system |
| Survivability | Ability to persist through severe shock |
| Absorptive capacity | Ability to absorb disturbance without changing regime |
| Repairability | Ease of restoring damaged parts |
| Resourcefulness | Ability to mobilize resources under stress |
| Attack surface | Number of exploitable vulnerabilities |
| Random failure robustness | Robustness to random component loss |
| Targeted attack robustness | Robustness to loss of hubs or keystone nodes |
| Cascade containment | Ability to localize failure |
| Single point of failure count | Components whose loss causes severe failure |
| Common-cause failure exposure | Shared dependencies that fail together |
| Resilience curve area | Integral of performance over time after disruption |

Generic resilience formula:

```text
resilience = ∫ performance(t) dt after disturbance
             --------------------------------------
             ideal performance over same interval
```

---

## 15. Adaptation, Learning, and Evolution Metrics

These metrics distinguish merely complicated systems from adaptive complex systems.

| Metric / Attribute | Meaning |
|---|---|
| Adaptivity | Ability to change behavior in response to environment |
| Learning rate | Speed of improvement from experience |
| Memory horizon | How far back history influences behavior |
| Exploration rate | Search of new possibilities |
| Exploitation rate | Use of known successful strategies |
| Exploration/exploitation balance | Search vs optimization |
| Innovation rate | New components, processes, or strategies per time |
| Mutation rate | Random variation rate |
| Selection pressure | Strength of filtering among variants |
| Fitness gradient clarity | Whether better states are detectable |
| Reproduction rate | Creation of similar entities |
| Recombination rate | Combining existing modules into new ones |
| Plasticity | Reconfigurability without identity loss |
| Evolvability | Capacity to generate viable variation |
| Path dependence | Degree to which history constrains future |
| Lock-in | Difficulty escaping current architecture |
| Drift | Directionless change over time |
| Adaptation latency | Delay between environmental change and response |
| Maladaptation risk | Adaptation that worsens long-term performance |
| Learning externality | Whether learning by one part helps or hurts others |
| Institutional memory | Persistence of knowledge across turnover |
| Forgetting rate | Loss of useful information over time |

Possible derived metrics:

```text
evolvability = variation_generation × selection_feedback × recombination_capacity

adaptive_capacity = sensing × learning × reconfiguration × resource_slack

lock_in = switching_cost × path_dependence × dependency_depth
```

---

## 16. Organization, Governance, and Coordination Metrics

These are especially important for social, software, institutional, economic, and AI-mediated systems.

| Metric / Attribute | Meaning |
|---|---|
| Centralization | Concentration of decision power |
| Decentralization | Distribution of decision power |
| Polycentricity | Multiple semi-independent control centers |
| Hierarchy depth | Number of authority levels |
| Span of control | Number of direct reports or dependents |
| Decision latency | Time to make decisions |
| Decision bandwidth | Number or complexity of decisions per time |
| Coordination cost | Cost of aligning activity |
| Conflict rate | Frequency of incompatible actions or goals |
| Conflict resolution efficiency | Time or cost to resolve conflicts |
| Rule density | Number of explicit rules |
| Norm strength | Informal constraint strength |
| Enforcement cost | Cost to enforce rules |
| Legitimacy | Acceptance of governance by participants |
| Accountability | Ability to trace responsibility |
| Power concentration | Inequality of influence |
| Information asymmetry | Unequal knowledge distribution |
| Trust level | Confidence among components or agents |
| Trust dependency | Degree system requires trust to function |
| Incentive alignment | Local incentives support global outcome |
| Principal-agent risk | Agents optimizing against system goals |
| Capture risk | Control layer captured by subset of agents |
| Governance adaptability | Ability to update rules |
| Bureaucratic drag | Delay or cost introduced by governance layer |

Possible governance archetypes:

```text
centralized_control
hierarchical_control
distributed_consensus
market_coordination
stigmergic_coordination
protocol_based_coordination
emergent_norm_coordination
hybrid_governance
```

---

## 17. Environment and Niche Metrics

A system’s complexity is partly a response to its environment.

| Metric / Attribute | Meaning |
|---|---|
| Environmental volatility | Rate of environmental change |
| Environmental uncertainty | Predictability of environment |
| Environmental diversity | Number of distinct external conditions |
| Resource abundance | Availability of required inputs |
| Resource variability | Stability of resource supply |
| Competition intensity | Rival systems competing for resources |
| Cooperation availability | External partners or mutualisms |
| Predation/adversarial pressure | Active hostile forces |
| Disturbance frequency | How often shocks occur |
| Disturbance severity | Size of shocks |
| Disturbance diversity | Variety of shock types |
| Niche breadth | Range of environments system can operate in |
| Niche specialization | Narrowness of fit |
| Environmental coupling | Strength of dependency on environment |
| Input diversity | Number of input sources |
| Output dependency | Who or what depends on system outputs |
| Externality production | Effects imposed outside system boundary |
| Ecological embeddedness | Number and depth of relationships to other systems |
| Substrate dependence | Reliance on specific physical or informational base |

Possible derived metrics:

```text
niche_fit = system_capabilities / environmental_demands

environmental_pressure = volatility × scarcity × adversarialness

specialization_risk = specialization × environmental_volatility
```

---

## 18. Function, Performance, and Value Metrics

These are often domain-specific, but the catalog needs a generic scaffold.

| Metric / Attribute | Meaning |
|---|---|
| Primary output | Main product, service, or function |
| Throughput | Output per time |
| Latency | Time from input to output |
| Reliability | Probability of successful operation |
| Availability | Fraction of time operational |
| Accuracy | Correctness of output |
| Precision | Variability around target |
| Quality | Fitness of output to need |
| Productivity | Output per resource |
| Efficiency | Useful output / input |
| Stability of performance | Variance in output quality |
| Scalability | Ability to grow without performance collapse |
| Elasticity | Ability to adjust capacity |
| Responsiveness | Speed of reaction to demand |
| Functional coherence | Degree outputs support each other |
| Goal achievement | Performance against stated objective |
| Value creation | Benefit produced |
| Value capture | Benefit retained by system |
| Externalized cost | Costs imposed elsewhere |
| Net utility | Benefit minus cost or harm |
| Multi-objective conflict | Tension among functions |

For comparison across domains, separate:

```text
intrinsic_function
observer_defined_function
participant_defined_function
measured_output
```

A market, an immune system, and an open-source ecosystem do not have the same kind of “purpose,” but all can be evaluated by function-like outputs.

---

## 19. Failure-Mode Taxonomy

Failure modes should be first-class objects in the catalog.

| Failure Mode | Description |
|---|---|
| Cascade failure | Local failure propagates |
| Fragmentation | System breaks into disconnected parts |
| Synchronization collapse | Coordination breaks down |
| Runaway positive feedback | Reinforcement escapes control |
| Oscillatory instability | System enters damaging cycles |
| Bottleneck overload | Critical channel saturates |
| Resource depletion | Inputs exhausted |
| Diversity collapse | Variation disappears |
| Monoculture fragility | Too much sameness |
| Capture | System controlled by narrow subset |
| Corruption | Internal incentives degrade function |
| Lock-in | Cannot adapt due to history or dependencies |
| Senescence | Maintenance burden overwhelms renewal |
| Overfitting | Too optimized for past environment |
| Interface breakdown | Standards or protocols fail |
| Trust collapse | Participants stop believing or cooperating |
| Legibility collapse | State becomes unobservable or unmanageable |
| Control instability | Interventions worsen behavior |
| Measurement gaming | Metrics become targets |
| Phase transition | Abrupt regime shift |
| Extinction / collapse | System ceases to persist |
| Absorption | System becomes part of another |
| Drift into incoherence | Loss of organizing principle |

Potential metrics:

```text
failure_mode_count
dominant_failure_mode
failure_cascade_depth
failure_threshold
mean_time_to_failure
mean_time_to_recovery
single_point_failure_count
hidden_coupling_score
technical_debt_score
trust_collapse_risk
capture_risk
overfitting_risk
```

---

## 20. Potentials and Latent Capacities

These describe what the system could become or do, not just what it currently does.

| Potential | Meaning |
|---|---|
| Reconfiguration potential | Ability to rearrange structure |
| Innovation potential | Capacity to generate new forms |
| Expansion potential | Ability to scale up |
| Compression potential | Ability to simplify without major loss |
| Generalization potential | Ability to work in new contexts |
| Learning potential | Capacity to improve |
| Resilience reserve | Unused recovery capacity |
| Slack reserve | Spare resources |
| Coordination reserve | Unused governance or coordination capacity |
| Control leverage | Small interventions with large effects |
| Transformation potential | Ability to become a different viable system |
| Collapse potential | Latent instability |
| Cascade potential | Latent propagation capacity |
| Phase-transition potential | Likelihood of abrupt regime shift |
| Integration potential | Ability to merge with other systems |
| Modularity potential | Ability to decompose into modules |
| Substitution potential | Ability to replace components |
| Automation potential | Ability to shift work to automated processes |
| Self-maintenance potential | Ability to repair or preserve itself |
| Self-replication potential | Ability to reproduce system pattern |

This category is inherently more speculative than many others, so it should always include confidence and evidence fields.

---

## 21. Comparative and Relational Metrics

This is where the project becomes a “periodic table” rather than a catalog.

| Metric / Attribute | Meaning |
|---|---|
| System similarity | Distance between metric vectors |
| Structural similarity | Similarity of graph/topology |
| Dynamic similarity | Similarity of time-series behavior |
| Functional similarity | Similarity of outputs/functions |
| Constraint similarity | Similar constraints |
| Failure-mode similarity | Similar ways of breaking |
| Evolutionary similarity | Similar developmental path |
| Homology | Shared deep structure or history |
| Analogy | Similar function without shared origin |
| Isomorphism | Same structure under relabeling |
| Embedding coordinates | Position in latent complexity space |
| Cluster membership | System type or class |
| Nearest neighbors | Most similar systems |
| Outlierness | Distance from known classes |
| Universality class | Shared invariant behavior |
| Tradeoff frontier position | Location relative to Pareto frontier |
| Missing-combination marker | Rare or absent metric combination |
| Relationship type | contains, depends on, competes with, regulates, transforms, consumes, produces |
| Dependency graph position | Role in larger system-of-systems |

Possible relation schema:

```text
SystemRelation = {
  source_system,
  target_system,
  relation_type,
  strength,
  direction,
  symmetry,
  dependency_type,
  temporal_window,
  confidence
}
```

Possible relation types:

```text
contains
part_of
depends_on
feeds
regulates
competes_with
cooperates_with
models
simulates
copies
descends_from
replaces
stabilizes
destabilizes
extracts_from
is_analogous_to
is_homologous_to
```

---

## 22. Metric Quality and Evidence Attributes

The catalog will include both data-rich and data-poor systems. Every metric should therefore carry information about measurement quality.

| Attribute | Meaning |
|---|---|
| Measurement method | Observation, simulation, expert judgment, historical inference |
| Data source | Where value came from |
| Confidence score | Trust in measurement |
| Uncertainty bounds | Range or error |
| Temporal resolution | Sampling frequency |
| Spatial/logical resolution | Granularity |
| Sample duration | Time span observed |
| Missingness | Missing data fraction |
| Bias risk | Known distortions |
| Reproducibility | Whether others can reproduce value |
| Domain transferability | Whether metric compares across domains |
| Normalization method | How raw value became comparable |
| Metric maturity | Experimental, accepted, validated |
| Applicability | Required, optional, domain-specific, not applicable |
| Observer effect | Whether measurement changes system |
| Gaming risk | Whether metric can be optimized perversely |

Metric maturity levels:

| Level | Meaning |
|---|---|
| L0 | Qualitative tag |
| L1 | Ordinal score, e.g. 0–5 |
| L2 | Direct numeric measurement |
| L3 | Computed from data/model |
| L4 | Validated predictive metric |
| L5 | Cross-domain invariant candidate |

---

## 23. Suggested Core Required Metric Set

For version 1, do not try to collect every metric for every system. Define a required core and optional modules.

| Category | Required Fields |
|---|---|
| Identity | name, domain, substrate, origin, system type |
| Boundary | boundary clarity, openness, environment |
| Scale | component count, relation count, hierarchy depth, characteristic time scale |
| Components | component diversity, agency density, turnover rate |
| Network | density, centralization, modularity, clustering, path length, hub concentration |
| Coupling | coupling strength, dependency depth, substitutability, cascade potential |
| Dynamics | state variability, regime count, feedback loops, stability, recovery rate |
| Information | entropy/diversity proxy, observability, information asymmetry |
| Resources | primary resource, throughput, slack, maintenance burden |
| Constraints | binding constraints, constraint tightness, capacity limit |
| Adaptation | learning/adaptation capacity, innovation rate, path dependence |
| Resilience | robustness, redundancy, recovery time, failure threshold |
| Governance | control centralization, decision latency, incentive alignment |
| Environment | volatility, scarcity, adversarialness, disturbance frequency |
| Failure | dominant failure modes, single points of failure |
| Relations | dependencies on other systems, systems depending on it |
| Evidence | confidence, source, measurement method |

This gives roughly 50–70 core fields per system, which is large but manageable.

---

## 24. Optional Metric Modules

Different systems should activate different metric modules.

| Module | Applies To |
|---|---|
| Network topology module | Any graph-like system |
| Agent-based module | Markets, societies, ecosystems, organizations |
| Dynamical systems module | Climate, brains, economies, ecosystems, traffic |
| Software module | Codebases, platforms, protocols, AI systems |
| Infrastructure module | Grids, supply chains, transportation, cloud systems |
| Biological module | Organisms, immune systems, cells, microbiomes |
| Social/institutional module | Governments, firms, communities, cultures |
| Ecological module | Ecosystems, food webs, habitats |
| Cognitive/information module | Minds, language, media systems, LLM ecosystems |
| Economic module | Markets, firms, trade networks |
| Control/governance module | Managed or regulatable systems |
| Resilience/risk module | Safety-critical systems |

---

## 25. Candidate Periodic Table Axes

For the eventual complexity map, some latent axes may be especially informative.

```text
openness
agency_density
adaptivity
coupling_strength
modularity
hierarchy_depth
centralization
feedback_intensity
resource_throughput
constraint_tightness
observability
controllability
resilience
path_dependence
environmental_volatility
failure_cascade_potential
```

Possible coordinate system:

| Axis | Low End | High End |
|---|---|---|
| Agency | Passive components | Strategic agents |
| Adaptivity | Static | Learning/evolving |
| Coupling | Loose | Tight |
| Modularity | Integrated | Modular |
| Control | Uncontrolled | Highly governable |
| Openness | Closed | Environmentally porous |
| Predictability | Stable | Chaotic/nonlinear |
| Resilience | Brittle | Robust/adaptive |
| Constraint | Flexible | Constraint-saturated |
| Emergence | Additive | Strong macro-patterning |
| Reflexivity | Non-reflexive | Self-altering when modeled |
| Resource regime | Abundant/slack | Scarce/high-load |

---

## 26. Weird but Valuable Metrics

These may produce some of the most interesting discoveries.

| Metric | Why It Matters |
|---|---|
| Agency density | Separates passive physical systems from strategic systems |
| Constraint topology | Maps what is possible, not just what exists |
| Maintenance burden | Captures system aging and complexity debt |
| Reflexivity score | Key for markets, politics, AI, and social systems |
| Trust metabolism | Social systems often consume trust as a resource |
| Attention metabolism | Media, software, management, and AI systems consume attention |
| Legibility | Some systems fail because nobody can see what is happening |
| Abstraction leakage | Especially useful for software and institutions |
| Interface rigidity | Standards create scale but can also create lock-in |
| Goal heterogeneity | Predicts conflict and coordination cost |
| Gaming susceptibility | Metrics become targets |
| Capture risk | Governance/control layer becomes parasitic |
| Over-optimization index | Efficiency gained by sacrificing slack or diversity |
| Latent cascade capacity | System appears stable until propagation starts |
| Coarse-grainability | Whether macro descriptions work |
| Homology score | Quantified “these are secretly the same kind of thing” |
| Complexity debt | Accumulated maintenance burden from past choices |
| Environmental mismatch | System optimized for an environment that no longer exists |

---

## 27. Candidate Database Structure

A first-pass database could include these top-level tables or collections:

```text
systems
system_boundaries
components
component_types
relations
relation_types
processes
state_variables
metrics
metric_observations
constraints
resources
environments
failure_modes
interventions
system_relations
classification_tags
evidence_sources
```

Controlled vocabulary for metric classes:

```text
descriptor
count
ratio
distribution
network_metric
time_series_metric
information_metric
causal_metric
resilience_metric
constraint_metric
resource_metric
governance_metric
comparative_metric
qualitative_score
```

---

## 28. Example Metric Observation Schema

```json
{
  "metric_id": "network.modularity",
  "system_id": "example_system",
  "value": 0.73,
  "unit": null,
  "normalized_value": 0.73,
  "scale_level": "meso",
  "temporal_window": {
    "start": "2026-01-01",
    "end": "2026-03-31"
  },
  "spatial_scope": "global_system",
  "method": "computed_from_graph",
  "data_source": "dependency_network_snapshot",
  "confidence": 0.82,
  "uncertainty": {
    "type": "bootstrap_ci",
    "lower": 0.69,
    "upper": 0.76
  },
  "assumptions": [
    "Edges represent active dependencies",
    "Edge weights normalized to [0,1]"
  ],
  "applies_to": true,
  "notes": "Computed on largest connected component."
}
```

---

## 29. Example System Relation Schema

```json
{
  "source_system": "open_source_ecosystem",
  "target_system": "software_supply_chain",
  "relation_type": "part_of",
  "strength": 0.91,
  "direction": "source_to_target",
  "symmetry": "asymmetric",
  "dependency_type": "component_and_maintenance_dependency",
  "temporal_window": {
    "start": "2020-01-01",
    "end": null
  },
  "confidence": 0.8
}
```

---

## 30. Example Composite Pattern Rules

Composite rules can be used as provisional hypotheses.

```text
high_modularity + high_coupling + low_slack
→ brittle modularity

high_diversity + low_coordination
→ fragmentation risk

high_centralization + high_volatility
→ adaptation bottleneck

high_efficiency + low_redundancy
→ cascade vulnerability

high_agency + low_observability
→ governance opacity

high_path_dependence + high_maintenance_burden
→ senescence / complexity debt

high_openness + high_adversarialness
→ security pressure

high_feedback_gain + high_feedback_delay
→ oscillatory instability

high_constraint_tightness + high_load + low_slack
→ threshold fragility

high_reflexivity + high_metric_visibility
→ gaming / Goodhart pressure
```

---

## 31. Design Warning

A lot of these metrics will be tempting to normalize into one number.

Do not do that early.

The value of the project will come from discovering configurations, clusters, constraints, tradeoffs, and system archetypes.

A single “complexity score” would erase the interesting parts.

The stronger goal is to build a map from structure to possibility:

> Given a system’s architecture, constraints, history, environment, and resource regime, what behaviors are possible, likely, unstable, powerful, fragile, or impossible?

---

## 32. Natural Next Steps

1. Define the initial controlled vocabulary for systems, metrics, relation types, and evidence types.
2. Choose 10–20 seed systems from very different domains.
3. Apply only the required core metric set first.
4. Track which fields are hard to populate.
5. Separate directly measurable metrics from qualitative or inferred ones.
6. Build the first similarity matrix.
7. Look for early clusters, outliers, and surprising analogies.
8. Convert promising derived patterns into testable hypotheses.
9. Add optional metric modules by domain.
10. Use the resulting dataset to discover candidate complexity classes.

---

## 33. Potential Seed Systems

A starter catalog might include:

| System | Domain |
|---|---|
| Ant colony | Biological / social insect |
| Immune system | Biological / adaptive defense |
| Human brain | Biological / cognitive |
| City | Urban / infrastructural / social |
| Open-source software ecosystem | Software / social / economic |
| Kubernetes ecosystem | Software infrastructure |
| Internet routing system | Technical infrastructure |
| Electrical grid | Infrastructure |
| Global supply chain | Economic / logistical |
| Financial market | Economic / reflexive |
| Coral reef | Ecological |
| Forest ecosystem | Ecological |
| Language | Cognitive / cultural / informational |
| Scientific community | Social / epistemic |
| Nation-state bureaucracy | Institutional |
| Traffic system | Urban / dynamical |
| Social media platform | Social / informational / algorithmic |
| Large language model ecosystem | AI / software / economic |
| Microbiome | Biological / ecological |
| Blockchain network | Technical / economic / governance |

These seed systems are intentionally diverse. The first useful discoveries may come from surprising nearest neighbors among them.

---

## 34. Reference Concepts to Explore Later

This document intentionally remains implementation-oriented. The following concepts may be worth deeper literature review later:

- complex systems theory
- network science
- dynamical systems
- information theory
- causal emergence
- resilience engineering
- adaptive systems
- social-ecological systems
- agent-based modeling
- cybernetics and control theory
- systems ecology
- evolutionary computation
- statistical mechanics
- graph embeddings
- manifold learning
- Pareto frontiers
- universality classes
- Goodhart’s law
- constraint satisfaction
- system-of-systems engineering

---

## 35. Summary

This ontology should be treated as a living framework.

The project is not merely to catalog complex systems, but to make them comparable.

The most promising outputs are likely to be:

- latent axes of complexity
- system classes and universality classes
- recurring tradeoffs
- failure-mode families
- resilience archetypes
- intervention archetypes
- lifecycle patterns
- system homologies and analogies
- rare or impossible metric combinations
- maps of constraint-shaped possibility

The eventual “periodic table of complexity” should not be a static ranking. It should be a map of how different forms of complexity arise, persist, adapt, fail, and transform.
