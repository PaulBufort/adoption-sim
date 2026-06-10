# Modeling decisions log

> Protocol: the builder (AI) logs every modeling choice that affects scientific claims —
> with options, trade-offs, and a recommendation — then proceeds with the recommendation
> marked **PROVISIONAL**. The scientist arbitrates at each review: change status to
> **RATIFIED** (keep), or pick another option / write a variant, and the builder updates
> code and docs to match. Nothing PROVISIONAL should be presented publicly as settled.

> **Arbitration session 2026-06-10 (scientist):** D1–D16 RATIFIED, several with
> additions recorded under the matching entries (dual-regime headline for D1,
> sensitivity sweeps for D2 and D8, caption rules for D9, re-verification for D16).
> New decision D17 (observability) ratified and implemented the same day.

| ID | Decision | Status |
|----|----------|--------|
| D1 | Threshold distribution | RATIFIED 2026-06-10 (+ dual-regime presentation) |
| D2 | Innovators (zero-threshold mass) | RATIFIED 2026-06-10 (+ p_innov sweep, p=0 labeled variant) |
| D3 | Credibility weights | RATIFIED 2026-06-10 (incl. closeness amendment, as realism feature) |
| D4 | "Ready" operationalization (awareness gate) | RATIFIED 2026-06-10 |
| D5 | "Willing" operationalization | RATIFIED 2026-06-10 |
| D6 | "Able" operationalization | RATIFIED 2026-06-10 |
| D7 | Update scheme, decay and relapse | RATIFIED 2026-06-10 (incl. amendment) |
| D8 | Broadcast operationalization | RATIFIED 2026-06-10 (+ T_b sweep) |
| D9 | Seeding strategies and budget fairness | RATIFIED 2026-06-10 (+ caption rule) |
| D10 | Informal-layer generator | RATIFIED 2026-06-10 |
| D11 | Dead-pocket definition | RATIFIED 2026-06-10 |
| D12 | Pivot-node definition | RATIFIED 2026-06-10 (null result + positive control) |
| D13 | Tenure: attribute only, inert in dynamics | RATIFIED 2026-06-10 |
| D14 | Replicate semantics (what error bars mean) | RATIFIED 2026-06-10 |
| D15 | Team locality (wide bridges) in within-dept ties | RATIFIED 2026-06-10 (as realism feature) |
| D16 | Headline scenario freeze + negative-result commitment | RATIFIED 2026-06-10 (re-verified post-D17) |
| D17 | Observability of adoption (visibility v) | RATIFIED 2026-06-10 |

---

## D1 — Threshold distribution

**Context.** Spec §2.2: θ drawn from "a parameterizable distribution (mean per role,
heterogeneity parameter)". The shape of this distribution drives every result.

**Options.**

1. **Beta distribution, reparameterized by (mean μ, concentration κ).**
   Natural support on [0,1], no truncation artifacts, two interpretable knobs
   (μ per role; κ = homogeneity — high κ means everyone is alike). Skew emerges
   naturally at low/high means.
2. **Truncated normal (μ, σ) on [0,1].** Familiar to most readers; but truncation
   distorts the realized mean near the boundaries (a configured μ=0.2 with large σ
   yields a true mean ≠ 0.2), which is a silent lie in figure captions.
3. **Uniform [μ−h, μ+h].** Maximally simple; but bounded support hides tail behavior
   (no strongly resistant individuals), and h has no natural interpretation.

**Trade-off summary.** Beta is the standard choice in the diffusion literature for
bounded heterogeneous traits and keeps captions honest (configured mean = true mean).
Truncated normal is more familiar but subtly misleading. Uniform is too crude for
threshold-sensitivity claims.

**Recommendation: Option 1 (Beta(μ, κ))**, with per-role mean offsets and a single
global κ. Defaults: μ = 0.30 for all roles (role offsets exposed but zero by default —
we do not assume seniors are more/less resistant without evidence), κ = 8
(sd ≈ 0.15 at μ = 0.3). **RATIFIED (2026-06-10).**

**Arbitration addition (scientist, 2026-06-10).** The headline presentation becomes
**dual-regime**: main panel at κ = 20 (broadcast fails cleanly), companion panel at
κ = 12 (the "lottery" regime where broadcast is a high-variance gamble), with a
caption stating that real-world threshold heterogeneity is unmeasured and the
qualitative story is regime-dependent. Implemented in experiment 1.

