# REVIEW A — v0.1 release-readiness sprint (2026-06-10)

> For the scientist. Model science untouched (verified mechanically, see §2).
> This file is the review companion for the release sprint; delete it or move it
> into docs/ after review if you don't want it shipping at the repo root.

## 1. What changed (infrastructure only)

| area | change |
|---|---|
| **Packaging** | `pyproject.toml` added; `pip install -e .` installs the engine as **`adoption_sim`** (maps to `core/`; internal imports made relative — pure style refactor). Repo-local `import core` still works everywhere it did. |
| **Headline precision** | `headline.toml` replicates **20 → 50** (your directive; dated note under D16). Notebook-01 narrative numbers, README caption, and reference lines all refreshed from the 50-rep data. Headline values moved within noise: broadcast 5.8→5.5%, cluster 28.9→**31.9%**, random 73.2→69.5%; non-overlap still holds (broadcast max 14.5% < cluster min 17.1%); κ=12 lottery range widened to 5–65% (50 draws caught a bigger jackpot). |
| **Figures** | New canonical `figures/` dir (was `docs/figures/`). **`python figures/make_all.py`** regenerates all **nine** final figures by executing notebooks 01–03 headlessly (notebooks stay the single source of truth for figure code — no duplicated plotting paths). Hash-verified deterministic: two consecutive full runs produce identical SHA-256s for all nine PNGs. |
| **Tutorial** | New `experiments/00_tutorial.ipynb` (executed, committed): loads the frozen headline TOML, one cascade + attribution, 3-strategy comparison (8 reps) that recovers the headline ordering, pointers onward. ~25 s of compute. Works with either install path (`adoption_sim` or repo-local). |
| **Provenance** | All four notebooks end with a standardized footer (scenario, master seed, **D1–D17 RATIFIED 2026-06-10**, versions, synthetic stamp). Stray status-asserting "PROVISIONAL" strings fixed in `core/defaults.py`, `headline.toml`, and notebook 01's conclusions. |
| **CITATION** | Schema-valid (cffconvert, CFF 1.2.0); author is now the entity "adoption-sim project contributors" instead of TODO-strings. |
| **CI** | Added: editable-install check (both matrix Pythons); tutorial execution; reproduce job now runs `figures/make_all.py` (all three notebooks) and asserts committed CSVs reproduce bit-for-bit under `constraints.txt`. |
| **README** | Opens caveat-then-figure (unchanged order), caption updated to 50-rep numbers, `figures/` paths, make_all + tutorial + editable-install mentions, sidecar wording made exact. |

Three remaining "PROVISIONAL" strings in the repo are deliberate: the protocol
description in `docs/decisions.md` (it's the vocabulary future decisions will use),
the same in `docs/spec.md` (your frozen original), and one dated historical line in
`docs/journal.md` (session-1 record). None asserts a current status.

## 2. Independent verification already done (fresh clone, separate agent)

- Clone → executed tutorial: **105 s**; clone → all nine figures: **181 s** (budget: 15 min).
- `pip install -e .` 5.1 s; `import adoption_sim` works from any cwd; mini-sims run.
- make_all twice: all nine PNG hashes identical across runs **and** byte-identical
  to the committed PNGs (stronger than CI's CSV-only contract).
- 67/67 tests; CSVs bit-identical after full re-execution; README caption numbers
  cross-checked against regenerated CSVs — all match.
- CITATION.cff validates against CFF schema 1.2.0.

Science-freeze proof: before the 50-rep change, the import refactor was gated by
re-running headline row 0 against the previously committed CSV — byte-equal
(final_rate 0.1295, full curve identical). The 50-rep CSVs were then regenerated
once and are reproduced bit-for-bit by CI from that point on.

## 3. What you should verify yourself

1. `python figures/make_all.py` on your machine: nine figures, hashes printed, no
   errors; second run identical hashes (~70 s per run on the dev machine).
2. Open `figures/headline.png` and read the README caption against it — these are
   the public face; confirm the 50-rep numbers and the wording carry your voice.
3. Skim notebook 00 (the tutorial) start to finish — it is the first thing
   strangers will run, and it states your negative result in the friendliest
   possible setting.
4. `git grep PROVISIONAL` — confirm you agree with the three deliberate survivors.

## 4. The 3 things most worth 30 minutes of your attention

1. **The two identity blanks only you can fill** — *RESOLVED by arbitration
   2026-06-10:* author = Paul Bufort (ORCID 0009-0000-6080-1887) in CITATION.cff
   and pyproject.toml; git history rewritten to your authorship (email used:
   `paulbufort@users.noreply.github.com` — the GitHub noreply convention;
   correct it with one more rewrite while private if your account email
   differs). Still open: the GitHub URL in README's `git clone <REPO_URL>` line
   and `repository-code` in CITATION.cff — fill at repo creation.
2. **The κ=8 default vs κ=20 headline-regime gap** — *RESOLVED by arbitration
   2026-06-10:* engine default aligned to the ratified headline regime
   (`theta_concentration` 8 → 20; dated D1 amendment). Out-of-the-box
   `SimParams()` now matches the published figures; κ=8 remains the documented
   sensitivity value. Bonus truth-restoration: the Streamlit demo had been
   running κ=8 under a caption that claimed κ=20 — now caption and code agree.
3. **Read notebook 01's §3–§5 narrative once as a hostile reviewer** (10 min):
   the 50-rep refresh changed several sentences (ranges, the κ=12 lottery max of
   65%, T_b lift 5.5→11.6%). Every number was patched from the regenerated CSVs
   and cross-checked, but narrative drift is exactly the class of error a referee
   loves to find, and only you know which phrasings you'll have to defend live.

## 5. Known leftovers (non-blocking)

- Streamlit Cloud deployment is still a 5-minute human step (needs your account);
  demo runs locally and in CI's AppTest.
- The Enron section of notebook 02 self-skips without `data/raw/` (by design);
  CI never exercises it.
- nbconvert prints a harmless "kernel TCP without encryption" notice during
  make_all; cosmetic, not in-repo fixable.
- `jupyter-events`/`jsonschema` pin: installing `cffconvert` into the main venv
  downgrades `jsonschema` and breaks nbconvert — validate CFF in a throwaway venv
  (as CI-free one-off; documented here so nobody trips on it).
