# Reviewer-response rationale — CN 2026 extended abstract

## v3 (2026-08-03, post-CP3) — corrigenda + oral-defense answers

> CP3 = independent senior-review pass (Opus) arbitrated in decisions.md
> **D23**; S3.3 implements it. Two claims were retracted (D19(b) pairing
> variance; D22(a) Eu-core "ignition 62%/42%"), the crossover is now
> explicitly endpoint-dependent, and the abstract counts sum to 40. If a
> referee spots the old wording in a cached draft, own it: "caught in an
> internal review pass, corrected before submission, logged in the repo".

**Rehearsed answers for the questions CP3 predicts:**

- *"Is the crossover a reach effect or a retention effect?"* At (r=1, ρ=0.25)
  it is **mainly retention**: terminal Δ −5.3 [−9.0, −1.5] vs cumulative Δ
  −1.8 [−5.4, +1.8] (descriptive) — decomposition stated in the paper.
  Cumulative reach is clearly negative (pointwise CI excluding zero) only at
  ρ=0.40 (−7.4 [−10.7, −4.1]). The
  crossover-location sentence is scoped to terminal adoption, our sole
  confirmatory endpoint.
- *"Isn't the +39.7 an artifact of the innovator atom?"* **Exploratory oral
  answer only — INDEPENDENT PANEL, n=12/arm, Welch; NOT paper-citable under
  the D19 source policy:** at p_innovator=0 the ordering survives, random −
  cluster ≈ +21.4 pp [14.9, 27.9] (`exp1_pinnov_headline.csv`). Offer it as
  "an exploratory sweep suggests", never as a confirmatory number.
- *"Doesn't cluster ever win?"* No cell reaches a ≥2 pp cluster win. Exactly
  one cluster-favoured contrast survives Holm — θ̄=0.35 at 1% budget,
  −0.76 pp, inside the ±2 pp band (`regime_map.largest_cluster_edge`). It
  sits in the starvation corner, where local critical mass *should* help —
  say so; it supports the mechanism narrative at negligible size.
- *"What does 'bimodal' mean on Eu-core, quantitatively?"* Pooled terminal
  rates: mode medians 9%/85%, **no draw between 21% and 82%** (gap ≈62 pp).
  We deliberately quote no "ignition rate": any cut is post hoc (that is the
  D22(a) retraction); the pre-declared quantity is the paired +13.5 [1.0,
  26.0].
- *"Why is 72% the ceiling-free number?"* Oral, unaudited: with willing≈85%
  and innovators, the attainable ceiling is ≈86%, so random's 72.0% is ≈84%
  of attainable. Fine to say aloud; kept out of the paper (D23: rejected
  addition).
- *"Why ±2 pp as the practical band?"* Pre-declared with the families (D18/
  D19); note honestly that the two independent estimates of the same
  headline contrast differ by 2.9 pp (39.7 vs 42.6) — the band is of the
  same order as design-level Monte-Carlo variation, which is why "win"
  additionally requires Holm significance, and `exceeds_band` marks the
  stronger cells.

## v2 (2026-08-02, post-CP1) — the crossover manuscript

> Current manuscript: "Disperse to ignite, concentrate to endure: a
> decay-driven crossover in modular complex contagions". Everything below this
> block describes the June build and is retained as history; where it
> conflicts with v2, **v2 wins** (notably: "parity" is superseded by the
> paired CROSSOVER — RESULTS_VERIFIED.md v2).

**The three objections, v2 answers:**

1. *"Already known (Centola/Valente)."* The prescription literature says seed
   clusters; we show that in organizations — where everyone already sits in a
   cluster — dispersion wins the entire ignition regime (14/40 cells, up to
   +43 pp, cluster wins none) AND that the folklore's core intuition
   resurfaces as a decay crossover, quantified with paired CIs. The
   contribution is the crossover map, not a rehash of either side.
