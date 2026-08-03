# RESULTS_VERIFIED.md

## v3 — CP3 corrigenda (2026-08-03, S3.3): claim corrections, zero data change

> Independent review (CP3, Opus, on commit `5346724`) found two published
> formulations the data do not support. **No simulation was re-run; every
> CSV and every paired number below stands bit-identical. The paper figure
> (`figures/exp1_crossover.png`) and the other CP1 artifacts are
> bit-identical; `paper/cp1/fig_eucore.png` alone was regenerated to correct
> its title ("bimodal ignition lottery" → "bimodal outcomes", D22(a)) — same
> data, new label.** The corrections are to claims, not results (full
> arbitration: decisions.md D23).

1. **Pairing rationale corrected (D19(b)).** "Shared between-organization
   variance (9–16 pp) drops out" is retracted. Pairing guarantees
   *confounding control* (identical organizations and agent draws per
   contrast), not variance reduction: realized random↔cluster correlations
   are weak (median ≈ +0.18 over the 58 paired cells; −0.09 at the headline
   cell, where the paired sd is 14.9 pp vs ≈14.3 pp independent-equivalent).
   All published CIs are unchanged — they were always computed from the
   paired differences themselves.
2. **email-Eu-core "ignition in 62% vs 42% of draws" retracted (D22(a)).**
   The ≥10% cut was post hoc and sits inside the low mode of a bimodal
   distribution (pooled mode medians 9.2%/84.6%; no draw between 20.2% and
   82.0%). The paper now reports the bimodal shape and the pre-declared
   +13.5 pp [1.0, 26.0] contrast only. No replacement cut adopted;
   `numbers.json` `eucore.ignition_share` → `eucore.modes` (largest-gap
   split, descriptive). The v2 bullet below stays as the historical record.
3. **Crossover endpoint-dependence made explicit (no new claim family).**
   Terminal adoption (confirmatory) reverses at (r=1, ρ=0.25): −5.3 pp
   [−9.0, −1.5]. Cumulative reach (secondary descriptive, pointwise
   uncorrected) is still uncertain there: **−1.8 pp [−5.4, +1.8]**, and is
   clearly negative (pointwise CI excluding zero) only at ρ=0.40:
   **−7.4 pp [−10.7, −4.1]** — both computed from
   the versioned `exp1_decay_paired_headline.csv`. The terminal reversal at
   ρ=0.25 is therefore driven mainly by differential retention (0.99 vs
   0.86). The paper states this; the crossover-location sentence remains
   scoped to terminal adoption.
4. Bookkeeping: regime map gains `largest_cluster_edge` (−0.76 pp at
   θ̄=0.35/1%, the only Holm-significant cluster-favoured contrast; classed
   equivalent); audit extended **35 → 42 claims**; abstract counts now sum
   to 40 (14 wins / 23 equivalent / 3 uncertain).

## v2 — Paired S2 verification and the crossover finding (2026-08-02, CP1)

> The **canonical numbers are now the PAIRED results** (D19, ratified at CP1):
> single successful full-pipeline execution of the paired protocol (6 350
> simulations, frozen seeds,
> master 20260610 / exp4 (20260610, 4)); a control re-run of the paired
> headline was **bit-identical**; the mechanical regeneration of the 8 legacy
> CSVs (adding the cumulative_rate / retention_rate / seeded_teams columns)
> was verified **bit-identical on every historical column**. Sources:
> `experiments/results/exp1_paired_headline.csv`, `exp1_regime_paired_headline.csv`,
> `exp1_decay_paired_headline.csv`, `exp1_robustness_headline.csv`,
> `exp4_eucore.csv`; analysis `experiments/cp1_analysis.py`; manuscript trace
> `paper/extract_numbers.py` → `paper/numbers.json` → `paper/audit_numbers.py`
> (35 claims verified). Technical note: one earlier pipeline launch aborted on
> a multiprocessing/stdin issue before any CSV was written
> (`paper/cp1/CP1_ARBITRATION.md` §7).

### ⚠ FLAGGED CONTRADICTION with the 2026-06-17 verification below

