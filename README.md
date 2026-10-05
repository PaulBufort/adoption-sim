# adoption-sim

**A research simulator of complex contagion on synthetic organizational networks.**
When an organization wants to spread a costly practice (a tool such as an AI
assistant, a work habit), should it concentrate the first adopters (seeds) in a
few dense teams, or disperse them across teams? In the simulated organizations,
dispersing seeds spreads the practice further, but concentrating them sustains it
when people often drop practices unused by colleagues: **disperse to ignite,
concentrate to endure.**

This repository holds the code, the decision log (D1–D23) and the reproduction
pipeline behind the extended abstract *Disperse to ignite, concentrate to endure:
a decay-driven crossover in modular complex contagions* (Paul Bufort), accepted at
COMPLEX NETWORKS 2026, the 15th International Conference on Complex Networks and
Their Applications (Granada, 1–4 December 2026).

> **⚠ Everything this tool produces is synthetic.** Generated organizations,
> stipulated thresholds, uncalibrated dynamics. It is an instrument for reasoning
> about *mechanisms* — never a forecast of any real rollout. The full list of things
> you cannot conclude is in [docs/limitations.md](docs/limitations.md), and it is
> long on purpose.

Built with AI assistance; every modeling decision was human-arbitrated and is
logged with its alternatives in [docs/decisions.md](docs/decisions.md).

![Figure 1 of the extended abstract, two panels. (a) Heat map of the paired difference in terminal adoption, random minus cluster seeding, across mean threshold and seed budget, without decay: dispersion wins along a diagonal band, grey cells are equivalent within ±2 pp, hatched cells are uncertain, and no cell shows a cluster advantage of 2 pp or more. (b) The same contrast as the relapse probability rises, for two retention requirements: it falls and changes sign between the tested values. SYNTHETIC DATA.](figures/exp1_crossover_2panel.png)

*Figure 1 of the extended abstract. Synthetic data: 50 paired organizations per
cell. (a) Paired difference in terminal adoption, random minus cluster (pp),
across mean threshold θ̄ and seed budget, without decay; Holm-corrected
difference and TOST families, grey = equivalent within ±2 pp; boxed cell = the
headline setting, an independent paired sample. (b) Same contrast with decay
(95% CIs; hollow marker = uncertain); r = reinforcement required for retention.*

## What the abstract reports

Terminal adoption in this synthetic model (50 paired organizations per
condition; 50 paired attribute draws on email-Eu-core), 95% confidence intervals
in brackets. The results in this section are quoted from the extended abstract;
each estimate is machine-extracted from the versioned result CSVs into
[`paper/numbers.json`](paper/numbers.json).

**Without relapse, dispersion wins.** In the headline scenario, random seeding
reaches 72.0% ± 9.2% terminal adoption (mean ± SD), against 32.4% ± 11.0% for
cluster seeding: a paired difference of **+39.7 pp [35.4, 43.9]**. Degree
targeting (champions) adds about 3.9 pp (descriptive, [0.6, 7.1]); one-per-team
coverage shows no clear difference from random seeding (−1.4 pp [−5.0, +2.2]).
On average, random seeding already places seeds in 82 of the 249 line teams,
against 13 for cluster seeding. Over the 40 cells of the regime map (Fig. 1a),
dispersion wins in 14, along a diagonal ignition band from +2.8 to +42.6 pp; the
strategies are equivalent within ±2 pp (TOST) in 23 (saturation at low θ̄,
starvation at high θ̄ and low budget), and 3 cells are uncertain. No cell shows a
detected cluster advantage of practical interest (≥ 2 pp); the largest observed
cluster edge is 0.8 pp. Broadcast, which uses no seeds (it buys awareness, not
adopters), ends at 5.5 ± 3.4% (0.0% in the 12 runs without innovators;
independent panel).