2. *"Artifact of your generator."* One-at-a-time robustness (8 variants, sign
   stable +14.7…+48.3 pp) + a SIGN replication on a real modular topology
   (email-Eu-core, ground-truth departments, synthetic attributes, +13.5 pp
   [1.0, 26.0]). Concession kept honest: mechanism not empirically validated;
   magnitudes not comparable across topologies (bimodal lottery regime).
3. *"You chose the regime."* The regime map IS the answer (paired n=50/cell,
   Holm two families, ±2 pp TOST band, three-way verdicts); the headline point
   sits in the ignition band, and the saturation/starvation cells are now
   *provably equivalent within ±2 pp* rather than unexplored. For decay: a
   2×3 (r × ρ>0) pre-declared grid brackets the crossover instead of one
   stipulated ρ.

**New surfaces a referee may probe (v2):**
- *"Your predictor failed."* Yes — pre-specified in the version-controlled
  decision log before execution, gates applied verbatim (AUC 0.642, below
  even the 0.70 partial threshold), no_go reported in the paper (one
  transparency sentence). The mechanism claims rest on measured meso counts
  only. This is a strength to defend, not hide: a pre-specified analysis
  with a published negative outcome. (Wording: "pre-specified", never
  "pre-registered" — there is no external registry.)
- *"champions beats random — why isn't that the story?"* Descriptive (+3.9 pp,
  outside the confirmatory families); one clause in §3.1, never in the
  abstract, per CP1 arbitration.
- *"Crossover location?"* Only bracketed between tested ρ values — never an
  estimated threshold (CP1 constraint; the paper's wording matches).
- *"Paired vs independent numbers differ (72.0 vs 69.5)."* Disjoint
  organization samples by seed layout; the paper cites paired exclusively for
  seeded strategies, the independent panel only for broadcast and the
  p_innov=0 ablation (D19 source policy; sidecars + audit_numbers enforce).

---

> Companion to `paper/main.tex` (corrected 2026-06-19). For oral defense and the
> camera-ready pass. Builds on `REVIEW_B.md`; updated for the decay **parity**
> correction. Every number traces to `paper/numbers.json` / `RESULTS_VERIFIED.md`.

## 0. What changed in this hardening pass (vs the 2026-06-12 build)

| Location | Before | After | Why |
|---|---|---|---|
| Abstract (iii) | "the ordering **reverses** under decay" | "the reach advantage **collapses to parity** … a reach–retention trade-off rather than a dominant strategy" | The 50-rep re-verification (2026-06-17) shows random→30.1% vs cluster→31.1% are **statistically indistinguishable** (gap +0.9 pp, 95% CI [−8,+10], n=12). "Reversal" was unsupported at the committed ρ. |
| §Results header | "Decay **reverses** the ranking" | "Decay **erases the reach advantage**" | Same. The figure (ρ=0.25) shows parity; the old text contradicted its own figure. |
| §Results body | "barely moves … reach–retention trade-off" | adds explicit parity stat + "scattered does not fall below cluster at this ρ — a clean reversal needs higher relapse, outside this regime" | Quantify the claim; pre-empt the "is there really an effect?" referee. |
| Abstract / §Results | two overfull lines (22 pt, 6 pt) | reflowed (≤7.5 pt) | Cosmetic; abstract is the showcase. |

No numbers were changed — all were already correct. Only the **interpretation** of
the decay result was brought in line with the verified statistics. Compiles to
**4 pages** (within the 4-page max), no undefined references. **Not committed** —
this is a change to a scientific claim; per `CLAUDE.md` it awaits your review.

## 0b. Response to external critical review (ChatGPT, 2026-06-19)

A skeptical-reviewer pass (verdict: *weak accept*) drove a second hardening round.
**Applied:**

| ChatGPT point | Change in `main.tex` |
|---|---|
| "decay-proof" too strong (n.s. at n=12 ≠ invariance) | → "nearly unaffected"; parity reworded to "the reach gap is no longer statistically detectable … scattered collapses toward the cluster level" |
| "±" ambiguous (sd vs CI) | labelled **mean±SD** at first use |
| broadcast is not an "equal-budget" strategy | reframed as a **zero-seed awareness baseline (not a seed budget)**; "four seeded strategies share a 5% budget" |
| over-general "contrary to folklore / robustly" | scoped to "the cluster-seeding folklore … in this modular regime"; dropped "robustly" |
| knockout claim too broad / weakest result | **cut** (abstract + discussion) to free space |
| missing influence-maximization reference | added **Kempe, Kleinberg & Tardos (2003)** + one framing line ("fixed structural heuristics, not influence-maximization optima") |
| **levier n°1: mechanism inferred, not measured** | **computed a mesoscopic ignition diagnostic**; added one quantified sentence (below) |

**The new diagnostic** (machine-derived, same headline path, 50 reps;
`paper/ignition_diag.py` → `paper/ignition_diag.json`; reproduces published reach
to **≤0.04 pp**). Of 249 line teams: scattered seeds land in **84±3** (random) /
**60±5** (champions) distinct teams vs cluster's **13±1** saturated teams;
scattered ignites **~200/249** teams to ≥50% adoption (random 197±34, champions
207±22) vs cluster's **89±27**, most via inter-team spillover (random: 125 of 197
ignited teams were unseeded). This turns "scattered seeds are latent cluster
seeds" from interpretation into a measured quantity — directly answering
ChatGPT's top recommendation.

