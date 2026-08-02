# Reviewer-response rationale — CN 2026 extended abstract

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