---

## D2 — Innovators (zero-threshold mass)

**Context.** With a pure Beta threshold distribution and credible-fraction exposure,
a one-shot broadcast converts almost exactly nobody (the comms term is a few percent
of anyone's credibility mass), so broadcast trivially fails — the headline comparison
would be rigged by construction. Real populations contain spontaneous early adopters.

**Options.**

1. **Mixture: with probability p_innov an agent has θ = 0 ("innovator"); otherwise
   θ ~ Beta(μ, κ).** Default p_innov = 0.025 (Rogers' classic ~2.5% innovator
   category). Broadcast then plausibly converts the scattered innovators and stalls —
   the *interesting* failure, not a rigged one.
2. **No atom; rely on the Beta lower tail.** Cleaner mathematically, but at μ=0.3
   the mass below a realistic one-shot broadcast exposure is ≪1%, so broadcast ≈ 0
   adoption by construction; the headline claim becomes circular.
3. **Larger atom (5–16%, Rogers' innovators + early adopters).** More generous to
   broadcast, but conflates "early adopter" (low θ but still social) with "innovator"
   (needs no peers), and overstates spontaneous conversion.

**Recommendation: Option 1** (p_innov = 0.025, θ=0 atom). It makes broadcast's failure
mode emergent (innovators adopt, cascade stalls at silo boundaries) rather than assumed.
Sensitivity over p_innov reported in experiments. **RATIFIED (2026-06-10).**

**Arbitration addition (scientist, 2026-06-10).** Default 2.5% confirmed, PLUS a
first-class sensitivity sweep p_innov ∈ {0, 0.01, 0.025, 0.05} in experiment 1.
The p = 0 cell **is** the "no-innovators" variant left open in D16 — always clearly
labeled as a variant, never presented as the default.

---

## D3 — Credibility weights

**Context.** Spec §2.2: "exposures weighted by source credibility (close peer >
manager > central comms)". Exposure of agent i = (Σ weights of adopted credible
contacts) / (Σ weights of all credible contacts), plus the broadcast term when active.

**Options.**

1. **Relationship-type weight table** (defaults):
   same-team peer 1.0 · other peer 0.6 · direct manager↔report 0.7 · central comms 0.3.
   Transparent, four numbers a reviewer can argue with, directly encodes the spec's
   ordering.
2. **Continuous tie strength from the informal generator × type multiplier.**
   Richer (strong cross-silo friendships possible), but two entangled mechanisms make
   attribution murky and the headline harder to explain.
3. **Uniform weights (all 1.0).** A null model — no credibility mechanism at all.

**Trade-off summary.** Option 1 keeps the mechanism inspectable and matches the spec's
qualitative ordering. Option 2 is more realistic but harder to defend number-by-number.
Option 3 alone would ignore the spec, but is valuable as a robustness toggle.

**Recommendation: Option 1 as the model, Option 3 retained as a built-in sensitivity
toggle** (experiments report whether headline ordering survives uniform weights).
**RATIFIED (2026-06-10).**