**Pushed back (no change):** the "equal-budget incommensurable" worry is a wording
issue (fixed), not a science flaw — broadcast is the reference floor by design
(D9); and we did **not** cut the visibility θ/v + pilots result (the exact,
machine-verified equivalence is the most novel piece). Still **4 pages**; **not
committed** (scientific change → human review, incl. the new diagnostic).

**Round-2 polish (external re-review, verdict now *accept / weak accept*), all applied:**
Fig. 1 caption "Five equal-budget strategies" → "Four equal-seed-budget strategies
plus a zero-seed broadcast baseline" (removes the page-2/page-3 inconsistency);
abstract opener "Under equal budgets" → "Under equal seed budgets (broadcast
excepted)"; "the folklore part fails" → "the cluster-seeding prescription fails
here"; discussion retention claim bounded to "in this reinforcement-dependent
decay regime, cluster seeding is the retention strategy". Remaining acknowledged
risk is **topological generality** (a scope caveat, not an internal-validity flaw),
already stated in the discussion + limitations.

## 1. The three objections a CN referee is most likely to raise

### Objection 1 — "This is already known: complex contagions need clustered seeding (Centola; Valente)."
**The 'déjà connu' attack — the most dangerous one.**

*Response.* The novelty is a **meso-structural boundary condition on a known
prescription**, not a new contagion rule. The "seed dense clusters, never scatter"
result was established in populations *not otherwise embedded in cohesive groups*
(online experimental networks, village field sites). Our claim is precisely about
what happens when that assumption is removed: in a **modular** population where
*every* node already sits in a dense team, cluster seeding's defining asset —
guaranteed local reinforcement — is **no longer scarce**, so scattering buys more
ignition surface per unit budget and wins on reach (random 69.5% vs cluster 31.9%,
non-overlapping distributions). The mechanism (wide bridges / threshold
reinforcement) is unchanged and explicitly Centola's; the **prescription inverts**
under realistic organizational modularity. That is a new, quantified, counter-intuitive
finding. We position against Granovetter/Watts (thresholds), Centola 2007/2010
(complex contagion, wide bridges) and Valente 2012 (the intervention folklore) by name.

### Objection 2 — "The result is an artifact of your synthetic generator."
*(Near-clique teams p=0.9, ring-adjacent sister bridges, SBM departments → the
team-as-latent-cluster mechanism is baked in.)*

