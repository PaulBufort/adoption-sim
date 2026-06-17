# CLAUDE.md — adoption-sim

> Project memory for Claude Code. Read this first, then `docs/`, before editing anything.

## What this repo is
A Python **research simulator** of complex contagion (costly-behaviour adoption) on synthetic
**two-layer organizational networks**. It is a demonstration and intuition instrument, **not** a
calibrated predictor. First use case: why enterprise AI rollouts fail — "the Broadcast Fallacy".

## Source of truth (read before touching code)
- `docs/decisions.md` — ratified modelling decisions + rationale. **RATIFIED decisions are fixed**; do not silently revisit them.
- `docs/limitations.md` — assumptions and known limits. Keep current.
- `spec.md` / `README.md` — scope and architecture.
The **repo**, not any chat history, is the source of truth.

## Current objective — v0.1 hardening (COMPLETE; see `RESULTS_VERIFIED.md`)
The v0.1 hardening items below are done and verified by a clean-room re-run:
1. **Streamlit demo** (`demo/`): in sync with the ratified config (silo 0.85, θ̄ 0.30, κ=20, budget 5%, 2.5% innovators, visibility v=1.0). ✅
2. **Notebook 01**: footer status `RATIFIED` (provenance footer prints D1–D17 RATIFIED). ✅
3. **Reproducibility**: clone-state → all figures + numbers in **~93 s** (target < 15 min). Fixed seeds, `constraints.txt` pinned. ✅
4. **`docs/` + `CITATION.cff`**: complete and mutually consistent (CITATION schema-valid). ✅
5. **Key numbers**: re-confirmed against a clean run; all CSVs/figures/`numbers.json` reproduce **bit-for-bit**. ✅

## Confirmed key numbers (50-replicate, machine-derived)
Source of truth: `paper/numbers.json` (regenerate via `figures/make_all.py` → `paper/extract_numbers.py`).
Full deltas-vs-cited and 95% CIs are in `RESULTS_VERIFIED.md`. Values below are means with 95% CI.
- Broadcast reach **5.5%** [4.5, 6.5] (κ=20); **0.0%** at p_innov=0 (exact); **11.6%** [9.6, 13.6] at T_b=20
- random **69.5%** [66.4, 72.7] · champions **73.4%** [71.4, 75.4] · cluster **31.9%** [29.3, 34.6] · line-manager **61.6%** [56.9, 66.2]
- no-innovator: random **41.5%** [35.3, 47.6] vs cluster **20.0%** [17.2, 22.9]
- decay (committed params, n=12): **scattered seeding is differentially punished** — random **69.5→30.2%** (−39 pp, highly significant) while cluster **31.9→31.1%** (−0.9 pp, not significant). Under decay random and cluster reach **statistical parity** (diff +0.9 pp, 95% CI [−8, +10]); cluster does **not** significantly overtake random at these params — do not claim an ordering "reversal" without a higher-ρ scenario (see `RESULTS_VERIFIED.md`).
- visibility: reach fully collapsed to the broadcast floor (~6%) for **v ≤ 0.6**; sharp transition in (0.8, 1.0]; theorem: global v ≡ rescaling θ→θ/v (D17 invariant, exact test)
- loud-pilot Δreach @v=0.8: champions **+15** · dispersed **+10** · cluster **+4**; outbound credibility/seed: cluster **5.7** · random **11.7** · champions **16.1**
- barbell bridge removal (positive control): relay knockout cuts off ~45% of mass (Δplateau > 0.3, unit-tested); top-M central removal ≈ no effect (D12 null)

Params (verified): 2000 nodes · 8 depts · teams ~8 · innovators 2.5% (θ=0) · willing 85% · able 100% · credibility 1.0/0.6/0.7/0.3 · mean θ 30% · κ=20 · seed budget 5% (100/2000) · silo 0.85 · locality 0.7 · **50 full-regeneration replicates** (D14; each replicate = a fresh org. The earlier "20 graphs × 20 runs" wording is superseded.).

## Figures (regenerated; bit-identical to committed PNGs)
- **F1** final reach by strategy (bars + CI) — exp.1
- **F2** reach vs retention under decay (random vs cluster)
- **F3** visibility phase curve (reach vs v; collapse < ~0.6)
- **F4** outbound credibility by seed type + loud-pilot Δ
- ⚠ **Do NOT** present a "spike & decay" curve as model output — it does not emerge from the model (stated limitation).

## Honesty requirements (non-negotiable)
- Synthetic ≠ calibrated: every figure caption says the data is synthetic.
- Report negative/null results; never delete them.
- If a re-run contradicts a cited number, **flag it loudly** in `RESULTS_VERIFIED.md` — never quietly edit code to match the old number.

## Conventions
- Stack: Python 3.12, NetworkX, NumPy, custom sim loop; Streamlit for the demo. Every new dependency is debt — justify it in the PR.
- One notebook per experiment; fixed seeds; YAML config per scenario; versioned results (CSV/parquet).
- 15–20 unit tests on the core (graph creation, threshold rule, state conservation); CI green before release.
- License **AGPL-3.0**. **Keep the repo private until the v0.1 release.**

## Working method
- Read the repo and **propose a short plan before editing**; list any decisions that need human arbitration.
- Small, reviewable commits with clear messages. Pushing follows the user's normal workflow.
- **Pause for explicit human review before**: (a) any commit that changes a scientific result or figure, (b) flipping repo visibility to public, (c) editing git author/identity config.