**Under relapse, the advantage changes sign between the tested values
(Fig. 1b).** An adopter relapses with probability ρ per step while their
exposure stays below r·θ. The dispersion advantage decreases monotonically in ρ.
When retention requires full reinforcement (r = 1), the paired difference falls
from +8.4 pp [4.2, 12.7] at ρ = 0.10 to −5.3 pp [−9.0, −1.5] at ρ = 0.25 and
−11.4 pp [−14.8, −8.0] at ρ = 0.40. With weaker coupling (r = 0.5), reversal is
seen only at the highest tested rate (−7.7 pp [−11.5, −3.9] at ρ = 0.40). All
runs at ρ ≥ 0.25 ended in absorbing states, ruling out a horizon artifact.
Clustered adoption barely moves (32.4% to 29.3% under the harshest setting),
while dispersed adoption collapses (72.0% to 17.9%).

**The reversal depends on the endpoint.** At r = 1, ρ = 0.25, the terminal
contrast has reversed while the contrast in cumulative reach (secondary,
descriptive) remains inconclusive (−1.8 pp [−5.4, +1.8]); it is clearly negative
only at ρ = 0.40 (−7.4 pp [−10.7, −4.1]). The terminal reversal is therefore
driven mainly by differential retention, the share of ever-adopters who remain
adopters (0.99 for cluster vs. 0.86 for random).

**Robustness and a real topology, both without relapse.** Varying one parameter
at a time (N = 500, 2000, 8000; team size 5, 12; silo 0.5, 0.7, 0.95), the
paired difference ranges from +14.7 to +48.3 pp and no confidence interval
crosses zero. On the real email-Eu-core topology (986 nodes, 42 ground-truth
departments, all behavioral attributes synthetic), the mean paired difference
over 50 attribute draws is +13.5 pp [1.0, 26.0]; adoption there is bimodal, with
a low mode (median 9%) and a high mode (median 85%).

**Why, within the model.** A random seed, usually alone in its team, starts far
below its threshold and may relapse immediately; a fully seeded team can keep
its members well above their thresholds. Dispersed seeding must activate teams
before its seeds relapse, which becomes harder as ρ increases. The strategy that
spreads a practice best is thus not necessarily the one that sustains it best.

## What it does not show

- **Synthetic and uncalibrated.** Thresholds are unobserved, decay parameters
  are set on a grid and time is abstract (a step is one round of influence).
  The results are orderings inside this model family, not forecasts for any
  organization.
- **One organizational setting for the reversal.** The crossover was measured
  in a single organizational setting; the robustness variants and the
  email-Eu-core arm were run without relapse.
- **Located, not estimated.** The sign change lies between two tested values of
  ρ (0.10 and 0.25 at r = 1); no crossover value is estimated.
- **One confirmatory endpoint.** Terminal adoption is the only confirmatory
  endpoint; cumulative reach and retention are secondary and descriptive.
- **email-Eu-core is a sign replication** on a real modular topology with
  synthetic behavioral attributes, not a validation of the mechanism;
  magnitudes are not comparable across topologies.
- **No claim of optimality.** The four seeding rules were fixed in advance;
  influence maximization is out of scope.
- **The local predictor failed.** A local predictor of team ignition,
  pre-specified in the decision log, failed its validation criterion (AUC 0.64
  vs. 0.70) and does not sufficiently explain dispersed activation; team-level
  trajectories remain future work.

The complete list is in [docs/limitations.md](docs/limitations.md).

## How the evidence was produced

- **Model.** Two-tier synthetic organizations: a formal hierarchy (eight
  departments, eight people per line team on average; 249 teams, 2,000 people)
  and an informal influence network resembling a nested stochastic block model
  (nearly complete teams, about six ties per person to other teams of the same
  department — mostly adjacent "sister" teams — about 0.45 to other departments,
  plus sparse random ties). Thresholds follow a Beta distribution with mean 0.30
  and concentration κ = 20; an agent is an innovator (θ = 0) with probability
  0.025. Adoption requires being ready (credibility-weighted exposure share ≥ θ
  and > 0), willing (drawn once, p = 0.85) and able, a decomposition taken from
  Coale (1973). The main measure, terminal adoption, is the share of agents who
  are adopters when a run ends (absorbing state, or after 100 steps); cumulative
  reach is secondary. Specification: [docs/model.md](docs/model.md).
