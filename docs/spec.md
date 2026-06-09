# Simulator v0.1 — Technical Specification

> Working name: `adoption-sim` (rename when the project name is decided).
> Python research simulator of complex contagion on organizational networks.
> Build: ~10 weeks at ~6 h/week, AI-assisted. License: AGPL-3.0. Repo private until v0.1 release.

---

## 1. Goal and scope

**Question v0.1 answers:** on a realistic simulated organization, when does a broadcast-style
rollout fail where cluster-based seeding succeeds — and which structures (silos, thresholds,
relays) determine the outcome?

This is a demonstration and intuition instrument. Calibration on real organizational data is
**out of scope** for v0.1.

**In scope:**
- Parameterizable synthetic organizational graphs
- Complex-contagion dynamics with thresholds
- Ready / willing / able agent states
- Comparative seeding strategies
- Output metrics and visualizations
- Reproducible notebooks, simple web demo

**Out of scope (v0.1):**
- LLM personas
- Real company data
- Production UI
- Any calibration pipeline

---

## 2. Model specification

### 2.1 Topologies (the terrain)

- **Synthetic organization generator:** hierarchical blocks (departments/teams) via a
  stochastic block model, plus a parameterizable rate of cross-silo ties. Size: 200–20,000
  nodes. Node attributes: unit, role (line manager / individual contributor / leadership),
  simulated tenure.
- **Two layers, deliberately distinct:**
  - *Formal layer* — the org chart (hierarchy). Broadcast messages travel here.
  - *Informal layer* — the real influence network (homophily + proximity + noise). Adoption
    travels here.
  The divergence between the two layers is the core demonstrative device.
- **Real public graphs import** (edgelist / GraphML): e.g. the Enron e-mail corpus and other
  published intra-organizational networks (SNAP, ICON). Demonstration use only.

### 2.2 Dynamics (the contagion)

- **Fractional threshold model** (Granovetter / Watts): an agent adopts when the share of its
  credible contacts having adopted ≥ threshold θ. θ drawn from a parameterizable distribution
  (mean per role, heterogeneity parameter).
- **Ready / willing / able decomposition:**
  - *ready* — sufficient exposure (the threshold condition; a network property)
  - *willing* — individual disposition (perceived cost, drawn randomly, modulated by role)
  - *able* — practical capacity (tool access/time; a unit-level parameter)
  Adoption requires all three. Every non-adoption is attributable to one missing condition,
  which makes diagnostic maps legible.
- **Reinforcement and decay:** exposures weighted by source credibility (close peer > manager
  > central comms); optional de-adoption when usage is not reinforced (retention parameter) —
  reproduces the documented "spike then relapse" pattern.
- **Seeding strategies compared:** broadcast (everyone exposed once) · random seeding ·
  champions (by centrality) · cluster seeding (dense per-unit clusters) · line-manager-first.

### 2.3 Output metrics

- Adoption curve (speed, plateau, relapse)
- Final adoption rate per unit
- Dead-pocket map (units below critical mass)
- Pivot nodes (relays whose removal changes the plateau)
- Parameter sensitivity (tornado chart)

---

## 3. Architecture and stack

| Component | Choice |
|---|---|
| Language / core | Python 3.12; NetworkX for graphs; custom simulation loop (simpler to master than mesa); NumPy; multiprocessing for parameter sweeps |
| Reproducibility | one Jupyter notebook per experiment; fixed seeds; YAML config per scenario; versioned results (CSV/parquet) |
| Visualization | Matplotlib/Plotly; simplified network views (sampling beyond 2,000 nodes) |
| Web demo | Streamlit Community Cloud (free): 4–5 sliders (size, silo strength, mean threshold, strategy, seed %) → curves + unit map. Pedagogical demo, by design |
| Repo layout | `/core` (engine) · `/experiments` (notebooks) · `/demo` (streamlit) · `/docs` (model, assumptions, limitations) · AGPL-3.0 · CITATION.cff |
| Quality | 15–20 unit tests on the core (graph creation, threshold rule, state conservation); basic GitHub Actions CI |

**Dependency policy:** NetworkX + NumPy + Streamlit cover everything. Every added dependency
is debt and must be justified in the PR description.

---

## 4. Build plan — milestones

With an agentic coder (Claude Code / Fable 5), the table below is a sequence of **review
gates**, not coding weeks: the agent builds toward each milestone autonomously; the human
reviews `docs/decisions.md`, arbitrates PROVISIONAL modeling choices, and must be able to
defend every scientific assumption before the next gate. Weekly human budget (~6 h) goes to
review and decisions, not code.

| Week | Objective | Milestone |
|---|---|---|
| W1–W2 | Freeze spec; repo skeleton; organizational graph generator + tests | a 1,000-node org graph, visualized |
| W3–W4 | Contagion engine: thresholds + R/W/A states + decay | a reproducible adoption curve on a toy scenario |
| W5 | Seeding strategies + parallel parameter sweep | comparison table: broadcast vs cluster seeding |
| W6 | Advanced metrics (dead pockets, pivot nodes) + clean visualizations | diagnostic maps |
| W7 | Experiment 1 notebook finalized (broadcast vs cluster seeding) | the headline figure |
| W8 | Real public graphs import + qualitative replication of known literature results (documented sanity checks) | sanity-check report in `/docs` |
| W9 | Streamlit demo + `/docs` (assumptions, limitations) | public demo online |
| W10 | Polish: README, CITATION, examples | v0.1 release (repo flips public) |

---

## 5. Definition of done

**v0.1:** a competent stranger clones the repo, runs experiment notebook 1 in under 15 minutes,
and reproduces the headline figure. The web demo runs online. Limitations are stated in
`/docs` in plain language.

**v1 (later):** + a historical backtest experiment (stylized diffusion fronts of the European
fertility transition) + a second experiment.

---

## 6. Honesty requirements (non-negotiable)

- `/docs/limitations.md` exists from W1 and grows with the project.
- Synthetic ≠ calibrated: every figure caption states the data is synthetic.
- Negative or null results in experiments are reported, not deleted.