**Amendment (2026-06-10, builder, after calibration scans — needs arbitration.)**
"Close peer" is now defined by *relationship closeness*, not team co-membership:
ties to ring-adjacent sister teams (D15) count as close collaborators with weight
**peer_close = 1.0**, like own-team peers; all other non-manager ties carry
**peer_far = 0.6**. Rationale: with sister ties at 0.6, two bridge ties deliver
about one teammate's worth of influence while also inflating the fractional
denominator — wide bridges were devalued exactly where the mechanism needs them,
and measured scans showed cluster seeding *never* beating random seeding under
any tested (θ̄, κ, silo, locality) combination. Weighting by closeness restores a
2:1 advantage of a saturated sister team over a lone scattered seed. The original
flat-0.6 variant remains available (`sister_close=False`) and the headline
experiment reports the comparison. *(Original note: "load-bearing for the headline
claim" — later downgraded; see the D15 empirical amendment.)*

**Arbitration (scientist, 2026-06-10): RATIFIED including this amendment**, with
the D15 framing — a structural-realism feature reported as an experimental
variable, not the mechanism the headline depends on.

---

## D4 — "Ready" operationalization (awareness gate)

**Context.** ready = "sufficient exposure (the threshold condition)". Subtlety: an
innovator with θ = 0 would otherwise adopt at t=0 in every scenario, even with zero
exposure — spontaneous ignition would contaminate all strategies.

**Options.**

1. **ready(i,t) ≡ [weighted adopted-contact share ≥ θ_i] AND [share > 0].**
   The second clause is an *awareness* requirement: you cannot adopt a tool you have
   never seen. Broadcast creates awareness for everyone (its purpose!); otherwise
   awareness requires ≥1 adopted contact.
2. **ready ≡ share ≥ θ_i only.** Simpler, but θ=0 innovators adopt out of thin air in
   every condition, inflating all baselines equally and muddying attribution.
3. **Separate two-stage awareness then adoption process (awareness spreads as simple
   contagion, adoption as complex).** Most realistic, but doubles the state space and
   the parameter count — overkill for v0.1.

**Recommendation: Option 1.** One extra clause, large gain in interpretability:
broadcast's *only* real power is creating awareness everywhere at once, which is
exactly the real-world intuition being tested. **RATIFIED (2026-06-10).**

---

## D5 — "Willing" operationalization

**Context.** willing = "individual disposition (perceived cost, drawn randomly,
modulated by role)". Adoption requires ready ∧ willing ∧ able; every non-adoption is
attributed to a missing condition.

**Options.**

1. **Static Bernoulli draw at t=0:** willing_i ~ Bernoulli(p_willing(role)), default
   p = 0.85 for all roles (role modulation exposed, neutral by default). Crisp
   attribution: a never-adopter who was ready is "unwilling", full stop.
2. **Continuous cost c_i vs. exposure surplus** (adopt iff share − θ_i > c_i).
   Richer, but "willing" then depends on exposure level, so the ready/willing
   attribution is no longer separable — the diagnostic map loses its meaning.
3. **Time-varying willingness (re-drawn each step or eroding with fatigue).** Adds a
   trend with no v0.1 evidence basis; harder to explain.

**Recommendation: Option 1.** The whole point of R/W/A in this spec is *legible
attribution*; only the static draw keeps the three conditions independent.
Note the honest consequence: with p=0.85, max possible adoption is ~85% (the willing
ceiling) — figures must say so. **RATIFIED (2026-06-10).**

---

## D6 — "Able" operationalization

**Context.** able = "practical capacity (tool access/time; a unit-level parameter)".

**Options.**

1. **Per-unit rate applied per agent at t=0:** able_i ~ Bernoulli(a_u) where a_u is
   the unit's capacity rate; default a_u = 1.0 everywhere, scenarios may handicap
   specific units. Models "some people in unit X lack licenses/time".
2. **Binary per unit (whole unit able or not).** Simpler, but produces all-or-nothing
   dead pockets that are trivially explained — nothing to diagnose.
3. **Global scalar.** Cannot produce unit-level diagnostic maps at all.

**Recommendation: Option 1**, with the headline scenario keeping a_u = 1.0 everywhere
(structural effects must emerge from the network, not from planted handicaps; "able"
is demonstrated in a dedicated attribution example instead). **RATIFIED (2026-06-10).**

---

## D7 — Update scheme, decay and relapse

**Context.** Spec §2.2: "optional de-adoption when usage is not reinforced (retention
parameter) — reproduces the documented spike-then-relapse pattern."

**Options — update scheme.**

1. **Synchronous discrete steps** (all agents evaluated on the state at t−1).
   Standard in the threshold-cascade literature (Watts, Centola & Macy), exactly
   reproducible, fast to vectorize. Known artifact: can synchronize waves.
2. **Random-sequential (asynchronous) updates.** Avoids synchrony artifacts, but
   results depend on update order (another RNG stream to explain), slower, and the
   literature baseline for comparison is synchronous.

**Options — relapse rule (when decay enabled).**

1. **Reinforcement hysteresis:** an adopter whose current weighted adopted-contact
   share < r·θ_i (r = retention factor, default 0.5) relapses with probability ρ per
   step (default 0 = off; 0.1 when studying relapse). Isolated adopters quit;
   socially-embedded ones persist — mechanistically meaningful relapse.
2. **Unconditional exponential decay** (relapse with prob ρ regardless of
   neighborhood). Simpler, but relapse then carries no structural information —
   spike-then-relapse becomes a curve-fitting trick, not a finding.

