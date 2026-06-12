# REVIEW B — paper claims audit (COMPLEX NETWORKS 2026 extended abstract)

> For the scientist, before submission (deadline 2026-09-02 AoE). Every claim in
> `paper/main.tex` that you must be able to defend orally, mapped to its
> evidence. All numeric values flow from `paper/numbers.json`
> (regenerate: `python paper/extract_numbers.py`); notebooks 01 and 03 are the
> source of truth. One premise correction is flagged at the bottom.

## 1. Claim → evidence map

| # | Claim in the paper | Evidence | numbers.json key |
|---|---|---|---|
| C1 | Broadcast stalls at 5.5±3.4% (range 1.8–14.5%), κ=20 | notebook 01 §3, Fig. 1 left; 50 reps | `headline_k20.broadcast` |
| C2 | Cluster reaches 31.9±9.2%; distributions don't overlap (broadcast max 14.5% < cluster min 17.1%) | notebook 01 §3, Fig. 1 left | `headline_k20.cluster`, `nonoverlap_k20` |
| C3 | Scattered dominates reach: random 69.5±11.1%, champions 73.4±7.0% | notebook 01 §3, Fig. 1 | `headline_k20.random/.champions` |
| C4 | κ=12: broadcast is a lottery 19.8±12.5% (range 4.9–64.5%); ordering unchanged | notebook 01 §3, Fig. 1 right | `headline_k12.*` |
| C5 | At p_innov=0 broadcast converts **exactly 0.0% in every replicate** | notebook 01 §4, Fig. 2; 12 reps, max=0 across all | `pinnov.broadcast@p=0` |
| C6 | At p_innov=0 random still beats cluster (41.4±9.3% vs 20.1±4.3%) | notebook 01 §4 (refutes the innovator-subsidy hypothesis — D16 mechanism amendment) | `pinnov.random@p=0`, `pinnov.cluster@p=0` |
| C7 | 20-step campaign lifts broadcast only to 11.6% | notebook 01 §5 (T_b sweep, 50 reps) | `tb.Tb=20` |
| C8 | Decay: random −57%, champions −40%, cluster −2.7% (31.9→31.1%) | notebook 01 §9, Fig. 3; ρ=0.25, 12 reps vs 50-rep no-decay baseline | `decay_drop_pct`, `decay.*` |
| C9 | No "spike-then-relapse" shape exists under social decay (negative result) | notebook 01 §9 finding 1; D7 amendment in decisions.md | — (qualitative) |
| C10 | θ/v equivalence is **exact**, incl. decay, broadcast-free | `tests/test_visibility.py::test_theta_over_v_equivalence_exact` (bit equality) + notebook 03 §1 witness (max \|Δ\| = 0.0) | — (theorem + test) |
| C11 | At v ≤ 0.6 no strategy exceeds 8.8% | notebook 03 §2 (global-v sweep, 12 reps) | `globalv.*@v=0.6` (max = champions 0.0877) |
| C12 | Broadcast is exempt from v (comms term not attenuated) | model definition (D17; Eq. 1 in paper); notebook 03 §2 | — (by construction) |
| C13 | Observable pilots: +4.0 / +9.5 / +15.0 pp (cluster/random/champions) at v_global=0.8 | notebook 03 §3, Fig. 4; 12 reps | `pilot_gain_pp_at_v0.8` |
| C14 | Outward credibility per seed 5.7 / 11.7 / 16.1 (the mechanism) | notebook 03 §3 mechanism cell; independently recomputed by `extract_numbers.py` (same seeds 900–904) | `outward_credibility_per_seed` |
| C15 | Knockouts of top-12 betweenness nodes (incl. CEO) shift plateau < replicate noise; barbell positive control fires (~50 pp) | notebook 01 §10; D12 amendment | — (notebook output) |
| C16 | One master seed; CI re-executes notebooks and fails on any CSV change | `.github/workflows/ci.yml` reproduce-headline job; two green runs on GitHub Linux runners (REVIEW_A §2) | — |
| C17 | Model spec as stated (weights 1.0/0.7/0.6/0.3; Beta(μ=0.30,κ); 2.5% innovators; willing 0.85; budget 5%; N=2000; 50 reps) | `experiments/scenarios/headline.toml`; `docs/model.md`; D1–D9, D16–D17 RATIFIED | `scenario` |

