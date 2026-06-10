# Model reference (v0.1)

> The model **as implemented** — every equation below is what the code does, not an
> aspiration. Decision IDs (D1…D16) link each choice to its alternatives and status in
> [decisions.md](decisions.md). All parameters live in `core/defaults.py`; scenario
> files override them per experiment.

## 1. The organization (`core/orggen.py`)

### Structure

One CEO; `n_departments` department heads (role *leadership*); departments contain
teams of mean size `mean_team_size` (minimum 3), each with exactly one *line manager*
and ICs. Node attributes: `team`, `dept`, `role`, `tenure` (Gamma(2, mean/2) years,
capped at 40 — shapes ties only, never behavior, D13).

### Formal layer

The org-chart tree: CEO—heads, head—managers of their department, manager—their ICs.
Used for roles, units, and the broadcast channel. Adoption never travels on it
directly; manager–report dyads are *also* present in the informal layer (weight
below), because real managers do talk to their reports.

### Informal layer (where adoption travels) — D10, D15

Undirected, weighted. Tie classes, in construction order (no overwrites):

| class | rule | weight (D3) |
|---|---|---|
| manager–report dyads | always (CEO–heads, head–managers, manager–ICs) | 0.7 |
| within-team peer | each IC pair, p = `p_team` (0.90) | 1.0 (`peer_close`) |
| within-dept cross-team | quota: `dept_degree`·dept_size/2 ties; partner team at ring distance d ~ 1+Geom(`team_locality`); tenure-homophily acceptance exp(−h·Δtenure/mean) | 1.0 if ring-adjacent ("sister team") else 0.6 |
| cross-department | quota: `cross_dept_degree_max`·(1−s)·N/2, s = `silo_strength`; homophily as above | 0.6 (`peer_far`) |
| noise | quota: `noise_degree`·N/2, uniform pairs | 0.6 |
| connectors | `connector_fraction`·N agents (tenure-biased) get `connector_extra_degree` extra ties; cross-dept with prob (1−s), else cross-team | 0.6 |

`silo_strength` s ∈ [0,1] is the headline structural knob: expected cross-department
degree = `cross_dept_degree_max`·(1−s). At s = 1 only the noise leak remains.

**Measured robustness note:** in the frozen headline regime the team-locality and
sister-weight choices are *not* load-bearing (plateau swing ≤ 0.1 pp; see
[sanity-checks.md](sanity-checks.md)) — they are structural-realism features and
experiment variables.

## 2. Agents — D1, D2, D5, D6

Drawn once at t = 0 (RNG order fixed: thresholds, innovators, willingness, ability):

- **Threshold** θᵢ ~ Beta(μ·κ, (1−μ)·κ) with μ = `theta_mean` + role offset
  (defaults 0.30, offsets 0), κ = `theta_concentration` (20). With probability
  `p_innovator` (0.025), θᵢ = 0 — *innovators* (D2).
- **Willing** wᵢ ~ Bernoulli(`p_willing[role]`) (0.85 — a hard ceiling on adoption).
- **Able** aᵢ ~ Bernoulli(per-department rate, default 1.0).
- **Visibility** vᵢ = `visibility` (global, default 1.0; D17) — deterministic, not a
  draw; the observable-pilots intervention overrides it per agent (seeds → 1.0).

## 3. Dynamics (`core/dynamics.py`) — D4, D7, D8, D17

**What "adoption" means (definitional note, ratified with D17).** Adoption here is
the **costly production behavior** — genuinely reorganizing how one works around the
tool — not shallow substitution use (search-bar replacement, spellcheck-grade
usage). Shallow use spreads as simple contagion, needs no critical mass, and is out
of scope; the threshold assumptions below are only coherent for the costly behavior.

Synchronous discrete steps. Let W(i) = Σ weights of i's contacts,
A(i,t) = Σ over i's *adopted* contacts j of v_j · w_ij — where v_j ∈ [0,1] is j's
**visibility** (D17: how much of j's adoption neighbors can actually see; global
default `visibility` = 1.0, per-agent override for interventions) — and
b(t) = `w_comms` (0.3) while a broadcast runs (t ≤ `broadcast_steps`, only under the
broadcast strategy), else 0. The comms term is *not* attenuated by v: a broadcast is
loud by nature.