**Recommendation: synchronous updates (1) + hysteresis relapse (1).** Headline figure
runs with decay OFF for clarity; a dedicated experiment section studies decay ON.
Relapsed agents may re-adopt if conditions are met again (no permanent immunity).
**RATIFIED (2026-06-10).**

**Empirical amendment (2026-06-10, builder).** Measured behavior of hysteresis
relapse contradicts the spec's expectation in an instructive way:

1. **No visible "spike then relapse"**: because relapse and adoption interleave
   during the cascade, decay manifests as a *lower plateau*, never as a visible
   overshoot-then-sag. The documented mass spike-then-relapse pattern appears to
   require *non-social* decay (novelty wearing off independently of neighbors) —
   exactly Option 2, which we rejected as structurally meaningless. Reported as a
   negative result; the model cannot currently reproduce that stylized fact.
   θ=0 innovators additionally can never relapse (share < r·0 is impossible) —
   coherent ("they never needed social proof") but worth your sign-off.
   *Arbitration (scientist, 2026-06-10): both signed off — innovators-never-relapse
   stands with that interpretation; the spike-then-relapse non-reproduction is
   reported as a finding.*
2. **Decay differentially punishes scattered adoption** (headline regime, ρ=0.25,
   r=1.0, 8 reps): random 0.73 → 0.26, champions 0.75 → 0.45, cluster 0.29 → 0.32
   (unchanged). At ρ=0.40 the cluster-vs-random ordering fully reverses (0.30 vs
   0.15). Cluster-seeded adoption is *decay-proof by construction* — local critical
   mass keeps everyone reinforced. This emergent finding becomes the decay section
   of experiment 1.

---

## D8 — Broadcast operationalization

**Context.** Spec: broadcast = "everyone exposed once". How does a broadcast enter a
*fractional* exposure rule?

**Options.**

1. **Transient virtual comms contact:** for steps t ∈ [1, T_b] (default T_b = 1),
   every agent's exposure is computed as (adopted-weight + w_comms)/(total-weight +
   w_comms), i.e. central comms is one additional "contact" of weight 0.3 (D3) that
   endorses the tool, for everyone, while the campaign runs. Afterwards the term
   vanishes (message salience fades). While the campaign runs, everyone is aware —
   the comms term satisfies D4's "share > 0" clause. Seeds *no* adopters directly.
2. **Persistent comms node** (a node adopted forever, connected to everyone).
   Models a permanent campaign, not "exposed once"; inflates every denominator
   forever; contradicts the spec's wording.
3. **Direct conversion:** broadcast flips a random x% to adopted at t=0. Operationally
   identical to random seeding — the comparison would be meaningless.

**Recommendation: Option 1.** Broadcast = universal awareness + a one-step credibility
nudge from a low-credibility source. Innovators (D2) and near-zero-θ agents convert;
everyone else needs peers. This is the mechanism the headline claim rests on, so it is
the single most important decision to arbitrate. **RATIFIED (2026-06-10).**

**Arbitration addition (scientist, 2026-06-10).** Headline keeps T_b = 1, PLUS a
sensitivity sweep T_b ∈ {1, 5, 20} in experiment 1 — the "what about repeated
campaigns?" objection, answered with data rather than argument.

---

## D9 — Seeding strategies and budget fairness

**Context.** Five strategies must be comparable. "Seeds" are agents set to adopted at
t=0 (and aware). Budget k = seed fraction (default 5% of N) for all strategies except
broadcast, which by definition seeds nobody (it buys awareness, not adopters).

**Definitions (as implemented).**

- **broadcast** — 0 seeds; universal awareness + transient comms exposure (D8).
- **random** — k·N agents uniformly at random.
- **champions** — top k·N by **degree centrality on the informal layer** (the
  well-connected, regardless of unit). Alternative: betweenness (bridge-people);
  kept as an option flag, default degree because it is the classic "champion
  program" heuristic and cheap at 20k nodes.
- **cluster** — fill whole teams: order teams (random permutation per replicate),
  seed every member of successive teams until the budget is spent (partial last
  team). Mirrors real pilot-team rollouts; maximizes local critical mass by
  construction.
- **line-manager-first** — k·N agents drawn uniformly from line managers (if the
  budget exceeds the manager count, all managers + random ICs top-up; logged).