- **Strategies.** Random, champions (top informal degree), cluster (whole teams)
  and one-per-team (round-robin coverage), each with a budget of 100 seeds;
  broadcast uses no seeds and serves as the baseline.
- **Paired protocol (D19).** In each condition cell, every strategy runs on the
  same 50 freshly generated organizations with the same random numbers, so
  contrasts are paired differences within organizations. Pairing is used as a
  confounding control, not for precision.
- **Pre-specified families.** The two confirmatory families (regime map and
  decay grid) were pre-specified in the version-controlled decision log after an
  exploratory panel (n = 12 organizations per cell, not used in Fig. 1); seeds
  were frozen before execution. Holm correction is applied within each family,
  to the difference tests and to TOST equivalence against a practical band of
  ±2 pp (≈40 people). Each cell is a *win*, *equivalent* (within ±2 pp, for the
  tested cells and model) or *uncertain*.
- **Number provenance.** Every reported estimate is machine-extracted from the
  versioned results ([`paper/extract_numbers.py`](paper/extract_numbers.py) →
  [`paper/numbers.json`](paper/numbers.json)) and checked by an audit script
  ([`paper/audit_numbers.py`](paper/audit_numbers.py)).

## Reproduce

```bash
git clone https://github.com/PaulBufort/adoption-sim.git
cd adoption-sim
python3 -m venv .venv && source .venv/bin/activate        # Python ≥ 3.11
pip install -r requirements-dev.txt -c constraints.txt    # pinned versions
```

**The abstract's numbers and the panels of Figure 1, from the versioned
results** (re-analysis only, no simulation):

```bash
python experiments/cp1_analysis.py   # figures/exp1_crossover.png + paper/cp1/
python figures/make_fig_2panel.py    # figures/exp1_crossover_2panel.png (Figure 1)
python paper/extract_numbers.py      # paper/numbers.json
python paper/audit_numbers.py        # exit code 0 = every audited claim found
```

`figures/exp1_crossover_2panel.png` is Figure 1 exactly as embedded in the
abstract; its SHA-256 is pinned in [paper/README.md](paper/README.md). It is a
two-panel re-rendering of panels (a) and (b) of `figures/exp1_crossover.png`,
from the same paired CSVs and the same statistics; the three-panel version adds
an asymmetry panel (c). `figures/make_fig_2panel.py` regenerates it and
cross-checks every plotted value against `paper/numbers.json` (PNG bytes can vary
across platforms through font rendering).

**Re-running the simulations.** The seeds were frozen before execution (D19).

- `python experiments/run_experiment1.py`: the paired headline and the paired
  decay grid, plus the June 2026 independent-sample panels;
- `run_paired_regime` and `run_robustness` in
  [`experiments/exp1.py`](experiments/exp1.py): the paired regime map and the
  robustness variants (called from Python; no command-line wrapper);
- `python experiments/fetch_eucore.py`, then
  `python experiments/exp4_realgraph.py`: the email-Eu-core arm (the first
  command downloads the graph from SNAP).

**Earlier material (June 2026).** The notebooks
`experiments/01_broadcast_vs_cluster.ipynb`, `02_sanity_checks.ipynb` and
`03_observability.ipynb` still execute; `python figures/make_all.py` runs them
headlessly and regenerates the nine legacy figures, `figures/headline.png`
included. Their strategy comparisons use independent samples: for every seeded
strategy the abstract cites the paired runs only, and these panels remain a
cross-check and the source of the broadcast numbers. New here? Start with
[`experiments/00_tutorial.ipynb`](experiments/00_tutorial.ipynb).

Run the test suite with plain `pytest` from the repo root (119 tests). Prefer a
package? `pip install -e .` installs the engine as `adoption_sim` (NetworkX +
NumPy only).

## The web demo

**One click (macOS/Linux):** double-click **`Launch Demo.command`** at the repo
root — it creates the environment on first run, starts the server, and opens your
browser. Close the Terminal window to stop it.

Or from a shell:

```bash
streamlit run demo/app.py
```