The v1 verdict "**parity, not reversal** under decay (cluster−random +0.9 pp,
95% CI [−8.1, +10.0], n=12 unpaired)" is **superseded**: the paired n=50
design resolves what that ±9 pp interval could not. At the very parameters of
the old decay run (r=1.0, ρ=0.25), the paired contrast is a **significant
modest reversal**: random − cluster = **−5.3 pp, 95% CI [−9.0, −1.5]**
(Holm-corrected within the pre-declared 7-contrast family; horizon effects
excluded — 98–100% of runs reach their fixed point in ~30–45 steps). The full
family shows an ordered **crossover**: +39.6 pp at ρ=0 → sign flip between
ρ=0.10 and 0.25 (r=1.0; later for r=0.5) → −11.4 pp at ρ=0.40. Nothing was
re-run with new seeds; the old CSV remains reproducible; the old *conclusion*
was a power limitation, not a data error. Also superseded: the two n=12
cluster-favoured regime cells (−1.2/−0.6 pp, uncorrected) — under n=50 +
Holm + the ±2 pp band, **no cell where cluster wins survives** (14 dispersion
wins / 23 equivalences / 3 uncertain). Rounding note: one_per_team−random CI
lower bound is −5.045 → quoted as −5.0 (an earlier −5.1 was a
double-rounding artifact).

### Canonical paired numbers (95% CIs; n=50 organization pairs)

- Headline (θ̄=0.30, 5%, κ=20, no decay): random 72.0±9.2%, champions
  75.9±8.2%, cluster 32.4±11.0%, one_per_team 70.6±10.4% (terminal adoption,
  mean±sd); **random − cluster +39.7 pp [35.4, 43.9]**; champions − random
  +3.9 pp [0.6, 7.1] (descriptive); one_per_team − random −1.4 pp
  [−5.0, +2.2] ("no clear difference", D20 amendment). Broadcast 5.5±3.4%
  and exactly 0.0% ×12 at p_innov=0 (independent panel — the only two
  independent-panel citations, per the D19 source policy).
- Regime map (40 cells): 14 dispersion wins (+2.8 to +42.6 pp; headline cell
  +42.6 [39.1, 46.0], an independent paired sample), 23 TOST-equivalent
  within ±2 pp, 3 uncertain, 0 cluster wins.
- Decay family (terminal adoption): see crossover above; secondary
  descriptive at (r=1, ρ=0.25): cumulative reach random 29.0% vs cluster
  30.9%; retention ratio 0.86 vs 0.99.
- Robustness (one-at-a-time, paired): Δ from +14.7 [9.8, 19.7] (N=500) to
  +48.3 [46.5, 50.1] (N=8000); all 8 CIs exclude zero.
- email-Eu-core (real topology, synthetic attributes, D22): random − cluster
  +13.5 pp [1.0, 26.0]; ignition in 62% vs 42% of draws **[the "ignition"
  label is retracted at v3 — D22(a); cut inside the low mode]**; SIGN
  replication only.
- Predictor (D21): verdict **no_go** — V1 pooled AUC 0.642 < 0.70 (12 789
  units), V2 sign agreement 14/14; per-strategy AUCs descriptive (cluster
  0.996, dispersed 0.59–0.69).

The v1 report below is retained verbatim as the historical record of the
2026-06-17 verification.

---

> Clean-room re-verification of the v0.1 headline numbers, run **2026-06-17**.
> Method: full integral re-run of every condition from scratch via
> `figures/make_all.py` (executes notebooks 01/02/03 → regenerates all CSVs and
> all 9 figures) followed by `paper/extract_numbers.py` → `paper/numbers.json`.
> **All data synthetic** (docs/limitations.md). Every value below is machine-derived
> from the versioned CSVs in `experiments/results/`; none is hand-entered.

## Headline verdict

- **The re-run reproduces every committed CSV, every figure PNG, and `numbers.json`
  BIT-FOR-BIT.** `shasum -a 256` over all 12 result CSVs, `paper/numbers.json`, and
  the 9 figure PNGs is identical before and after the re-run. Only re-executed
  notebooks and `.meta.json` provenance sidecars (timestamps/host) changed.