```
share_i(t) = (A(i,t−1) + b(t)) / (W(i) + b(t))
ready_i(t) = share_i(t) > 0  AND  share_i(t) ≥ θ_i          (D4: awareness gate)
adopt:        ¬adopted ∧ ready ∧ willing ∧ able  →  adopted
relapse (if ρ>0):  adopted ∧ share_i(t) < r·θ_i  →  ¬adopted with prob ρ    (D7)
```

**Equivalence (D17, exactly tested):** for v > 0, global visibility with thresholds
{θᵢ} produces the identical trajectory as v = 1 with thresholds {θᵢ/v}, in any
no-broadcast scenario, including decay. Global invisibility is threshold inflation;
only *differential* visibility (e.g. the observable-pilots intervention,
`seeding.pilot_visibility`) can affect strategy orderings. See experiment 3.

Defaults: ρ = `relapse_prob` = 0 (decay off), r = `retention_factor`. Seeds adopt
unconditionally at t = 0 (pilot groups get access, D9) and relapse like anyone else.
Re-adoption after relapse is allowed. The loop stops at the first step where nothing
changed and nothing can change (fixed point), and pads the curve to `max_steps`.

Every non-adopter is attributed to exactly one missing gate, in the order
able → willing → ready (plus *relapsed* for ever-adopters), which produces the
diagnostic maps.

**Measured properties** (see decisions.md amendments): decay lowers plateaus but
never produces a visible spike-then-relapse (D7); θ = 0 innovators cannot relapse;
no individual knockout shifts the plateau in generated orgs (D12).

## 4. Seeding strategies (`core/seeding.py`) — D8, D9

Budget k = ⌊`budget`·N_active⌋ identical for all seeded strategies (default 5%).

| strategy | seeds |
|---|---|
| broadcast | none — universal transient exposure b(t) instead (D8) |
| random | k uniform |
| champions | top-k informal degree (random tie-break; custom score injectable) |
| cluster | whole line teams in random order until k (partial last team) |
| line_manager_first | k uniform among line managers (top-up random if k exceeds them) |

## 5. Metrics (`core/metrics.py`) — D11, D12

- adoption curve; plateau = mean of last 10 steps; relapse = peak − plateau
- per-unit final rates; **dead pocket** = unit < 0.25 final adoption (D11)
- **pivot node** = candidate whose removal (zeroed ties, excluded everywhere) shifts
  the mean plateau > 5 pp (D12); candidates screened by betweenness
- tornado sensitivity: one-at-a-time low/high per parameter (`core/sweep.tornado`)

## 6. Reproducibility contract — D14

A scenario's `master_seed` spawns one `numpy.random.SeedSequence` child per
(condition, replicate); each child yields the (org, seeding, dynamics) generator
triple. Re-running any sweep with any worker count reproduces results bit-for-bit
(`tests/test_scenario_sweep.py`). Replicates regenerate the organization by default —
error bands mean "across organizations of this kind", not "across runs on one org".
Results ship as CSV + JSON sidecar (scenario, versions, git commit, synthetic flag).

## References

- Granovetter, M. (1978). Threshold Models of Collective Behavior. *AJS* 83(6).
- Watts, D. J. (2002). A simple model of global cascades on random networks. *PNAS* 99(9).
- Centola, D., & Macy, M. (2007). Complex Contagions and the Weakness of Long Ties. *AJS* 113(3).
- Centola, D. (2010). The Spread of Behavior in an Online Social Network Experiment. *Science* 329.
- Centola, D. (2018). *How Behavior Spreads*. Princeton University Press.
- Holland, P. W., Laskey, K. B., & Leinhardt, S. (1983). Stochastic blockmodels: First steps. *Social Networks* 5(2).
- Rogers, E. M. (2003). *Diffusion of Innovations* (5th ed.). Free Press. (adopter categories; the 2.5% innovator convention)