Five controls (size, silo strength, mean threshold, strategy, seed budget) →
adoption curves vs the broadcast reference, a dead-pocket department map, and a
ready/willing/able attribution chart. Deployment to Streamlit Community Cloud:
[demo/README.md](demo/README.md).

## What's in the box

| path | contents |
|---|---|
| `core/` | engine — org generator, threshold dynamics, seeding, metrics, sweeps (independent and paired designs), ingest. **Imports NetworkX + NumPy + stdlib only** (enforced by a test) |
| `experiments/` | the paired pipeline (`exp1.py`, `stats.py`, `paired_io.py`, `cp1_analysis.py`, `exp4_realgraph.py`, predictor scripts) · four executed notebooks (tutorial · June 2026 strategy comparison · sanity checks · observability) · scenario TOMLs · versioned results (CSV + provenance JSON) |
| `paper/` | `extract_numbers.py` → `numbers.json` → `audit_numbers.py` · checkpoint arbitration records (`cp1/`, `cp3/`, `cp4/`) · provenance of the submitted abstract ([paper/README.md](paper/README.md)) |
| `figures/` | `exp1_crossover_2panel.png` (Figure 1 of the abstract, from `make_fig_2panel.py`) · `exp1_crossover.png` (three-panel version, from `experiments/cp1_analysis.py`) · nine legacy figures regenerated by `make_all.py`, including `headline.png` |
| `demo/` | Streamlit app (synthetic-data banner included) |
| `docs/` | [spec](docs/spec.md) · [model math](docs/model.md) · [assumptions](docs/assumptions.md) · [limitations](docs/limitations.md) · [decision log](docs/decisions.md) · [sanity checks](docs/sanity-checks.md) · [build journal](docs/journal.md) |
| `tests/` | 119 tests: threshold rule on hand-computed graphs, state conservation, determinism (parallel ≡ serial), paired-design identities, statistics, seeding budgets, stack policy, demo smoke |
| `RESULTS_VERIFIED.md` | verification record: canonical paired numbers, corrigenda, superseded claims flagged rather than deleted |

## The science, honestly

- **Every modeling choice that affects claims is logged** in
  [docs/decisions.md](docs/decisions.md) with its alternatives and trade-offs:
  D1–D17 **RATIFIED** at the 2026-06-10 arbitration, D18–D23 at the 2026-08-02/03
  CN2026 checkpoints (paired protocol, regime map, decay crossover, email-Eu-core
  replication, corrigenda).
- **Results that went against expectations stay on the record**: without decay,
  the "seed clusters" heuristic is not reproduced (Fig. 1a); socially reinforced
  decay lowers plateaus but never draws an overshoot-then-sag adoption curve (D7);
  no single relay person is load-bearing in generated organizations (D12); making
  pilot teams visible does not rescue cluster seeding (D17, experiment 3); the
  local ignition predictor failed its pre-specified gate (D21).
- **Corrections are kept visible, not edited away.** The June 2026 "parity, not
  reversal" verdict under decay, from an unpaired design that could not resolve
  the contrast, is superseded and flagged in
  [RESULTS_VERIFIED.md](RESULTS_VERIFIED.md); retracted wordings remain in the
  decision log next to their corrigenda (D17(a), D19(b), D22(a), D23).
- **Sanity checks**: Granovetter's knife-edge, Centola & Macy's weak-long-ties
  result and Watts' cascade condition replicate qualitatively, and the θ/v
  visibility equivalence holds exactly
  ([docs/sanity-checks.md](docs/sanity-checks.md)).
- **Every figure states that its data is synthetic.**

## Requirements & license

Python ≥ 3.11. Runtime: NetworkX, NumPy, Streamlit (dependency policy: nothing else;
additions must be justified). Dev: + matplotlib, jupyterlab, pytest.

**AGPL-3.0** — see [LICENSE](LICENSE). Cite via [CITATION.cff](CITATION.cff), which
also lists the extended abstract.

*Status: research code accompanying the CN2026 extended abstract. Calibration on
real organizational data is explicitly out of scope ([spec](docs/spec.md) §1).
Time steps are abstract influence rounds.*