- **67/67 unit tests pass.**
- **Reproducibility: 93 s** clone-state → all figures + numbers (target < 15 min — met
  with large margin; consistent with README's 113 s fresh-clone measurement).
- **Demo is already in sync** with the ratified config (silo 0.85, θ̄ 0.30, κ=20 in
  captions, budget 5 %, 2.5 % innovators, visibility slider default v=1.0). The
  CLAUDE.md "currently stale" note is itself stale — no demo change needed.
- **Notebook 01 footer is already RATIFIED** (0 occurrences of PROVISIONAL; the
  provenance footer prints "D1–D17 RATIFIED 2026-06-10"). That objective is done.

## ⚠ Numbers cited in CLAUDE.md are from the pre-release **20-replicate** era; the repo is now **50-replicate**

The D16 release-sprint directive raised headline replicates **20 → 50** for figure
precision (recorded in `experiments/scenarios/headline.toml:3` and the D16 entry).
That precision bump shifted several headline means by a few points. **The 50-rep
values are the current machine truth** and already feed the paper (`numbers.json`).
The cited values in CLAUDE.md / README were never updated. Per the honesty rule I am
flagging these loudly rather than silently editing code or docs.

### Headline strategy reach, κ=20 (`exp1_strategies_headline.csv`, n=50)

95% CI computed as mean ± t₀.₉₇₅(df=49)·sd/√n (sample sd, ddof=1).

| Quantity | CLAUDE.md cited | Verified (50-rep) | 95% CI | Δ | Status |
|---|---|---|---|---|---|
| broadcast | 5.8 % | **5.50 %** (sd 3.42) | [4.52, 6.47] | −0.3 pp | CORRECTED (stale) |
| random | 73 % | **69.54 %** (sd 11.18) | [66.36, 72.72] | −3.5 pp | CORRECTED (stale) |
| champions / "hubs" | ~75 % | **73.37 %** (sd 7.10) | [71.35, 75.39] | −1.6 pp | confirmed (≈) |
| cluster | 29 % | **31.93 %** (sd 9.28) | [29.29, 34.56] | +2.9 pp | CORRECTED (stale) |
| line-manager-first | 60 % | **61.57 %** (sd 16.38) | [56.92, 66.23] | +1.6 pp | confirmed (≈) |

Non-overlap still holds: broadcast max (14.5 %) < cluster min (17.1 %); broadcast and
cluster CIs are nowhere near touching. Qualitative story intact: broadcast stalls;
scattered (random/champions) ≫ cluster.

**Robustness caveat (honest):** champions [71.35, 75.39] and random [66.36, 72.72]
**overlap** in [71.35, 72.72] — champions is nominally higher but the two are **not
cleanly separable** at n=50. The robust claim is "scattered (random *and* champions)
≫ cluster ≫ broadcast", not "champions > random".

### Other cited numbers

| Quantity | CLAUDE.md cited | Verified | Status |
|---|---|---|---|
| broadcast @ p_innov=0 | 0.0 % | **0.000 %** (n=12, exact across all reps) | ✅ EXACT |
| broadcast @ T_b=20 | 13.5 % | **11.6 %** (sd 7.0, n=50) | CORRECTED (stale, −1.9 pp) |
| no-innovator random vs cluster | 42 % / 20 % | **41.5 % / 20.0 %** (n=12) | ✅ confirmed |
| decay reversal — random | 73 → 26 | **69.5 → 30.2** (−56.6 %, n=12) | CORRECTED (stale) |
| decay reversal — cluster | 29 → 32 | **31.9 → 31.1** (−2.7 %, n=12) | CORRECTED (stale) |
| visibility collapse threshold | v ≈ 0.6 | random 6.6 % @v=0.6 → 12.6 % @v=0.8 → 69 % @v=1; collapse in (0.6, 0.8] | ✅ confirmed (qualitative) |
| θ→θ/v equivalence theorem | exact | regenerated `exp3_equivalence.png`; exact assert in `test_visibility.py` | ✅ confirmed |
| loud-pilot Δreach (hubs/dispersed/cluster) | +15 / +10 / +4 | champions **+15.0** / random **+9.5** / cluster **+4.0** pp @v=0.8 | ✅ confirmed |
| outbound credibility/seed (team vs hub) | 5.7 / 16.1 | cluster **5.69** / champions **16.11** (random 11.74) | ✅ confirmed |
| barbell bridge removal (positive control) | −45 pts | relay knockout cuts clique B (5/11 ≈ 45 % of mass); `test_pivot…` asserts Δplateau > 0.3 | ✅ confirmed (mechanism) |
| top-12 central removal (pivot null, D12) | ≈ no effect | null result holds; no single node load-bearing | ✅ confirmed |

### ⚠ Statistical robustness of the decay claim (ULTRATHINK, n=12)

The cited "decay reversal" (random 73→26 < cluster 29→32, an *ordering reversal*)
came from the D7 amendment's 8-rep illustrative scan (ρ=0.25). Tested against the
**committed** decay CSV (`exp1_decay_headline.csv`, n=12) with the 50-rep no-decay
baseline, the ordering reversal is **NOT statistically supported**:

| Comparison | Result | Verdict |
|---|---|---|
| random under decay | 30.15 % [24.74, 35.56] | — |
| cluster under decay | 31.07 % [23.12, 39.02] | — |
| **cluster − random** (under decay) | **+0.92 pp**, Welch t=0.21, 95% CI of diff **[−8.13, +9.98]** | **NOT distinguishable (CI straddles 0)** |
| random decay-drop | 69.54 → 30.15 % = **−39.4 pp**, t=−13.5 | **highly significant** |
| cluster decay-drop | 31.93 → 31.07 % = **−0.85 pp**, t=−0.22 | **not significant (decay-proof)** |

**Honest restatement of the message.** Decay *differentially punishes* scattered
seeding: **random collapses** (−39 pp, robust) while **cluster is unaffected**
(−0.9 pp, NS). The two thereby reach **statistical parity** under decay — cluster
does **NOT** significantly overtake random at the committed ρ. The stronger "cluster
*wins* / ordering reverses" framing only holds at higher relapse (the D7 text notes a
clean reversal at ρ=0.40, a scenario not in the committed headline CSV). I did **not**
adjust any parameter to recover the reversal; the parity result stands as measured.

