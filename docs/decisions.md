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

> **Arbitration session 2026-08-02 (scientist, CP1).** Based on the paired S2
> results (`paper/cp1/CP1_ARBITRATION.md`): Route A retained, recentered on a
> **decay-driven crossover** (working title "Disperse to ignite, concentrate to
> endure"). D17(a) corrigendum, D18 (paired upgrade), D19, D21 (verdict
> **no_go**), D22 (sign replication) RATIFIED; D20 RATIFIED with a wording
> amendment (the ±2 pp equivalence of one_per_team vs random is NOT
> established — only "no clear difference was detected"). Terminology fixed:
> `final_rate` is reported as **terminal (active) adoption**, `cumulative_rate`
> as **cumulative reach**; the crossover is located between tested ρ values,
> never as an estimated threshold.

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
| D17 | Observability of adoption (visibility v) | RATIFIED 2026-06-10; consequence (a) RETRACTED by ratified amendment 2026-08-02 (CP1) |
| D18 | Regime map: dispersed-vs-cluster boundary (θ̄ × budget) | RATIFIED 2026-08-02 (CP1) as the paired n=50 3-class upgrade |
| D19 | Paired replicate protocol (common random numbers) | RATIFIED 2026-08-02 (CP1), incl. amendments |
| D20 | Coverage seeding strategy: one_per_team | RATIFIED 2026-08-02 (CP1) with amendment: "no clear difference detected", NOT equivalence |
| D21 | Team-level ignition predictor (semi-analytic) | RATIFIED 2026-08-02 (CP1) — verdict **no_go** accepted as-is |
| D22 | Real-topology replication: email-Eu-core (pre-declaration) | RATIFIED 2026-08-02 (CP1) as SIGN replication on a real topology, not mechanism validation; amendment (a) 2026-08-03 (CP3): "ignition 62%/42%" label RETRACTED |
| D23 | CP3: independent-review arbitration (S3.3 corrigenda) | RATIFIED 2026-08-03 (CP3) — wording corrections only, no data change |

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

**Amendment (scientist, 2026-06-10, release sprint).** The engine *default*
`theta_concentration` is aligned to the ratified headline regime (8 → 20) for
least surprise: `SimParams()` out of the box now behaves like the published
figures. κ = 8 remains the documented sensitivity value (and κ = 12 the lottery
companion); published experiment results are unaffected — every scenario file
pins κ explicitly. Side effect worth recording: the Streamlit demo had been
running on the κ=8 default while its caption claimed κ=20; this amendment makes
the caption true.

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

## D18 — Regime map: dispersed-vs-cluster boundary (θ̄ × budget)

**Context (builder, 2026-08-01).** External review of the COMPLEX NETWORKS
abstract (critical-review pass) argued the headline "scattered beats cluster"
rests on a chosen regime: two κ values at one (θ̄, budget) point do not locate a
boundary, and the tornado (exp 2) already shows θ̄ and budget are the two most
decisive parameters. Requested: an explicit 2D map of
ΔR = mean final reach (random − cluster).

**Options considered.**

1. **θ̄ × budget grid at frozen κ=20** (chosen): 8 θ̄ values (0.15–0.50
   bracketing the frozen 0.30) × 5 budgets (1–15% bracketing the frozen 5%) ×
   {random, cluster} × 12 replicates (sweep standard, D14) = 960 runs, ~20 s.
   Directly answers the review; slots into exp 1 and `make_all` unchanged.
2. **θ̄ × intra-team density:** mechanistically interesting (embedding is the
   claimed mechanism) but does not answer the budget half of the objection.
3. **3D (adding κ):** ~3× cost and an unreadable figure; κ=12 companion already
   exists for the headline.

**Statistics.** Per-cell Welch test with the conservative critical value
t₀.₉₇₅(df=11)=2.201 (no scipy in the stack — stack policy); non-significant
cells hatched in the figure. Cell (0.30, 5%) at n=12 (72.4% vs 28.6%) is
consistent with the 50-replicate headline (69.5% vs 31.9%).

