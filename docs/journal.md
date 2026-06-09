# Build journal

> One entry per work block, newest first. Each entry ends with a teaching note:
> what was built, the key design choices, and what the scientist should be able to
> explain to a conference audience.

---

## 2026-06-10 — Session 1: empty repo → v0.1 candidate

**Scope:** v0.1 per docs/spec.md. Everything below was built and verified this session.

### What exists now

- **Engine** (`core/`, NetworkX+NumPy+stdlib only, test-enforced): two-layer org
  generator (D10/D15), fractional-threshold contagion with ready/willing/able gating
  and optional decay (D1–D8), five seeding strategies (D9), metrics incl. dead
  pockets and pivot knockouts (D11/D12), multiprocessing sweeps with bit-for-bit
  seed discipline (D14), TOML scenarios with typo-loud validation, real-graph ingest.
- **Experiments:** notebook 01 (headline: broadcast vs cluster, executed, committed
  with outputs; also a CLI twin) and notebook 02 (sanity checks 4/4 PASS:
  Granovetter, Centola–Macy, Watts, D3-null robustness; tornado; Enron real-topology
  demo). Results as CSV + provenance sidecars in `experiments/results/`.
- **Demo:** Streamlit app (5 controls → curves vs broadcast reference, dead-pocket
  map, R/W/A attribution), synthetic banner, AppTest smoke tests.
- **Docs:** model.md (math as implemented), assumptions.md, limitations.md (16
  entries incl. measured non-reproductions), decisions.md (D1–D16, all
  PROVISIONAL), sanity-checks.md, README, CITATION.cff (author = TODO placeholder).
- **Quality:** 59 tests green; CI runs tests + smoke on 3.11/3.13 **and re-executes
  notebook 1 asserting the committed CSVs reproduce bit-for-bit** under
  constraints.txt.
- **Independent stranger test** (fresh clone, README only): clone → reproduced
  headline figure in **113 s** (budget: 15 min); figure and CSVs byte-identical;
  59/59 tests; demo healthy. Its friction list (10 items) was fixed same-session,
  except CITATION author (needs you).

### Findings that shaped the science (all in decisions.md)

1. **The headline holds and is robust** (D16): broadcast 5.8%±3.3% vs cluster
   28.9%±7.1% (20 replicates, distributions non-overlapping); silo strength
   monotonically caps cluster's plateau. It survives uniform credibility weights
   and locality changes.
2. **Negative result, committed to publication** (D16): scattered seeding (random/
   champions) beats cluster seeding on reach everywhere we looked — every scattered
   seed already sits inside a dense team; the 2.5% innovator atom subsidizes
   scattering in all conditions. I did NOT manufacture the folklore ordering; the
   honest lever (a no-innovators variant) is flagged for your arbitration.
3. **Decay reverses the trade** (D7 amendment): with relapse-when-unreinforced,
   random collapses 0.73→0.26 while cluster holds 0.29→0.32 (full reversal at
   ρ=0.4). Also: no spike-then-relapse shape exists in this model — decay lowers
   plateaus instead; reported as a model limitation, not hidden.
4. **No hero relays** (D12 amendment): knockouts of top-betweenness nodes (incl.
   CEO) move nothing; one-sided pilots at hermetic silos simply fail to jump rather
   than depend on a gateway person. Diagnostic validated on a designed bottleneck;
   no seed-fishing for a prettier demo.
5. **Tornado** (notebook 02): θ̄ (46pp swing) and seed budget (42pp) dominate;
   team_locality ≈ 0pp — D15/D3-amendment downgraded from load-bearing to
   structural-realism features. Arbitration priority is therefore D1/D2.

### Engineering decisions (builder's discretion, FYI)

- TOML via stdlib `tomllib` instead of YAML (hard stack constraint; flag if you object).
- Altair/pandas used in the demo only — they ship inside Streamlit; root
  requirements stay exactly NetworkX+NumPy+Streamlit.
- `constraints.txt` records known-good exact versions; CI re-derives the headline
  CSVs under them, so dependency drift that changes results becomes a red build.
- Commits are authored "Claude (builder)" since no git identity is configured on
  this machine; rewrite or amend authorship before the repo goes public if you want
  your name on the history.

### For your review (the arbitration queue)

Highest priority: **D1/D2** (threshold distribution + innovator atom — the tornado
says these carry the result), **D16** (headline freeze + the negative result and
whether to add the no-innovators variant), **D8** (broadcast operationalization).
Then D3/D15 (now non-load-bearing), D5 (willingness ceiling appears in every
figure), D7 (decay semantics; innovators-never-relapse), D9 (broadcast-as-floor
fairness framing), D12/D14 and the rest. CITATION.cff needs your name; README needs
the repo URL at release; the Streamlit Cloud deploy is a 5-minute human step
(demo/README.md) since it needs your account.

### Teaching note (what you should be able to explain on stage)

**What was built:** a falsifiable toy — a two-layer synthetic organization where a
new practice spreads only through credible peer exposure, gated by three independent
conditions (ready/willing/able), so that every failure is attributable: *never
exposed enough* vs *never willing* vs *never able*.

**The three design choices that carry everything:**
1. *Fractional thresholds with an innovator atom* (D1/D2). The Beta mean sets how
   much social proof a person needs (θ̄=0.30 ≈ "a third of my credible contacts");
   the 2.5% θ=0 innovators are why a broadcast converts *anyone*. The tornado chart
   proves these two numbers carry the headline — which is why they are the first
   thing to defend or change.
2. *Broadcast = universal awareness at low credibility* (D8). It is not "weak
   seeding" — it seeds nobody. It makes everyone *aware* for one step at weight 0.3
   vs 1.0 for a close colleague. Innovators ignite, then arithmetic kills it: one
   comms message is ~3% of anyone's credibility mass, far below any realistic
   threshold. This is the mechanism behind "the all-hands demo converted the
   enthusiasts and nobody else."
3. *Cluster seeding = buying local critical mass* (D9). Saturating whole teams
   guarantees that everyone adjacent sees *several* adopters at once. It reliably
   beats broadcast ~5×, and silos cap its ceiling — structure decides its reach.

**The slide you must not skip (because someone in the room knows the literature):**
in this model family, *scattered* seeding beats cluster seeding on raw reach — every
employee already lives inside a dense team, so 100 scattered seeds are 100 lottery
tickets on team ignition, and tickets beat guarantees here. The honest claim is
narrower than the folklore: **local critical mass must come from somewhere;
broadcast provides none — and if usage decays without reinforcement, only the
clustered gains survive** (random −64% vs cluster ±0 under decay). That last
sentence — reach favors scattering, retention favors clustering — is the most
defensible takeaway in the whole project, and it emerged from the model rather than
being designed in.

**The honesty armor:** every figure is stamped synthetic; 16 limitations are
enumerated in plain language; three things the model *fails* to reproduce are
documented next to the four literature results it passes; and all 16 modeling
decisions sit in a log with alternatives, waiting for the scientist — not the
builder — to ratify them.

---

## 2026-06-10 — Session 1 (opening notes, kept for the record)

- Environment: Python 3.13 venv; networkx/numpy/matplotlib/streamlit/pytest/
  jupyterlab. Git repo initialized (`main`), full AGPL-3.0 text in LICENSE.
- `docs/decisions.md` written **before any engine code** (D1–D13 at that point).
- `docs/limitations.md` seeded from W1 (spec §6).
- Stack-policy choices logged above under "Engineering decisions".