*Response.* The mechanism *is* the point, and it is the empirical norm: real
organizations are modular (teams, departments). We are not claiming an exotic
topology — we are claiming that the **ordinary** one breaks the folklore. Robustness
is shown to uniform credibility weights, team-locality 0.4–0.9, and the
innovator atom removed (p_innov=0) — the scattered-beats-cluster ordering survives
all three (`docs/sanity-checks.md`).
**Honest concession (state it first, before the referee does):** there is **no
real-topology replication of the headline** in the abstract. The Enron-graph demo
(notebook 02) shows the *same qualitative ordering* (broadcast 15% < cluster 24% <
random 49%) but with synthetic agents on a fixed graph, so we do **not** cite it as
evidence. This is the #1 item for the full-paper version. The extended abstract
claims **possibility in plausible regimes**, not population typicality.

### Objection 3 — "The orderings are regime-local; you chose the regime."
*(All headline claims live at θ̄=0.30, κ∈{12,20}; low/tight thresholds saturate,
high thresholds die.)*

*Response.* The **dual-regime** presentation (κ=20 clean-failure + κ=12 lottery)
exists precisely to show the result is not a single lucky point. The tornado
analysis (notebook 02) quantifies which knobs carry the outcome (θ̄ ≈ 46 pp, budget
≈ 42 pp). Crucially, **"thresholds are unobserved" is stated in the abstract and
in `docs/limitations.md`** — we do not hide it. The defensible claim is "the
folklore *fails* in plausible regimes," i.e. an existence/possibility result, not
a universal law. We concede typicality is open and say so.

## 2. The correction turns a weakness into a strength

A referee who reads the decay figure (ρ=0.25, parity) against an old "reversal"
sentence would have caught an internal contradiction — a fatal credibility hit.
The corrected framing is **more** defensible:

- The retention effect is **differential fragility**, not an ordering flip:
  random −57% (t=−13.5, highly significant) vs cluster −2.7% (t=−0.22, n.s.).
  The *difference in robustness* is large and significant; the *post-decay levels*
  are at parity.
- We explicitly **decline** to claim cluster overtakes random (that requires ρ≈0.40,
  logged in D7, outside the headline). Reporting the null/parity honestly is exactly
  what the repo's honesty rules require — and reviewers reward it.
- The keeper message — a genuine **reach–retention trade-off** (wide-but-fragile
  scattered vs narrow-but-stable cluster) — survives the correction intact.

## 3. Secondary surfaces (one rehearsed sentence each)

- **Broadcast's 0-seed budget asymmetry** → it is captioned as the *reference floor*
  (D9): broadcast buys awareness, not adopters; the comparison is fair across the
  four *seeded* strategies, all at 5%.
- **Sweeps at 12 reps vs headline 50** → precision only; orderings are stable and
  the headline claims use 50.
- **θ/v equivalence and the p_innov=0 zero** → say **"machine-verified"**, not
  "approximately": bit-equality test (`test_visibility.py`) and 12/12 literal zeros.
- **Observable-pilots boosts seeds, not whole pilot teams** → cohort-fairness across
  strategies; the team-level variant is future work.
- **4-page length** → within the stated maximum (recommended 2–3, max 4).

## 4. Pre-submission checklist (human steps, CMT)

- [ ] Decide whether to also fix the stale "reversal" caption in
      `experiments/03_observability.ipynb:244` for repo consistency (flagged in
      `RESULTS_VERIFIED.md`; non-blocking for the abstract).
- [ ] CMT: 1 primary + up to 4 secondary subject areas; ≥3 keywords (5 already in
      the abstract). Candidate primary: *"Dynamics on/of networks — social
      contagion / spreading"*; secondaries: *agent-based models*, *social networks*,
      *diffusion/influence*.
- [ ] Upload the PDF as the file; do **not** paste the full text into the CMT
      "abstract" field (that field is the short summary only).
- [ ] Single-blind: author name stays (Paul Bufort, ORCID 0009-0000-6080-1887).
- [ ] Déonto: this is non-remunerated scientific publication = green zone
      (art. 14 §5, per your prior memo). No commercial element in the submission.