**Findings (synthetic; orderings, not magnitudes).** (i) θ̄ ≤ 0.20: both
strategies saturate at the willing ceiling — no contrast. (ii) A diagonal
ignition band (θ̄ 0.25→0.40 as budget rises 1%→15%) where dispersion wins by
+7 to +44 pp; the frozen headline point sits inside it. (iii) A starved corner
(θ̄ ≥ 0.35, budget ≤ 5%) where nothing spreads and the only significant
cluster-favoured cells appear (≈ −1 pp). The folklore prescription is right
only where the campaign is doomed regardless.

**D17(a) corrigendum — RATIFIED amendment (scientist, 2026-08-02, CP1).** D17
inferred "a global v cannot reorder the seeded strategies; the ordering is
provably v-invariant". The equivalence v ≡ θ→θ/v is exact (the proposition
stands, unit-tested), but the *no-reordering corollary is RETRACTED*: the
regime map shows the random-vs-cluster ordering changes along the θ̄ axis, and
sliding θ̄→θ̄/v moves the organization across that map. Correct use of the
theorem: a global visibility drop relocates the organization on the regime
map; it does not preserve orderings. Consequences (b) and (c) unaffected.

**RATIFIED (scientist, 2026-08-02, CP1) in the paired-upgrade form below.**
Final counts (n=50 pairs/cell, Holm two families, ±2 pp band): **14 dispersion
wins** (+4 to +43 pp), **23 proven equivalences** (within ±2 pp, for the
tested cells and model), **3 uncertain**, **0 cluster wins** — the two n=12
cluster-favoured cells did not survive the corrected design. Canonical
artifact: `experiments/results/exp1_regime_paired_headline.csv`; the n=12
map is superseded (never committed).

**Upgrade path (builder, 2026-08-02 — pending CP1 arbitration).** The n=12
independent-samples map is superseded by `exp1.run_paired_regime` under D19:
50 paired replicates per cell (random and cluster on identical organizations),
two Holm-corrected test families (paired difference; paired TOST against a
±2 pp practical band), and a 3-class cell verdict — *win* (Holm difference
p < 0.05 AND |Δ̂| ≥ 2 pp), *equivalence* (Holm TOST p < 0.05: the contrast is
provably inside ±2 pp — "strategy irrelevant here" as a positive claim),
*uncertain* (neither). The old (n=12, uncorrected) and new cell counts will be
recorded side by side at the CP1 regeneration commit; the n=12 CSV was never
committed, so the supersession leaves no divergent published artifact.

## D19 — Paired replicate protocol (common random numbers)

**Context (builder, 2026-08-02).** External review of the CN2026 abstract,
priority 1: the decay comparison behind the "reach–retention" framing was an
*unpaired* n=12-vs-n=50 contrast across two different sweeps — different
organizations, different agent draws — leaving the decisive quantity
(cluster − random under decay) at +0.9 pp with a ±9 pp CI: parity claimed on an
inconclusive interval. The regime map had the same weakness cell by cell
(random and cluster drawn on different orgs). Between-organization variance
(sd ≈ 9–16 pp) dominates these contrasts; pairing removes it.

**Options.**

1. **Independent sampling, more replicates.** Precision grows only as 1/√n;
   reaching a ±2 pp CI on the decay contrast would need n in the hundreds.
2. **Common random numbers (chosen):** `core/sweep.expand_paired_jobs` — within
   each (base-combo, replicate) block, every condition of the paired axes
   reuses the same pre-spawned (org, seeding, dynamics) seed triple: identical
   organization, identical θ/willing/able draws, identical seed sets where the
   strategy coincides; decay arms diverge only at the first relapse draw
   (verified bit-exact in tests/test_paired.py). Contrasts become paired
   differences; between-org variance cancels.
3. **share_graph (rejected):** D14 option 2 fixes the org across replicates
   *within* a condition — the opposite design; bending it would silently revisit
   ratified D14. `expand_paired_jobs` raises if share_graph is set.

