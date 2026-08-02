"""D21 gates V1/V2 applied to the ACTUAL paired data + the pre-declared verdict.

Usage (after the paired runs exist):
    python experiments/validate_predictor.py             # print + write JSON

Gate definitions live in docs/decisions.md D21 and experiments/predictor.py
(V1_AUC_GO = 0.80, V1_AUC_PARTIAL = 0.70, V2_AGREEMENT_GO = 0.90, zero
opposite-sign errors for go) — this harness only APPLIES them.

- **V1 (measured mode).** Reconstructs the 200 paired-headline runs bit-exactly
  from their frozen seed triples (same expand_paired_jobs layout as the CSV),
  builds each team's TeamSpec from the run's actual draws, and scores the
  level-1 isolated-team prediction on every SEEDED team, pooled over
  (team × replicate × strategy) across the four paired strategies. Pooling
  over all four strategies is the pre-declared reading of "per-team ignition
  AUC on seeded teams" (D21 names no strategy split); per-strategy AUCs are
  reported as descriptive diagnostics only.
- **V2 (analytic mode).** Classifies the paired regime map with the
  pre-declared 3-class scheme (Holm, ±2 pp band), then compares the SIGN of
  the level-1 prediction Δ = reach_local(random) − reach_local(cluster),
  computed per cell with theta_mean and budget set to the cell's values and
  the external mass calibrated on headline organizations, against the decisive
  cells. Predictor Monte-Carlo seeds are fixed here (V2_SEED_ENTROPY), frozen
  before any observed cell was classified.

Output: paper/cp1/predictor_validation.json + a console report. The verdict is
whatever the gates return — go, partial, or no_go (D21: expected partial).

ALL DATA SYNTHETIC. Stack policy: numpy + stdlib only.
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from core.dynamics import run_simulation  # noqa: E402
from core.orggen import generate_org  # noqa: E402
from core.scenario import build_sim_params, org_kwargs  # noqa: E402
from core.seeding import make_seeding  # noqa: E402
from core.sweep import expand_paired_jobs  # noqa: E402
from experiments import exp1  # noqa: E402
from experiments.paired_io import aligned_pair, cell_finals, read_rows  # noqa: E402
from experiments.predictor import (  # noqa: E402
    IGNITE_FRAC,
    predict_strategy,
    predict_team,
    roc_auc,
    team_specs_from_org,
    v2_sign_agreement,
    verdict,
)
from experiments.stats import classify_cells  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
REGIME_CSV = HERE / "results" / "exp1_regime_paired_headline.csv"
OUT_DIR = HERE.parent / "paper" / "cp1"
V2_SEED_ENTROPY = (20260802, 2)     # frozen pre-execution
V2_N_DRAWS = 800
EXT_MASS = None                     # filled from calibrate_predictor (official seed)


def _external_mass():
    """Official fixed-seed external-mass calibration (same as D21's note)."""
    global EXT_MASS
    if EXT_MASS is None:
        from experiments.calibrate_predictor import CAL_SEED, N_ORGS
        master = np.random.SeedSequence(CAL_SEED)
        s_orgs, _, _ = master.spawn(3)
        from experiments.predictor import measure_external_mass
        sc = exp1.headline_scenario()
        vals = []
        for child in s_orgs.spawn(N_ORGS):
            compiled = generate_org(**org_kwargs(sc),
                                    seed=np.random.default_rng(child)).compile()
            vals.append(measure_external_mass(compiled))
        EXT_MASS = (float(np.mean([v["manager"] for v in vals])),
                    float(np.mean([v["ic"] for v in vals])))
    return EXT_MASS


def v1_on_paired_headline(replicates: int | None = None) -> dict:
    """Reconstruct the paired-headline runs and score V1 on the pooled
    (team x replicate x strategy) seeded-team units."""
    sc = exp1.headline_scenario()
    jobs = expand_paired_jobs(sc, {"seeding.strategy": list(exp1.PAIRED_STRATEGIES)},
                              replicates=replicates)
    pool: list[tuple] = []            # (strategy, fraction_pred, pred_ig, obs_ig)
    for job in jobs:
        s_org, s_seed, s_dyn = job["seeds"]
        jsc = job["scenario"]
        compiled = generate_org(**org_kwargs(jsc),
                                seed=np.random.default_rng(s_org)).compile()
        seeding = make_seeding(jsc["seeding"]["strategy"], compiled,
                               jsc["seeding"]["budget"],
                               rng=np.random.default_rng(s_seed))
        res = run_simulation(compiled, build_sim_params(jsc), seeding,
                             rng=np.random.default_rng(s_dyn))
        specs = team_specs_from_org(compiled, res.theta, res.willing, res.able)
        seeds_by_team: dict[int, list[int]] = {}
        for g in seeding.initial_adopters:
            seeds_by_team.setdefault(int(compiled.team[g]), []).append(int(g))
        for t, spec in specs.items():
            gids = seeds_by_team.get(t)
            if not gids:
                continue
            members = np.flatnonzero((compiled.team == t) & compiled.active)
            local = np.isin(members, gids)
            pred = predict_team(spec, local)
            pool.append((jsc["seeding"]["strategy"], pred["fraction"],
                         pred["ignited"], bool(res.team_final[t] >= IGNITE_FRAC)))
    frac = np.array([p[1] for p in pool])
    pred_ig = np.array([p[2] for p in pool], dtype=bool)
    obs_ig = np.array([p[3] for p in pool], dtype=bool)
    per_strategy = {}
    for s in exp1.PAIRED_STRATEGIES:
        m = np.array([p[0] == s for p in pool])
        per_strategy[s] = {
            "n": int(m.sum()),
            "auc": roc_auc(frac[m], obs_ig[m]),
            "accuracy": float((pred_ig[m] == obs_ig[m]).mean()),
            "observed_ignition_rate": float(obs_ig[m].mean()),
        }
    return {
        "n_units": len(pool),
        "auc": roc_auc(frac, obs_ig),
        "accuracy": float((pred_ig == obs_ig).mean()),
        "tp": int((pred_ig & obs_ig).sum()), "fp": int((pred_ig & ~obs_ig).sum()),
        "tn": int((~pred_ig & ~obs_ig).sum()), "fn": int((~pred_ig & obs_ig).sum()),
        "base_rate_observed": float(obs_ig.mean()),
        "per_strategy": per_strategy,
    }


def classify_regime_map(csv_path=REGIME_CSV, band: float = 0.02) -> dict:
    """The pre-declared 3-class classification of the paired regime map.
    Returns {cell_key: classified dict} with cell_key = (theta_mean, budget)."""
    rows = read_rows(csv_path)
    cells = cell_finals(rows, ("agents.theta_mean", "seeding.budget"))
    keys = sorted(cells, key=lambda c: (float(c[0]), float(c[1])))
    pairs = [aligned_pair(cells[k], "random", "cluster") for k in keys]
    classified = classify_cells(pairs, band=band)
    return {k: c for k, c in zip(keys, classified)}


def v2_on_paired_regime(observed_cells: dict, n_draws: int = V2_N_DRAWS) -> dict:
    """Predict Δ(random − cluster) per cell from cell-local (theta, budget)."""
    sc = exp1.headline_scenario()
    n_pop = sc["org"]["n_agents"]
    w_ext = _external_mass()
    keys = sorted(observed_cells, key=lambda c: (float(c[0]), float(c[1])))
    children = np.random.SeedSequence(list(V2_SEED_ENTROPY)).spawn(len(keys) * 2)
    predicted = {}
    for i, key in enumerate(keys):
        theta, budget = float(key[0]), float(key[1])
        n_seeds = int(np.floor(budget * n_pop))
        common = dict(n_pop=n_pop, n_seeds=n_seeds, m=8, n_teams=249,
                      n_draws=n_draws, w_ext=w_ext, theta_mean=theta)
        pr = predict_strategy("random", np.random.default_rng(children[2 * i]), **common)
        pc = predict_strategy("cluster", np.random.default_rng(children[2 * i + 1]), **common)
        predicted[key] = pr["reach_local"] - pc["reach_local"]
    return {"predicted_delta": predicted,
            "sign_report": v2_sign_agreement(predicted, observed_cells)}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("V1: reconstructing the paired-headline runs (bit-exact seed triples)...")
    v1 = v1_on_paired_headline()
    print(f"  pooled AUC {v1['auc']:.3f} over {v1['n_units']} seeded-team units "
          f"(accuracy {v1['accuracy']:.3f}, observed ignition rate "
          f"{v1['base_rate_observed']:.3f})")
    for s, d in v1["per_strategy"].items():
        print(f"    {s:14} n={d['n']:5}  AUC={d['auc']:.3f}  acc={d['accuracy']:.3f}")
    print("V2: classifying the paired regime map + cell-local predictions...")
    observed = classify_regime_map()
    counts: dict[str, int] = {}
    for c in observed.values():
        counts[c["cls"]] = counts.get(c["cls"], 0) + 1
    print(f"  map classes: {counts}")
    v2 = v2_on_paired_regime(observed)
    rep = v2["sign_report"]
    print(f"  decisive cells {rep['n_decisive_cells']}, agreement "
          f"{rep['agreement']:.3f}, opposite-sign errors {rep['opposite_sign_errors']}")
    verd = verdict(v1["auc"], rep["agreement"], rep["opposite_sign_errors"])
    print(f"VERDICT: {verd['verdict']}")
    for r in verd["reasons"]:
        print(f"  - {r}")
    payload = {
        "v1": v1,
        "map_class_counts": counts,
        "v2": {"agreement": rep["agreement"],
               "n_decisive_cells": rep["n_decisive_cells"],
               "opposite_sign_errors": rep["opposite_sign_errors"],
               "n_missing_predictions": rep["n_missing_predictions"],
               "per_cell": [{**c, "cell": list(c["cell"])} for c in rep["per_cell"]],
               "predicted_delta": {str(k): v for k, v in v2["predicted_delta"].items()},
               "seed_entropy": list(V2_SEED_ENTROPY), "n_draws": V2_N_DRAWS},
        "verdict": verd,
        "data_is_synthetic": True,
    }
    out = OUT_DIR / "predictor_validation.json"
    out.write_text(json.dumps(payload, indent=2, default=float))
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
