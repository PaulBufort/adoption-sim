# Build journal

> One entry per work block, newest first. Each entry ends with a teaching note:
> what was built, the key design choices, and what the scientist should be able to
> explain to a conference audience.

---

## 2026-06-10 — Session 2: arbitration applied, D17 built, experiment 3

**Scope:** your arbitration directives, in order. All six execution items done.

### What changed

- **decisions.md:** D1–D16 flipped to RATIFIED with your additions recorded in
  place; D17 written up (options incl. the rejected stochastic variant and its
  ratchet artifact) and implemented the same day.
- **Engine (D17):** `SimParams.visibility` (global, default 1.0 — provably and
  bit-verifiably inert), per-agent override in `run_simulation`, and the
  `seeding.pilot_visibility` scenario key for the intervention. 8 new tests (67
  total), including an **exact** θ/v equivalence test that passes with decay on.
- **Experiment 1 rebuilt:** dual-κ headline (20 main / 12 lottery) with the
  heterogeneity caption; p_innov ∈ {0, 0.01, 0.025, 0.05} sweep; T_b ∈ {1, 5, 20}
  sweep; the D9 caption rule baked into the broadcast legend label so no figure can
  omit it; negative result + mechanism immediately after the headline. Frozen-recipe
  CSVs re-verified **bit-identical** post-D17.
- **Experiment 3 (new):** `03_observability.ipynb` — equivalence theorem + exact
  witness, global-v sweep (5 strategies × 4 v), observable-pilots intervention
  (3 strategies × 3 v_global, seeds at v=1), outward-credibility mechanism table.
- **Docs/demo:** model.md (D17 equation + the costly-production-behavior
  definitional note), limitations.md (entries 13–14 + 19; renumbered 1–19),
  sanity-checks.md (check 5: exact equivalence; non-reproduction 4), assumptions.md,
  README (dual-panel caption, ratified status), demo visibility slider + broadcast
  floor captions.

### Findings you asked to be told about (item 6)

1. **v < 1 does NOT rescue cluster seeding — twice.** Global v provably cannot
   (θ/v equivalence; empirically confirmed: orderings preserved at every v). The
   observable-pilots intervention doesn't either: at v_global = 0.8, loud pilots
   buy cluster +3.9 pp but random +9.5 pp and champions +15.1 pp. **Cluster never
   overtakes random anywhere in the tested space.** Your going-in hypothesis is
   refuted in this model family, and the mechanism is measured: gains track
   outward credibility per seed (cluster 5.7 · random 11.7 · champions 16.1) —
   a pilot team's megaphone mostly points at people who already adopted.
2. **A second expectation broke — mine.** The D16 mechanism analysis had credited
   the innovator atom as co-cause of scattering's advantage. The ratified p_innov
   sweep refutes the necessity claim: at p_innov = 0, random still beats cluster
   (42% vs 20%). Team embedding + the Beta tail suffices. D16 carries the
   amendment.
3. **Broadcast's yield is 100% innovator-derived:** at p_innov = 0 it converts
   exactly 0.000 across all replicates. And T_b: a 20-step sustained campaign
   lifts broadcast 5.8% → 13.5% — repetition more than doubles a small number and
   still loses to every seeded strategy by multiples.
4. **Below v ≈ 0.6 nothing works at all** (θ_eff ≥ 0.5 exceeds nearly everyone):
   if usage is mostly invisible, the binding constraint is visibility itself, not
   seeding strategy. Corollary: broadcast — the only strategy whose channel stays
   loud — becomes competitive at low v *by standing still*.

### Teaching note (what's new for the conference audience)

The observability result is the most counter-intuitive deliverable so far, and it
unpacks in three beats:

1. **"Nobody can see who uses the tool" is just "everyone is more resistant",
   exactly.** Global invisibility v rescales every threshold to θ/v — we prove it,
   test it bit-for-bit, and show the sweep. So the intuition "our pilots failed
   because usage is invisible" contains no strategy-relevant information *unless*
   visibility differs across people.
2. **Making pilots loud is real but goes to the wrong address.** Work-out-loud
   rituals help in proportion to how much of the speaker's credibility points at
   *non-adopters*. Whole pilot teams fail that test by construction — most of
   their ties point at each other. The same ritual on well-connected individuals
   buys 3–4× more adoption. One sentence for the stage: *a megaphone is wasted in
   a room where everyone already agrees.*
3. **The honest arc of the project so far:** the folklore "seed clusters, not
   individuals" failed on reach (session 1), survived on retention under decay
   (session 1), and now fails again under every visibility variant we ratified
   (session 2) — each verdict with a measured mechanism attached. That arc — a
   model that keeps disagreeing with its builders' and its owner's hypotheses and
   says so in print — *is* the credibility instrument.

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