**Fairness rule.** All seeded strategies get *exactly* the same number of seeds
(⌊k·N⌋); broadcast gets zero seeds plus universal awareness. An optional
"broadcast + random k%" hybrid exists for the demo but is not one of the five
canonical strategies.

**Open question for arbitration.** Is "broadcast (0 seeds) vs cluster (k% seeds)" a
fair headline comparison, or should the headline compare *equal-budget* strategies
only, with broadcast as a reference floor? Recommendation: present broadcast as the
reference floor and say so explicitly in captions. **RATIFIED (2026-06-10).**

**Arbitration addition (scientist, 2026-06-10) — caption rule:** every figure that
shows broadcast states **"0 seeds — broadcast buys awareness, not adopters."**
Implemented as the broadcast legend label in `experiments/plotting.py`, so no figure
can omit it.

---

## D10 — Informal-layer generator

**Context.** Spec §2.1: informal layer = "homophily + proximity + noise"; silos and
their permeability are the core demonstrative device.

**Options.**

1. **Hierarchical stochastic block model with four tie classes:** within-team p_team
   (dense), within-department p_dept, cross-department p_cross (the *silo
   permeability* knob, possibly scaled by tenure homophily), plus uniform random
   noise ties. Silo strength s ∈ [0,1] maps monotonically: s=1 → p_cross ≈ 0
   (hermetic silos); s=0 → p_cross ≈ p_dept (no silo effect).
2. **Spatial/latent-space model** (embed agents, connect by distance). Elegant
   homophily, but silo strength is then an emergent quantity — not a slider — and
   the demo needs a slider.
3. **Watts–Strogatz-style rewiring of the formal tree.** Cheap, but conflates the
   two layers by construction, undermining the formal/informal divergence the spec
   demands.

**Recommendation: Option 1**, with degree kept realistic (mean informal degree ~8–15,
right-skewed via a small hub mechanism: a fraction of agents get extra cross-unit
ties, interpretable as "tenured connectors"). Formal layer = the org-chart tree
(report→manager→department head→leadership) and is used only to define roles, units,
manager links and broadcast reach — adoption never travels along it unless the same
dyad also exists informally (manager↔report dyads are added to the informal layer
with the D3 manager weight, since real managers do talk to their reports).
**RATIFIED (2026-06-10).**

---

## D11 — Dead-pocket definition

**Context.** "Dead-pocket map (units below critical mass)".

**Options.**

1. **Absolute cutoff:** unit is a dead pocket if final adoption < 25% (parameter).
   Simple, comparable across scenarios; arbitrary number.
2. **Relative cutoff:** < 50% of the global final rate. Adapts to scenario scale, but
   a universally failed rollout then has *no* dead pockets — perverse.
3. **Bimodality detection** (gap-based clustering of unit rates). Statistically
   prettier, fragile on few units.

**Recommendation: Option 1** (default 0.25, reported alongside the threshold so the
reader can re-cut). **RATIFIED (2026-06-10).**

---

## D12 — Pivot-node definition

**Context.** "Pivot nodes (relays whose removal changes the plateau)."

**Options.**

1. **Counterfactual knockout among candidates:** candidates = top-M nodes by
   betweenness centrality on the informal layer (M default 20; approximate betweenness
   sampling above 2,000 nodes); for each, remove the node, re-run R replicates, and
   report Δplateau. Pivot ⇔ mean Δplateau > ε (default 5 percentage points).
   Honest (it *is* the definition) but costs M·R extra runs.
2. **Pure structural proxy** (betweenness/bridging score only, no re-runs). Cheap but
   answers a different question — structure, not dynamics; the spec's wording is
   explicitly counterfactual.

**Recommendation: Option 1**, with the structural score reported alongside as the
screening heuristic it is. **RATIFIED (2026-06-10).**