This means: `docs/limitations.md` #16 ("Cluster seeding wins on *retention under
decay* instead") is slightly **overstated** at committed params — it reaches parity,
not a win. Flagged for your call; not edited (it is a maintained docs file, and the
underlying differential-robustness claim — cluster is decay-proof, random is not — is
fully supported).

### κ=12 lottery companion (`exp1_kappa12_headline.csv`, n=50)

broadcast **19.8 %** (sd 12.5) — the high-variance "lottery" regime, as documented
in D1/D16. random 80.4 %, champions 81.1 %, cluster 49.6 %, line-manager 79.6 %.

## Parameters re-confirmed (against `core/defaults.py` + `headline.toml`)

| Param | Stated | Verified |
|---|---|---|
| nodes | 2000 | ✅ 2000 |
| departments | 8 | ✅ 8 |
| mean team size | ~8 | ✅ 8 |
| innovators (θ=0 atom) | 2.5 % | ✅ 0.025 |
| willing | 85 % | ✅ 0.85 (all roles) |
| able | 100 % | ✅ 1.0 |
| credibility 1.0/0.6/0.7/0.3 | peer_close/peer_far/manager/comms | ✅ 1.0 / 0.6 / 0.7 / 0.3 |
| mean θ | 30 % | ✅ 0.30 |
| κ (theta_concentration) | 20 | ✅ 20.0 |
| seed budget | 5 % (100/2000) | ✅ 0.05 |
| silo strength | 0.85 | ✅ 0.85 |
| team locality | 0.7 | ✅ 0.7 |
| dept degree | 6.0 | ✅ 6.0 |
| **replicates** | **"20 graphs × 20 runs"** | ⚠ now **50** full-regeneration replicates (D14 semantics: each replicate = a fresh org). The "20×20" description is stale. |
| master seed | — | 20260610 |

## Stale-citation grep — full inventory (2026-06-17)

Searched whole repo for distinctive 20-rep values (5.8, 13.5, 73, 29, 73→26, "20 graphs × 20 runs").

**Corrected on branch `align-50rep-numbers` (this change):**
- `CLAUDE.md` — numbers block, replicate description, "Current objective" block.

**Already aligned (no change needed):**
- `README.md` — already shows 50-rep values (~6 %, cluster ~32 %, lottery 5–65 %,
  "50 replicates"); confirmed by REVIEW_A.md. Re-verified clean.
- `experiments/01_…ipynb` "champions ≈ 73%" (correct: 73.4 %) and the `:414` code
  output (`random 67.7% cluster 28.9%`, the n=12 p_innov sweep — correct for that sweep).

**Stale but NOT edited — left for your decision (outside the CLAUDE.md/README scope):**
- `experiments/03_observability.ipynb:244` caption — "random 73% → 13%, cluster 29% → 11%";
  should read "random 69% → 13%, cluster 28% → 11%" (50-rep / global-v). Text-only but
  changes the committed notebook — flag for OK.

**Deliberately NOT edited — historical/ratified records (editing would falsify them):**
- `docs/journal.md:162,224,234` — dated log entries; record what was measured at the time.
- `docs/decisions.md:267` — D7 amendment text (RATIFIED): the "0.73→0.26 / 0.29→0.32"
  8-rep scan. Ratified = fixed; the parity caveat is recorded here instead.

## Recommended follow-ups (need your sign-off)

1. **DONE on branch:** cited numbers in `CLAUDE.md` aligned to verified 50-rep values,
   with honest decay framing (parity, not reversal). Diff awaiting your OK before push.
2. **Your call:** fix the `03_observability.ipynb:244` caption (73/29 → 69/28).
3. **Your call:** soften `docs/limitations.md` #16 ("cluster wins on retention") to
   "cluster is decay-proof; reaches parity with random under decay". Not done.

No figures were regenerated *as a change*: the clean-room run reproduced all 9 PNGs
bit-identically, so there is nothing to commit on the figure side.