Oral-defense tip: C5 and C10 are the two claims with the word "exactly" — both
are machine-checked (12/12 replicates literal zero; bit-equality test). Say
"machine-verified", not "approximately".

## 2. The 3 weakest points a referee will attack

1. **"Your negative result is an artifact of your generator."** The
   scattered-beats-cluster finding is demonstrated on ONE synthetic family
   (near-clique teams of ~8, ring-adjacent sister bridges, SBM departments).
   A referee can argue the team-as-latent-cluster mechanism is baked in by
   the p_team=0.9 cliques. *Defense:* the mechanism is the point (modularity
   is the empirical norm in organizations); robustness shown to uniform
   credibility weights, locality 0.4–0.9, and p_innov=0 (sanity-checks.md).
   *Honest concession:* no real-topology replication of the headline is in
   the paper — the Enron demo (notebook 02) shows the same qualitative
   ordering (broadcast 15% < cluster 24% < random 49%) but with synthetic
   agents on a fixed graph, and is not cited as evidence. This is the first
   thing to fix for the full-paper version.
2. **"The orderings are regime-local; you chose the regime."** All headline
   claims live at θ̄=0.30, κ∈{12,20}: at low/tight thresholds everything
   saturates and no strategy differs; at high thresholds everything dies
   (D16 logs the regime map). *Defense:* the dual-regime presentation exists
   precisely for this; the tornado (notebook 02) quantifies which knobs carry
   the result (θ̄ 46 pp, budget 42 pp); thresholds being unobserved is stated
   in the abstract and limitations. *Concession a referee may force:* the
   paper demonstrates possibility ("folklore fails in plausible regimes"),
   not typicality.
3. **"The retention result is built into your decay rule."** Under
   reinforcement-hysteresis relapse, adopters embedded in saturated teams
   essentially cannot relapse — cluster's decay-immunity is close to
   structural tautology, and ρ=0.25 is stipulated. *Defense:* that lock-in IS
   the claimed mechanism (retention comes from local critical mass, which is
   what cluster seeding buys); D7 logs the rejected alternative
   (memoryless decay) and why; the reversal magnitude (random −57% vs cluster
   −3%) is an emergent quantity, not an input. *Concession:* with
   non-social novelty decay the reversal would weaken; the model documents
   that it cannot reproduce spike-then-relapse for the same reason (C9).

Secondary attack surfaces worth one rehearsed sentence each: broadcast's
0-seed budget asymmetry (answer: it is captioned as the reference floor, D9);
sweeps at 12 replicates vs headline 50 (answer: precision, orderings stable);
the observable-pilots intervention boosts seeds only, not whole pilot teams'
late adopters (answer: cohort-fairness across strategies; team-level variant
is future work); LLNCS abstract at the 4-page maximum (answer: within limit).

## 3. Premise correction (flagged for transparency)

The tasking referenced "the LLM social-simulation validity critiques cited in
docs/decisions.md" — **decisions.md contains no such citations** (the only
LLM mention in the repo docs is spec.md listing "LLM personas" as out of
scope). The paper now cites three real, verified works to make that
positioning explicit (Argyle et al. 2023; Bisbee et al. 2024; Wu et al.
arXiv:2506.19806) in the introduction. If you would rather anchor this in the
decision log too, a one-line D18 note would do it — not done unilaterally,
since the science docs are yours.

## 4. What changed in the repo

- `paper/`: `main.tex` (LLNCS, 4 pages exactly), `refs.bib` (8 entries, all
  web-verified), `numbers.json` + `extract_numbers.py` (programmatic number
  provenance), vendored `llncs.cls`/`splncs03.bst`/`aliascnt.sty`,
  `main.pdf`, `README.md` (build + submission checklist).
- No model, experiment, or documentation changes — science frozen.
