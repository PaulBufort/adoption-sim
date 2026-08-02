"""Fixed-seed a-priori calibration of the D21 level-1 ignition predictor.

Usage:
    python experiments/calibrate_predictor.py            # print the report
    python experiments/calibrate_predictor.py --json P   # also write JSON to P

Reproducible by construction: one master SeedSequence (CAL_SEED = 20260802)
spawns the organization seeds (external-mass calibration), the Monte-Carlo
stream for the P_ig(s, m) curve, and one independent stream per strategy for
the folding — so adding or removing a strategy never shifts the others.

This is NOT part of the pre-declared experiment pipeline: it writes no CSV
under experiments/results/, touches no scenario, and reads only the frozen
headline scenario plus the committed meso diagnostic (paper/ignition_diag.json)
for the observed reference values it compares against. Its numbers back the
pre-execution calibration note in docs/decisions.md D21.

Wording contract (user arbitration 2026-08-02): the level-1 shortfall is
quoted as "X% of ignited TEAMS / Y% of REACH not explained by the local
predictor" — two different denominators, never interchanged, and never the
stronger mechanistic phrase "non-local" (what is measured is the predictor's
residual, not the channel that produced it).

ALL DATA SYNTHETIC. Stack policy: numpy + stdlib only.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from core.orggen import generate_org  # noqa: E402
from core.scenario import org_kwargs  # noqa: E402
from experiments import exp1  # noqa: E402
from experiments.predictor import (  # noqa: E402
    measure_external_mass,
    p_ignite,
    predict_strategy,
)

CAL_SEED = 20260802
N_ORGS = 5              # organizations averaged for the external-mass estimate
N_DRAWS_CURVE = 3000    # Monte-Carlo teams per s for the P_ig curve
N_DRAWS_FOLD = 1500     # Monte-Carlo teams per s inside the strategy folding
STRATEGIES = ("random", "cluster", "one_per_team")
M = 8                   # headline mean team size
IGNITION_JSON = pathlib.Path(__file__).resolve().parent.parent / "paper" / "ignition_diag.json"


def calibrate(seed: int = CAL_SEED, n_orgs: int = N_ORGS,
              n_draws_curve: int = N_DRAWS_CURVE,
              n_draws_fold: int = N_DRAWS_FOLD) -> dict:
    master = np.random.SeedSequence(seed)
    s_orgs, s_curve, s_fold = master.spawn(3)
    sc = exp1.headline_scenario()

    # 1. External credible mass, averaged over fresh headline organizations.
    per_org = []
    for child in s_orgs.spawn(n_orgs):
        compiled = generate_org(**org_kwargs(sc), seed=np.random.default_rng(child)).compile()
        ext = measure_external_mass(compiled)
        ext["denominator_share"] = ext["overall"] / float(compiled.total_weight.mean())
        per_org.append(ext)
    ext_mass = {
        k: {"mean": float(np.mean([e[k] for e in per_org])),
            "sd": float(np.std([e[k] for e in per_org], ddof=1)) if n_orgs > 1 else 0.0}
        for k in ("manager", "ic", "overall", "denominator_share")
    }
    w_ext = (ext_mass["manager"]["mean"], ext_mass["ic"]["mean"])

    # 2. P_ig(s, m=8) curve at headline agent parameters.
    rng_curve = np.random.default_rng(s_curve)
    curve = {}
    for s in range(M + 1):
        r = p_ignite(s, M, rng_curve, n_draws=n_draws_curve, w_ext=w_ext)
        curve[s] = {"p_ignite": r["p_ignite"], "mean_fraction": r["mean_fraction"]}

    # 3. Strategy folding — one independent stream per strategy.
    n_pop = sc["org"]["n_agents"]
    n_seeds = int(np.floor(sc["seeding"]["budget"] * n_pop))
    n_teams = 249  # line teams at the headline size (N=2000, mean team 8)
    fold_children = s_fold.spawn(len(STRATEGIES))
    strategies = {}
    for strat, child in zip(STRATEGIES, fold_children):
        p = predict_strategy(strat, np.random.default_rng(child), n_pop=n_pop,
                             n_seeds=n_seeds, m=M, n_teams=n_teams,
                             n_draws=n_draws_fold, w_ext=w_ext)
        strategies[strat] = {
            "p_team_ignites": p["p_team_ignites"],
            "expected_ignited_teams": p["expected_ignited_teams"],
            "reach_local": p["reach_local"],
        }

    # 4. Confrontation with the committed meso diagnostic (observed values).
    comparison = {}
    if IGNITION_JSON.exists():
        diag = json.loads(IGNITION_JSON.read_text()).get("aggregates", {})
        for strat in ("random", "cluster"):
            if strat not in diag or strat not in strategies:
                continue
            obs_reach = float(diag[strat]["final_rate"][0])
            obs_teams = float(diag[strat]["n_ignited50"][0])
            pred = strategies[strat]
            comparison[strat] = {
                "observed_reach": obs_reach,
                "predicted_local_reach": pred["reach_local"],
                "share_of_reach_unexplained": 1.0 - pred["reach_local"] / obs_reach,
                "observed_ignited_teams": obs_teams,
                "predicted_local_ignited_teams": pred["expected_ignited_teams"],
                "share_of_teams_unexplained": 1.0 - pred["expected_ignited_teams"] / obs_teams,
            }

    return {
        "cal_seed": seed,
        "n_orgs": n_orgs,
        "n_draws_curve": n_draws_curve,
        "n_draws_fold": n_draws_fold,
        "scenario": sc["meta"]["name"],
        "external_mass": ext_mass,
        "p_ignite_curve_m8": curve,
        "strategies": strategies,
        "comparison_vs_observed": comparison,
        "data_is_synthetic": True,
    }


def report(cal: dict) -> str:
    lines = [
        f"D21 level-1 predictor calibration — seed {cal['cal_seed']}, "
        f"{cal['n_orgs']} orgs, {cal['n_draws_curve']}/{cal['n_draws_fold']} MC draws",
        f"external credible mass: manager {cal['external_mass']['manager']['mean']:.2f} · "
        f"IC {cal['external_mass']['ic']['mean']:.2f} · "
        f"{100 * cal['external_mass']['denominator_share']['mean']:.0f}% of the denominator",
        "P_ig(s, m=8): " + "  ".join(
            f"s={s}:{v['p_ignite']:.3f}" for s, v in cal["p_ignite_curve_m8"].items() if int(s) <= 4),
    ]
    for strat, p in cal["strategies"].items():
        lines.append(f"{strat:13} P(team ignites)={p['p_team_ignites']:.4f}  "
                     f"E[ignited teams]={p['expected_ignited_teams']:6.1f}  "
                     f"local reach={100 * p['reach_local']:5.1f}%")
    for strat, c in cal["comparison_vs_observed"].items():
        lines.append(
            f"{strat:8} not explained by the local predictor: "
            f"TEAMS {100 * c['share_of_teams_unexplained']:.0f}% "
            f"({c['predicted_local_ignited_teams']:.1f} predicted vs "
            f"{c['observed_ignited_teams']:.0f} observed) · "
            f"REACH {100 * c['share_of_reach_unexplained']:.0f}% "
            f"({100 * c['predicted_local_reach']:.1f} pp vs "
            f"{100 * c['observed_reach']:.1f} pp)")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=pathlib.Path, default=None,
                    help="also write the full calibration dict to this path")
    args = ap.parse_args()
    cal = calibrate()
    print(report(cal))
    if args.json:
        args.json.write_text(json.dumps(cal, indent=2))
        print(f"written: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