**Empirical amendment (2026-06-10, builder).** At v0.1 parameters the knockout
diagnostic returns a **null result**: across headline and harsher-silo variants
(N=1000, symmetric and one-sided seeding, fixed or re-drawn workforces), no single
node's removal shifts the plateau beyond replicate noise — generated organizations
carry enough redundant bridges that no individual is load-bearing. Even fully
one-sided pilots (all seeds in one department) either fail to jump silos at all
(silo ≥ 0.94: the receiving side needs θ ≤ one bridge tie's share ≈ 0.05, i.e.
an innovator, and then a successful team ignition — joint probability ~7% per
org) or jump through redundant paths. We do NOT fish for lucky seeds to
manufacture a pivot demo. The notebook reports the null, validates the diagnostic
on a designed bottleneck (barbell positive control, also a unit test), and keeps
the tool for imported real topologies where genuine bottlenecks exist.
``pivot_nodes`` gained an ``agents`` parameter to support fixed-workforce
("this org, these people") semantics.

---

## D13 — Tenure: attribute only, inert in dynamics

**Context.** Spec lists "simulated tenure" as a node attribute. Nothing in the spec
says tenure affects adoption.

**Options.**

1. **Tenure shapes the network only** (tenure homophily in informal tie formation;
   long-tenured agents slightly likelier to be cross-unit connectors), and is
   otherwise inert in the dynamics.
2. **Tenure modulates thresholds or willingness** (e.g. veterans more resistant).
   Plausible-sounding, but it would be an *invented* behavioral claim with no v0.1
   evidence; it would silently shape results.

**Recommendation: Option 1.** v0.1 makes no behavioral claims about tenure; this is
stated in limitations.md. **RATIFIED (2026-06-10).**

---

## D14 — Replicate semantics (what error bars mean)

**Context.** Each experimental condition is run R times (default 20). What varies
between replicates determines what the reported bands mean.

**Options.**

1. **Full regeneration:** each replicate draws a *new* organization (same generator
   parameters) *and* new agent attributes and dynamics randomness. Bands then mean:
   "across organizations of this kind" — the honest scope of a synthetic-data claim.
2. **Fixed graph, redrawn agents/dynamics:** one organization per condition, R
   draws of thresholds/willingness/seeds. Tighter bands, faster; but claims silently
   condition on one particular random org, inviting over-reading.
3. **Nested design (G graphs × R draws each)** with variance decomposition.
   The statistically complete answer; more machinery than v0.1 claims require.

**Recommendation: Option 1** for all headline claims (R = 20, seeds derived from one
master seed via `numpy.random.SeedSequence.spawn`); Option 2 retained as an engine
flag (`share_graph`) for the pedagogical demo, where regenerating per slider-move
would be slow and the demo makes no quantitative claims. **RATIFIED (2026-06-10).**

---

## D15 — Team locality (wide bridges) in within-department ties

**Context (empirical, from the first calibration scan, 2026-06-10).** With
within-department cross-team ties spread *uniformly* across a department's ~15–30
teams, a fully adopted team presents at most ~1 tie to any neighbouring team —
"narrow bridges". Result, measured on a 24-cell scan (θ̄ × κ × silo, N=2000,
6 replicates): cluster seeding **never** outperforms random seeding anywhere; it
saturates its seeded teams and stalls (~6–10%), while random seeding percolates
through the low-threshold tail whenever that tail is fat enough. This contradicts
the central literature result this tool is meant to demonstrate (Centola & Macy
2007; Centola 2010: complex contagion requires *wide bridges* — multiple
overlapping ties between adjacent clusters).

**The modeling question.** Is uniform within-department mixing the right null, or
should collaboration ties be locally concentrated ("sister teams" that share
projects), giving adjacent teams several overlapping ties?

**Options.**

1. **Add a team-locality parameter.** Teams within a department sit on a ring
   (a stand-in for project/desk proximity); a cross-team tie's partner team is
   chosen at ring distance d ~ 1 + Geometric(team_locality), so high locality
   concentrates ties on 1–2 sister teams (wide bridges), locality → 0 recovers
   uniform mixing. Default 0.7. Realistic (collaboration is locally concentrated
   in real orgs), one interpretable knob, and makes bridge width an *explicit
   experimental variable* instead of a hidden assumption.
2. **Keep uniform mixing.** Honest null, but then the simulator's main
   demonstration is "cluster seeding stalls; scattered seeding wins or everything
   dies" — a defensible negative result, yet it would contradict the established
   experimental literature *because of a known unrealistic structural assumption*
   (no real department mixes its teams uniformly).
3. **Hardwire sister-team pairs** (each team gets exactly 2 partners, dense
   inter-team blocks). Strongest bridges, but a new discrete structure with more
   arbitrary choices (how many partners? how dense?), and no smooth dial back to
   the uniform null.