**D14 untouched.** A replicate is still a fully regenerated organization; error
bands still mean "across organizations of this kind". Pairing operates *within*
a replicate, *across* conditions.

**Analysis toolkit** (`experiments/stats.py`, numpy + stdlib — no scipy, stack
policy): paired t with hand-coded Student-t tails (regularized incomplete beta,
pinned to the repo's 2.201/df=11 and 2.0096/df=49), 95% CIs, effect size d_z,
paired TOST against a ±2 pp practical-negligibility band, Holm step-down
applied SEPARATELY to the difference family and the equivalence family, and the
3-class cell verdict (see D18 upgrade).

**Outcome measures (user arbitration, 2026-08-02).** Alongside terminal reach
(`final_rate`), the decay analyses report **cumulative reach** — ever-adopted
share among active agents, read directly from the engine's `ever_adopted`
tracker (`RunResult.ever_adopted`; denominator = active agents, consistent with
`final_rate` and the seed budget) — and **retention_rate** = terminal /
cumulative (undefined/NaN when cumulative = 0). The ratio is always reported
next to the absolute levels: a high retention ratio on a tiny base is not a
win (docs/limitations.md #16).

*Why the tracker is mandatory, not a convenience (found while testing,
2026-08-02):* the attribution shortcut (n_adopted + n_relapsed) **undercounts**
cumulative reach. Seeds adopt unconditionally (D9), so a non-willing or
non-able seed that later relapses is attributed NOT_WILLING/NOT_ABLE, not
RELAPSED — those ever-adopters vanish from the shortcut (≈1–2% of agents at
headline parameters). `tests/test_run_job_columns.py` pins both the exact
tracker identity and the shortcut's bounded undercount.

**Anti-seed-fishing commitment.** master_seed stays 20260610; the seed layout
(SeedSequence children indexed by (base-combo, replicate), one triple per
block) was frozen at implementation time — commits `d86efba` and `09724dc`,
BEFORE any paired result was inspected. Whatever the paired runs show is
reported; if they contradict a previously cited number, that is flagged in
RESULTS_VERIFIED.md per the honesty rules, never quietly edited away.

**RATIFIED (scientist, 2026-08-02, CP1), including the amendments below and
the reporting outcome:** the paired protocol resolved the decay question the
n=12 unpaired design could not — see D18 and RESULTS_VERIFIED for the
crossover finding and the flagged contradiction with the previously cited
"parity".

**Amendment (user arbitration, 2026-08-02 — pre-declared BEFORE any paired
run executes; audit findings integrated).**

1. **Decay family correction, pre-declared.** The grid **executes 24 arms**
   (3 strategies × 2 r × 4 ρ; 1 200 sims at n = 50), but the primary family
   contains only the **seven unique** paired random − cluster contrasts: one
   per (r, ρ) cell with ρ > 0 (2 r × 3 ρ), plus the shared ρ = 0 baseline
   (its two r arms are bit-identical by construction — r is inert without
   relapse — and count once; the duplication is kept as a free bit-identity
   self-check). The family is Holm-corrected and classified with the same
   3-class scheme (±2 pp band) as the regime map. **Primary endpoint:
   `final_rate`** (terminal reach among active agents). The two D19 outcome
   metrics `cumulative_rate` and `retention_rate` are **secondary**: reported
   descriptively (means, per-cell paired CIs), with no Holm-corrected
   win/equivalence claim attached — any corrected claim on a secondary metric
   would require its own pre-declared family. Contrasts involving champions
   are likewise descriptive only.
2. **Reporting policy: the paper cites the PAIRED runs exclusively** for every
   seeded-strategy mean and contrast. The independent 50-replicate panel
   remains the source for broadcast (not part of the paired design) and serves
   as a repo-level cross-check. Audit fact behind the rule: by seed layout the
   paired and independent samples are **disjoint** organizations for the
   seeded strategies (0/50 shared; broadcast incidentally shares 50/50) —
   their means differ by sampling noise and must never be presented as the
   same number. `paper/audit_numbers.py` must treat them as distinct sources.
3. **run_robustness layout fixed pre-execution** (audit findings): (a)
   `pair_id` is prefixed with the axis name — `expand_paired_jobs` restarts
   its block index per call, so raw ids would collide across the three axes
   and a join on `pair_id` alone would silently mix organizations; (b) the
   headline configuration appears exactly **once** (as n_agents = 2000) — the
   mean_team_size axis would otherwise reproduce that arm *bit-identically*
   (same spawn index ⇒ same organizations), and the silo axis would
   triplicate the configuration under fresh seeds.
4. **A-priori power fact (recorded for CP1):** with n = 50 pairs and the
   ±2 pp band, TOST equivalence is declarable only if the paired sd is below
   ≈ 8.4 pp. Unpaired between-org sds run 9–16 pp — without pairing, no cell
   could ever have been declared equivalent. Check the realized paired sds at
   CP1 against this bound.

**D19(b) amendment — CP3 corrigendum (scientist arbitration, 2026-08-03).**
The variance-mechanism claims above — "pairing removes it" (Context) and
"between-org variance cancels" (option 2) — are **retracted as stated**; the
original wording is left in place per the honesty rules. What the design
guarantees is *confounding control*: every contrast compares strategies on
identical organizations and agent draws, so organization-level heterogeneity
cannot confound a within-block difference. It does **not** guarantee variance
reduction or narrower CIs than independent sampling: the realized
random↔cluster correlation across the 58 paired cells is weak (median ≈ +0.18)
and slightly *negative* at the headline cell (−0.09; paired-difference sd
14.9 pp vs ≈14.3 pp under a hypothetical independent design) — ignition
variance is largely strategy-specific, not shared. All published CIs are
unaffected (they were always computed from the paired differences themselves).
The manuscript sentence citing a "shared between-organization variance
component (9–16 pp) [that] drops out" was corrected at S3.3; the a-priori
power fact in item 4 is unaffected, and the realized paired sds meet its
≈8.4 pp TOST bound only in saturated/starved cells — which is exactly why
every declared equivalence lies in those regions (recorded at CP3; the
manuscript now says so).

## D20 — Coverage seeding strategy: one_per_team

**Context (builder, 2026-08-02).** External review, priority 5: random and
cluster are mechanism probes, not credible best-practice baselines. Degree
targeting already exists (`champions` = top-k informal degree). The live
mechanistic question is whether random's advantage is simply *touching many
teams* — its Poisson seed spread covers ~84 of 249 line teams at the headline
budget. `one_per_team` makes coverage explicit: maximal dispersion WITH a
coverage guarantee.

**Spec** (`core/seeding.py`): one uniformly chosen member per line team, teams
visited in random order; budget beyond the team count starts a second
round-robin pass; exact-budget assert inherited from D9; leadership team
excluded on synthetic orgs (imported real graphs treat unit 0 as ordinary —
see D22). Greedy influence maximization stays explicitly out of scope for the
abstract (cited as a non-goal; Kempe–Kleinberg–Tardos).

**Pre-declared reading grid (before paired results were inspected):**
one_per_team ≥ random would be *consistent with* the team-coverage mechanism;
one_per_team ≈ random would suggest random's Poisson spread already achieves
effective coverage at this budget. Either outcome is reported; neither is
described as "proving" the mechanism.

**RATIFIED with amendment (scientist, 2026-08-02, CP1).** Observed paired
contrast one_per_team − random: −1.4 pp, 95% CI [−5.0, +2.2] (n=50; the exact bound is −5.045 — an earlier −5.1 was a double-rounding artifact). The CI
extends beyond the ±2 pp band, so **equivalence is NOT established**; the only
authorized wording is "**no clear difference was detected**" (consistent with
— not proving — random's Poisson spread already covering teams effectively).
Never write "proved equivalent" for this contrast.

## D21 — Team-level ignition predictor (semi-analytic, level 1)

**Context (builder, 2026-08-02).** External review, priority 3: the meso
diagnostic (seeded/ignited team counts) *measures* the mechanism but predicts
nothing. The upgrade with the best originality-to-risk ratio: a semi-analytic
per-team ignition rule validated against the simulations.

**Scope (level 1, the paper-facing deliverable).** Within-team Granovetter
cascade computed exactly on the team's members (θ draws incl. innovator atom,
willing/able gates, within-team credibility weights) under an external-mass
dilution term (each member's denominator includes their out-of-team credible
mass); P_ig(s, m) tabulated by vectorized Monte Carlo off-network; folded
through each strategy's seeds-per-team distribution (hypergeometric for
random; ⌊k/m̄⌋ fully seeded teams for cluster; s=1 in min(k, n_teams) teams
for one_per_team; champions excluded — no clean closed form). Level 2
(spillover bootstrap on the team-quotient graph) is a stretch goal with a hard
stop on 2026-08-19; it is full-paper material.

**Pre-declared validation gates.** V1: per-team ignition AUC ≥ 0.80 on seeded
teams (level 1's claim is local ignition, not spillover). V2: sign agreement
with ≥ 90% of the *decisive* paired regime-map cells, zero opposite-sign
errors. Verdicts: **go** (predictor sentence + ignition-boundary overlay on
the regime figure), **partial** (AUC 0.70–0.80: overlay framed as "consistent
with", no AUC claim), **no-go** (measured meso mechanism only; predictor named
as future work). All three text variants are pre-drafted before CP1 so the
checkpoint is a selection, not a rewrite. Language rule in all variants:
results are "consistent with" the mechanism — never "prove" it.

**PROVISIONAL (builder, 2026-08-02).** Awaiting scientist arbitration (CP1).

**Pre-execution calibration note (user arbitration, 2026-08-02 — gates
untouched).** Level 1 is implemented (`experiments/predictor.py`; its cascade
is pinned bit-exactly against the engine on an isolated team) and calibrated
by the fixed-seed script `experiments/calibrate_predictor.py` (master seed
20260802; 5 orgs, 3000/1500 MC draws; deterministic, unit-tested). Official
run: out-of-team credible mass ≈ 48% of the exposure denominator;
P_ig(s, m=8) at headline parameters: s=1 → 0.021, s=2 → 0.210, s=3 → 0.676,
s≥4 → 1.0. Folding: cluster buys 13.0 near-certain local ignitions; random
buys ~100 tickets at ~2% across ~84 teams (E ≈ 4.9 locally ignited teams).
Confronted with the committed meso diagnostic: for random, **98% of observed
ignited teams and 90% of observed reach are not explained by the level-1
local predictor** (two different denominators — teams vs reach — never to be
interchanged; an earlier exploratory run quoted 97% for teams, superseded by
the official seeded run). The phrasing is deliberate: "not explained by the
local predictor" is what was measured; whether the residual is inter-team
spillover, model error, or both is exactly what level 2 would have to decide.
Level 1 models the ignition kernel, not final reach; the sign of
Δ(random − cluster) at the headline point is nonetheless reproduced
(+1.6 pp local vs +37.6 pp observed). **Expected verdict:
*partial*.** The V1/V2 gates and the go/partial/no-go rule are NOT modified
and will be applied verbatim to the validation data at CP1; the case
"V1 passes, V2 fails" is read as *partial* (local ignition validated, map
sign structure not) — flagged for arbitration, not silently resolved.

**RATIFIED (scientist, 2026-08-02, CP1) — actual verdict: `no_go`, accepted
as-is.** Gates applied verbatim to the paired data
(`paper/cp1/predictor_validation.json`): V1 pooled AUC **0.642** over 12 789
seeded-team units (< 0.70, below even the partial band; observed ignition
rate of seeded teams 90.7%), V2 sign agreement 1.000 on 14 decisive cells,
zero opposite-sign errors. Per-strategy AUCs (descriptive): cluster 0.996,
champions 0.694, random 0.631, one_per_team 0.591 — consistent with, not
demonstrating, local ignition being predictable exactly where seeding is
concentrated. Paper consequence = the pre-drafted no-go variant: the meso
mechanism stays MEASURED (CSV-derived); the predictor is named as
pre-specified in this decision log and failed at its gates — AUC below even
the partial threshold (one transparency sentence in the body, never the
abstract); level-2 modeling is future work. Wording rule: "pre-specified in
a version-controlled decision log", never "pre-registered" (no external
registry was used).

## D22 — Real-topology replication: email-Eu-core (pre-declaration)

**Context (user arbitration, 2026-08-02).** The #1 admitted weakness of the
abstract (REVIEWER_RATIONALE §1): no real-topology replication of the headline
contrast. The user chose email-Eu-core (SNAP) over Enron because it ships
**ground-truth department labels** (42 departments) — community structure is
given, never inferred (no Louvain).

**Pre-declared design — written and committed BEFORE the experiment is run.**

1. **Topology.** email-Eu-core is a *directed* email graph; the model runs on
   undirected weighted graphs. Symmetrization: **union** — undirected edge
   u–v iff at least one email in either direction; self-loops dropped;
   isolates dropped (exposure share undefined; core/ingest.py contract).
   Mutual-only symmetrization is an optional robustness variant if time
   allows, not a headline arm.
2. **Units.** SNAP department labels attach via `as_org(..., team_attr=…)`.
   On imported graphs, unit 0 is an **ordinary seedable department** — the
   LEADERSHIP_TEAM exclusion is a synthetic-generator semantic and does not
   apply (cluster and one_per_team both treat it as seedable; tested).
3. **Agents.** ALL behavioral attributes are synthetic (headline θ, willing,
   able, credibility mapping from core/ingest.py). Framing is fixed:
   *"replication on a real modular topology with synthetic behavioral
   attributes"* — NEVER an empirical validation of a real diffusion
   (docs/limitations.md #11 applies verbatim).
4. **Protocol.** Fixed real topology; 50 fresh attribute+seed draws; within
   each draw, every compared strategy (random, cluster; champions if cheap)
   sees exactly the same topology and the same agent attributes (CRN, D19);
   paired contrast with 95% CI. The D14 deviation (topology fixed across
   replicates) is intrinsic to a real-graph arm and recorded here: bands mean
   "across attribute draws on THIS topology".
5. **Reporting commitment.** The result is reported whichever way it comes
   out — **including if the random-vs-cluster ordering fails to reproduce**.
   The only drop condition is a *technical* failure (download/format), and a
   drop would itself be stated in the paper's repo. No re-runs with new seeds.

**RATIFIED (scientist, 2026-08-02, CP1) — as a SIGN replication on a real
modular topology with synthetic behavioral attributes, NOT a mechanism
demonstration.** Outcome (reporting commitment honored): paired
random − cluster **+13.5 pp, 95% CI [+1.0, +26.0]**, p=0.034, n=50 attribute
draws; the regime on this topology is a bimodal ignition lottery (draws end
near ~9% or ~83%; random ignites in 62% of draws vs 42% for cluster;
champions saturates at 84.4% ± 1.3). Authorized claim: *the sign of the
dispersed-vs-clustered contrast replicates on a real modular topology with
synthetic behavioral attributes*; magnitudes are not comparable across
topologies and the mechanism is not empirically validated.

**D22(a) amendment — CP3 corrigendum (scientist arbitration, 2026-08-03).**
The clause "random ignites in 62% of draws vs 42% for cluster" is **retracted
as a measurement**; the sentence above is left in place as the historical
record. The ≥10% cut behind those shares (a) was not pre-declared in this
entry — only the paired contrast was — and (b) falls **inside the low mode**
of the strongly bimodal outcome distribution (pooled random+cluster terminal
rates: mode medians 9.2% / 84.6%; **no draw between 20.2% and 82.0%** — a
~62 pp gap), so it separates non-ignited draws from other non-ignited draws
rather than measuring the low/high-mode split. **No replacement threshold is
adopted** (any post-hoc cut, including the reviewer's 20%, inherits the same
problem). Authorized descriptions from this arm: the pre-declared paired
contrast (+13.5 pp [1.0, 26.0]) and the bimodal shape itself
(`paper/numbers.json` → `eucore.modes`, a descriptive largest-gap split that
replaces the removed `eucore.ignition_share`). The 62%/42% values survive
only here and in the CP1 package as the trace of the retracted labelling.

## D23 — CP3: independent-review arbitration (S3.3 corrigenda)

**Context (scientist arbitration, 2026-08-03).** An independent senior-review
pass (Opus, read-only, on submission candidate commit `5346724`) returned a
weak-accept with two scientific errors, two overstatements, and several
recommendations. This entry records the arbitration; S3.3 implements it.
**No simulation, no new seed; every new number derives from the
already-versioned paired CSVs and enters `numbers.json` + the audit
(35 → 42 claims).**

| Reviewer point | Decision | Implementation |
| --- | --- | --- |
| S1.1 — "shared between-org variance (9–16 pp) drops out" is false (median paired correlation ≈ +0.18; −0.09 at headline) | **accepted** | D19(b) corrigendum; manuscript claims confounding control only, no efficiency gain assumed; post-hoc correlations recorded here, NOT in the paper |
| S1.2 — Eu-core "ignition 62%/42%" uses a ≥10% cut inside the low mode | **accepted, amended** | D22(a) retraction; manuscript reports the bimodal shape (medians 9%/85%, no draw between 21% and 82%); reviewer's replacement 20% cut REJECTED as equally post hoc |
| S2.1 — crossover is endpoint-dependent; cumulative contrast at (1,.25) is −1.8 [−5.4,+1.8], inside the band | **accepted** | terminal stays the sole confirmatory endpoint; cumulative contrasts quoted as secondary descriptive with pointwise uncorrected CIs: −1.8 [−5.4,+1.8] at (1,.25), −7.4 [−10.7,−4.1] at (1,.40); "driven mainly by differential retention" now explicit |
| S2.2 — abstract arithmetic incomplete (14+23≠40); equivalences structurally degenerate | **accepted in part** | abstract now 14 / 23 (saturated-or-starved) / 3 with no cluster win ≥2 pp; the reviewer's "14 of ~17 cells where strategies can differ" denominator REJECTED as a post-hoc classification |
| S2.3 — "cluster seeding wins nowhere" too strong | **amended** | replaced by "no practically relevant cluster win (≥2 pp); largest cluster edge 0.8 pp, in the starved corner, inside the band". Reviewer's own claim of "three reliable cluster edges" is WRONG after Holm: exactly one sub-1 pp edge is Holm-significant (θ̄=0.35, budget 1%, −0.76 pp, p_holm<10⁻⁴; the other two: 0.17, 0.97) — recorded in `regime_map.largest_cluster_edge` |
| Add p_innov=0 random−cluster (+21.4 [14.9,27.9]) to the paper | **REJECTED** | independent panel, n=12/arm, Welch — D19 amendment 2 forbids citing the independent panel for any seeded-strategy contrast; kept in `paper/REVIEWER_RATIONALE.md` as an explicitly-labelled exploratory oral answer |
| Add ~86% willing-ceiling note | **REJECTED** | not needed by any claim; would add an unaudited number |
| Timeline: "pre-specified before execution" reads too strong | **accepted** | manuscript now says "after exploratory n=12 panels, before the confirmatory run"; no claim of pre-specification prior to all exploration |

**Delivery constraints honored:** `final_rate` remains the only confirmatory
endpoint; cumulative contrasts stay descriptive (no new Holm family); exactly
4 pages; figure unchanged; audit extended; 119 tests green; corrigenda in
this file + `RESULTS_VERIFIED.md` v3 rather than silent edits.

---
*All defaults above are recorded in `core/defaults.py` and surfaced in `docs/model.md`.
Changing a decision here should change exactly one place in code.*
