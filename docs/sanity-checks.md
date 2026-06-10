# Sanity checks — qualitative replication of known results

> Run and reproduced by `experiments/02_sanity_checks.ipynb` (executed 2026-06-10,
> adoption-sim 0.1.0, master seeds inside the notebook). "PASS" means the *qualitative*
> literature result — shapes and orderings, never numbers — emerges from this engine.
> All runs are synthetic; the Enron section uses a real topology with synthetic agents.

## Replications

| # | Reference result | Setup | Measured | Verdict |
|---|---|---|---|---|
| 1 | Threshold knife-edge: minimal distribution changes flip collective outcomes (Granovetter 1978) | complete graph N=100, θ grid i/N, one instigator | intact grid → 100%; one θ moved 0.01→0.5 → cascade stops at 1% | **PASS** |
| 2 | Complex contagion needs wide bridges; long ties help simple contagion but block complex (Centola & Macy 2007; Centola 2010) | ring lattice (k=8) vs degree-matched random graph, seed = one focal neighborhood (9 nodes), θ=0.25 vs θ=0.10 | complex: lattice 100% vs random 4% · simple: random reaches 90% in 3 steps vs lattice 44 | **PASS** |
| 3 | Single-seed global cascades require vulnerable nodes, θ < 1/z (Watts 2002) | random 8-regular, N=2000, one seed, 10 graphs per θ | θ=0.10: 10/10 global cascades · θ=0.15: max 0.1% | **PASS** |
| 4 | Headline result robust to the credibility-weight assumption (D3 null model) | all weights = 1.0 incl. comms, 10 replicates | broadcast 5.2% vs cluster 42.7% (gap survives; cluster even gains) | **PASS** |
| 5 | D17 equivalence: global visibility v ≡ thresholds θ/v (no-broadcast scenarios) | one org, same draws, v=0.6 vs θ/0.6 — and a unit test incl. decay | trajectories identical, max \|Δ\| = 0.0 | **PASS (exact)** |

**Methodological note on check 2.** A first version seeded 5% of nodes *at random* and
the random graph cascaded to 100% — correctly: dense random seeding sits above the
complex-contagion percolation threshold. The literature claim concerns *localized*
seeding (a focal neighborhood). The failed first attempt is kept in the notebook text
because it is instructive, and because deleting failed attempts is how simulators
end up overtrusted.

## Sensitivity (tornado, headline cluster scenario, 10 replicates/side)

| parameter | low → high | plateau swing |
|---|---|---|
| agents.theta_mean | 0.27 → 0.33 | **46.0 pp** |
| seeding.budget | 0.03 → 0.08 | **41.8 pp** |
| agents.p_innovator | 0.0 → 0.05 | 26.2 pp |
| agents.theta_concentration | 12 → 30 | 26.1 pp |
| org.silo_strength | 0.70 → 0.95 | 13.6 pp |
| org.team_locality | 0.40 → 0.90 | **0.1 pp** |

Two consequences, both recorded in `docs/decisions.md`:

- The headline result hangs on the **threshold distribution** (D1/D2) and the **seed
  budget** far more than on structure. Those decisions deserve the strictest scrutiny
  at review.
- `team_locality` (D15) is **not load-bearing** in the frozen κ=20 regime, despite
  having been introduced (with the D3 closeness amendment) to enable cluster spreading
  in the κ=12 regime explored during calibration. Combined with check 4 (cluster
  *gains* under uniform weights), the wide-bridge machinery is best understood as a
  structural-realism feature and an experimental variable — not as the mechanism the
  headline depends on. D15/D3 amendments are flagged accordingly for arbitration.

## Real topology demonstration (NOT a replication, NOT a calibration)

SNAP `email-Enron` (36,692 nodes, 183,831 edges, real intra-organizational e-mail
ties; max degree 1,383): with headline synthetic agents on the fixed real graph,
3 replicates — broadcast 15.4% · cluster 24.2% · random 48.9%. The qualitative
ordering matches the synthetic organizations (broadcast < cluster < scattered).
Broadcast converts more here than on generated orgs (15% vs 6%): heavy-tailed degree
puts more people within one tie of the low-threshold fringe. The edges are real;
thresholds, willingness, weights and "teams" (Louvain communities) are synthetic —
this says nothing about Enron (limitations.md #11).

## Known non-reproductions (kept on purpose)

1. **"Always seed clusters" folklore** — scattered seeding beats cluster seeding on
   reach across the explored space (D16); the claim survives only as the weaker
   "local critical mass must come from somewhere; broadcast provides none." The
   ratified p_innov sweep sharpened the mechanism: the ordering survives with **zero
   innovators** (random 42% vs cluster 20% at p=0), while broadcast's yield at p=0
   is exactly 0.0% — entirely innovator-derived (D16 mechanism amendment).
2. **Spike-then-relapse** — socially-reinforced decay produces lower plateaus, never
   the overshoot shape (D7 amendment); reproducing it would need non-social decay.
3. **Individual pivot relays in generated orgs** — knockout deltas ≈ 0 everywhere;
   bridge redundancy is the norm (D12 amendment, with barbell positive control).
4. **Visibility as cluster seeding's rescue (D17, experiment 3)** — neither global
   v < 1 (provably equivalent to threshold inflation) nor the observable-pilots
   intervention reorders scattered ≥ cluster; loud pilots help scattering *more*,
   in proportion to outward credibility per seed (cluster 5.7, random 11.7,
   champions 16.1). Below v ≈ 0.6 no strategy works at all — visibility itself is
   the binding constraint in that regime.