**Recommendation: Option 1.** It contains Option 2 as the locality→0 limit, so
experiments can show *both* regimes and report honestly when cluster seeding does
NOT win (narrow bridges, fat low-θ tail). The headline figure must state the
locality value; the bridge-width sensitivity becomes a first-class experiment
section. **RATIFIED (2026-06-10).**

**Empirical amendment (2026-06-10, builder, after the notebook-02 tornado).** In the
*frozen headline regime* (κ=20), `team_locality` is **not load-bearing after all**:
sweeping it 0.4 → 0.9 moves the cluster plateau by 0.1 pp (vs 46 pp for θ̄), and the
headline gap also survives uniform credibility weights (cluster even gains —
sanity-checks.md check 4). Locality and the D3 closeness amendment mattered in the
κ=12 regime explored during calibration, not in the frozen one. Downgrade both from
"load-bearing for the headline" to "structural realism features and experimental
variables". This *strengthens* the headline (robust to two contested choices) and
shifts arbitration priority to D1/D2 (threshold distribution) and the seed budget.

---

## D16 — Headline scenario freeze + negative-result commitment

**Context.** Calibration scans (2026-06-10; ~100 cells over θ̄ × κ × silo × locality ×
dept_degree × budget, N=2000, 6–10 replicates each) mapped three regimes:

1. **Low/tight thresholds (θ̄ ≲ 0.2):** everything — including broadcast — saturates
   near the willing ceiling (~85%). Innovators ignite their own teams via the low-θ
   tail; team→sister-team dominoes finish the job. No strategy contrast.
2. **Moderate thresholds (θ̄ ≈ 0.30, κ ≈ 12–20):** the demonstrative regime.
   Broadcast converts only innovators and stalls (5–8% at κ=20), or becomes a
   high-variance lottery (κ=12: 0.20 ± 0.13 — sometimes an innovator's team ignites
   a cascade, usually not). Cluster seeding reliably builds local critical mass and
   spreads through sister-team bridges; **silo strength monotonically caps its
   plateau** (0.83 → 0.35 as s goes 0.5 → 0.95). This answers the spec's headline
   question: *when does broadcast fail where cluster succeeds, and which structures
   gate the outcome.*
3. **High thresholds (θ̄ ≳ 0.36):** everything stalls; differences are noise.

**The negative result (committed to publication, per spec §6).** Across the entire
explored space, *scattered* strategies (random, champions-by-degree) matched or beat
cluster seeding — e.g. random 0.67 ± 0.12 vs cluster 0.31 ± 0.07 in the headline
cell. Mechanism, in this model family: (a) every agent is embedded in a dense team,
so each scattered seed is itself a potential team-igniter through the heterogeneous
threshold tail; (b) the 2.5% innovator atom acts as a free scattered seeding subsidy
in every condition; (c) fractional thresholds devalue additional bridges (every new
tie also grows the denominator). The popular "always seed clusters" heuristic is
NOT reproduced here; experiment 1 reports this prominently rather than hiding it,
with the mechanism analysis above as testable explanation.

**Headline scenario (frozen, RATIFIED 2026-06-10):** N=2000, 8 departments, mean team 8,
silo_strength=0.85 (panel B sweeps 0.5–0.95), team_locality=0.7, dept_degree=6.0,
θ̄=0.30, κ=20, p_innovator=0.025, p_willing=0.85, able=1.0, budget=5%, decay off,
20 replicates with full regeneration (D14), all five strategies.
*(Release-sprint note, 2026-06-10, owner directive: headline replicates raised
20 → 50 for figure precision. A precision knob, not a model change — recipe
parameters and D14 semantics untouched.)*

**Alternatives considered for forcing a "cluster beats random" ordering** — tighter
θ (κ 25–200), smaller budgets (1–2%), wider bridges (dept_degree 6, locality 0.9),
closeness-weighted sisters (D3 amendment) — none produced it; the innovator atom
plus team embedding always favored scattering. Removing the innovator atom entirely
(p_innovator=0) would manufacture the ordering but break broadcast's realism (D2's
rationale). *Resolution (arbitration 2026-06-10): the no-innovators regime is
demonstrated as the clearly-labeled p_innov = 0 cell of the D2 sensitivity sweep —
a variant, never the default.*

**Arbitration (scientist, 2026-06-10): RATIFIED** — recipe frozen, negative result
reported prominently in experiment 1 with the mechanism analysis. Re-verified after
the D17 implementation: with the ratified default v = 1.0 the engine consumes no
additional randomness, and the headline result CSVs reproduce **bit-for-bit**
(checked by CI's reproduce-headline job).

**Mechanism amendment (2026-06-10, builder, from the ratified D2 sweep).** The
original analysis credited the innovator atom as a co-cause of scattering's
advantage ("a free scattered seeding subsidy"). The p_innov sweep **refutes the
necessity half of that claim**: at p_innov = 0, random *still* beats cluster
(0.42 ± 0.09 vs 0.20 ± 0.04). Team embedding plus the heterogeneous Beta tail is
sufficient; innovators amplify the gap but do not create it. Meanwhile broadcast
at p_innov = 0 converts **exactly 0.000** across all replicates — broadcast's
entire yield is innovator-dependent. Both figures are in experiment 1 §4.

---

## D17 — Observability of adoption (visibility v)

**Context (scientist, 2026-06-10).** Real-world AI usage is largely *invisible*: it
happens in a browser tab; colleagues see outputs, not methods. The model so far
assumes every adopted contact generates exposure — implicitly visibility = 1.0.
Invisibility may be exactly what devalues scattered seeds in reality, so this knob
speaks directly to D16's negative result.

**Definitional note (ratified with this decision, recorded in model.md).**
"Adoption" in this model means the **costly production behavior** — genuinely
reorganizing how one works around the tool — not shallow substitution use
(search-bar replacement, spellcheck-grade usage). Shallow use spreads as simple
contagion, needs no critical mass, and is out of scope; conflating the two would
make every threshold assumption incoherent.

**Operationalization options.**

1. **Deterministic per-source attenuation:** adopted contact j contributes
   v_j · w_ij to i's exposure numerator; the denominator (total credible contact
   mass) is unchanged — the *person* still counts among i's credible voices, their
   *adoption* is just partially visible. Global scalar v as the model parameter;
   per-agent v_j as an override for interventions. Smooth, reproducible, no new
   randomness.
2. **Stochastic visibility:** each adopted contact is *seen* with probability v
   per step (fresh Bernoulli draws). Arguably more literal, but in a synchronous
   model with absorbing adoption, upward exposure fluctuations get locked in
   (ratchet effect), so stochastic visibility systematically *inflates* adoption
   relative to its own mean — an artifact, not a mechanism. Also adds an RNG
   stream that breaks the bit-for-bit reproduction of all v = 1 results.
3. **Visibility as edge property** (some relationships are show-your-screen
   relationships). Most realistic, but another generator mechanism with no v0.1
   evidence basis; per-agent overrides (option 1) cover the intervention use case.

**Recommendation: Option 1**, default v = 1.0 (backward compatible; at v = 1 the
implementation is the identity and all ratified results stand unchanged).

**Proposition (equivalence; proof in experiment 3, verified by an exact test).**
For v > 0 and any scenario *without a broadcast term*, the trajectory under global
visibility v with thresholds {θᵢ} is **identical** to the trajectory under v = 1
with thresholds {θᵢ/v} (same draws, same seeds): ready, awareness, and relapse
conditions all transform as v·A/W ≥ θ ⟺ A/W ≥ θ/v. Consequences: (a) a *global*
v cannot reorder the seeded strategies — it only slides everyone along the θ̄
sensitivity axis; D16's scattered ≥ cluster ordering is provably v-invariant;
(b) broadcast is the exception (the comms term is fully visible by nature — a
broadcast is loud), so low v *relatively* favors broadcast; (c) the scientifically
live question is **differential** visibility — the "observable pilots" intervention
(seeded agents carry v = 1 while the world sits at v < 1, modeling work-out-loud
rituals; an intervention, not a structural assumption). Experiment 3 measures
whether that intervention rescues cluster seeding.

**RATIFIED (scientist, 2026-06-10).** Implemented as `SimParams.visibility`
(scenario key `agents.visibility`), per-agent override `run_simulation(visibility=…)`,
and the intervention key `seeding.pilot_visibility`.

---
*All defaults above are recorded in `core/defaults.py` and surfaced in `docs/model.md`.
Changing a decision here should change exactly one place in code.*
