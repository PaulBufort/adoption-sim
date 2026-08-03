"""Machine-derive every statistic cited in the paper into paper/numbers.json.

Source policy (D19, ratified at CP1): all seeded-strategy means and contrasts
come from the PAIRED CSVs (single S2 execution, frozen seeds); the independent
50-replicate panel is the source ONLY for broadcast and the p_innov = 0
ablation (sweeps the paired design does not cover). The predictor verdict is
read from the versioned validation JSON. paper/audit_numbers.py checks the
manuscript against this file.

Terminology (CP1): final_rate -> "terminal adoption"; cumulative_rate ->
"cumulative reach".

Usage: python paper/extract_numbers.py   (writes paper/numbers.json)
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.scenario import load_scenario  # noqa: E402
from experiments.paired_io import aligned_pair, cell_finals, read_rows  # noqa: E402
from experiments.stats import classify_cells, paired_stats  # noqa: E402

RESULTS = REPO / "experiments" / "results"
BAND = 0.02

DECAY_FAMILY = ([("0.5", "0.0")]
                + [(r, rho) for r in ("0.5", "1.0") for rho in ("0.1", "0.25", "0.4")])


def _contrast(cell, a, b):
    s = paired_stats(*aligned_pair(cell, a, b))
    return {"delta_pp": round(100 * s["mean_d"], 4),
            "ci_pp": [round(100 * s["ci"][0], 4), round(100 * s["ci"][1], 4)],
            "p": s["p"], "n": s["n"]}


def paired_headline() -> dict:
    rows = read_rows(RESULTS / "exp1_paired_headline.csv")
    cell = cell_finals(rows, ())[()]
    means = {s: {"mean_pct": round(100 * float(np.mean(list(v.values()))), 1),
                 "sd_pct": round(100 * float(np.std(list(v.values()), ddof=1)), 1),
                 "n": len(v)} for s, v in cell.items()}
    # Meso mechanism, now CSV-derived (seeded_teams + team_rates columns);
    # line teams only (unit 0 = leadership on synthetic orgs).
    meso = {}
    n_line_teams = None
    for s in ("random", "champions", "cluster", "one_per_team"):
        seeded, ignited = [], []
        for r in rows:
            if r["strategy"] != s:
                continue
            teams = [t for t in json.loads(r["seeded_teams"]) if t != 0]
            rates = json.loads(r["team_rates"])
            n_line_teams = len(rates) - 1
            seeded.append(len(teams))
            ignited.append(int(np.sum(np.array(rates[1:]) >= 0.5)))
        meso[s] = {"seeded_teams_mean": round(float(np.mean(seeded)), 1),
                   "ignited50_mean": round(float(np.mean(ignited)), 1)}
    return {
        "means": means,
        "contrasts": {
            "random-cluster": _contrast(cell, "random", "cluster"),
            "champions-random": _contrast(cell, "champions", "random"),
            "one_per_team-random": _contrast(cell, "one_per_team", "random"),
        },
        "meso": meso,
        "n_line_teams": n_line_teams,
    }


def independent_panel() -> dict:
    rows = read_rows(RESULTS / "exp1_strategies_headline.csv")
    b = [r["final_rate"] for r in rows if r["strategy"] == "broadcast"]
    prows = read_rows(RESULTS / "exp1_pinnov_headline.csv")
    b0 = [r["final_rate"] for r in prows
          if r["strategy"] == "broadcast" and float(r["agents.p_innovator"]) == 0.0]
    return {
        "broadcast": {"mean_pct": round(100 * float(np.mean(b)), 1),
                      "sd_pct": round(100 * float(np.std(b, ddof=1)), 1),
                      "n": len(b)},
        "broadcast_at_pinnov0": {"all_exactly_zero": bool(all(v == 0.0 for v in b0)),
                                 "n": len(b0)},
    }


def regime_map() -> dict:
    rows = read_rows(RESULTS / "exp1_regime_paired_headline.csv")
    cells = cell_finals(rows, ("agents.theta_mean", "seeding.budget"))
    keys = sorted(cells, key=lambda c: (float(c[0]), float(c[1])))
    classified = classify_cells([aligned_pair(cells[k], "random", "cluster") for k in keys],
                                band=BAND)
    counts: dict[str, int] = {}
    win_deltas = []
    headline_cell = None
    for k, c in zip(keys, classified):
        counts[c["cls"]] = counts.get(c["cls"], 0) + 1
        if c["cls"] == "win_x":
            win_deltas.append(100 * c["mean_d"])
        if float(k[0]) == 0.30 and float(k[1]) == 0.05:
            headline_cell = {"delta_pp": round(100 * c["mean_d"], 4),
                             "ci_pp": [round(100 * c["ci"][0], 4),
                                       round(100 * c["ci"][1], 4)],
                             "cls": c["cls"]}
    # CP3 (D23): the manuscript's "no practically relevant cluster win" sentence
    # is backed by the largest cluster-favoured point estimate across the map.
    negatives = [(k, c) for k, c in zip(keys, classified) if c["mean_d"] < 0]
    worst_k, worst = min(negatives, key=lambda t: t[1]["mean_d"])
    return {"n_cells": len(keys), "counts": counts,
            "win_delta_min_pp": round(min(win_deltas), 1),
            "win_delta_max_pp": round(max(win_deltas), 1),
            "headline_cell": headline_cell,
            "largest_cluster_edge": {
                "delta_pp": round(100 * worst["mean_d"], 4),
                "theta_mean": float(worst_k[0]), "budget": float(worst_k[1]),
                "cls": worst["cls"],
                "holm_significant_diff": bool(worst["p_diff_holm"] < 0.05),
                "n_cluster_edges_holm_significant": sum(
                    1 for _, c in negatives if c["p_diff_holm"] < 0.05)},
            "n_pairs_per_cell": 50, "band_pp": 100 * BAND}


def decay() -> dict:
    rows = read_rows(RESULTS / "exp1_decay_paired_headline.csv")
    cells = cell_finals(rows, ("dynamics.retention_factor", "dynamics.relapse_prob"))
    classified = classify_cells(
        [aligned_pair(cells[k], "random", "cluster") for k in DECAY_FAMILY], band=BAND)
    fam = {}
    for k, c in zip(DECAY_FAMILY, classified):
        x, y = aligned_pair(cells[k], "random", "cluster")
        fam[f"r={k[0]},rho={k[1]}"] = {
            "delta_pp": round(100 * c["mean_d"], 4),
            "ci_pp": [round(100 * c["ci"][0], 4), round(100 * c["ci"][1], 4)],
            "cls": c["cls"],
            "random_pct": round(100 * float(x.mean()), 1),
            "cluster_pct": round(100 * float(y.mean()), 1),
        }
    key = ("1.0", "0.25")
    sec = {}
    for s in ("random", "cluster"):
        sub = [r for r in rows if r["strategy"] == s
               and (r["dynamics.retention_factor"], r["dynamics.relapse_prob"]) == key]
        ret = [r["retention_rate"] for r in sub if not np.isnan(r["retention_rate"])]
        sec[s] = {"cumulative_pct": round(100 * float(np.mean([r["cumulative_rate"] for r in sub])), 1),
                  "retention_mean": round(float(np.mean(ret)), 2)}
    # CP3 (D23): head-to-head cumulative-reach contrasts at the two cells the
    # manuscript discusses. Secondary descriptive — pointwise uncorrected CIs,
    # never part of the confirmatory (terminal-adoption) Holm family.
    cum_cells = cell_finals(rows, ("dynamics.retention_factor", "dynamics.relapse_prob"),
                            value="cumulative_rate")
    cum = {}
    for k in (("1.0", "0.25"), ("1.0", "0.4")):
        s = paired_stats(*aligned_pair(cum_cells[k], "random", "cluster"))
        cum[f"r={k[0]},rho={k[1]}"] = {
            "delta_pp": round(100 * s["mean_d"], 4),
            "ci_pp": [round(100 * s["ci"][0], 4), round(100 * s["ci"][1], 4)],
            "p": s["p"], "n": s["n"]}
    return {"family": fam, "secondary_at_r1_rho025": sec,
            "cumulative_contrasts": cum,
            "note": "primary endpoint = terminal adoption (final_rate); "
                    "cumulative/retention secondary descriptive, pointwise "
                    "uncorrected CIs (D19; CP3/D23)"}


def robustness() -> dict:
    rows = read_rows(RESULTS / "exp1_robustness_headline.csv")
    cells = cell_finals(rows, ("param", "value"))
    deltas = {}
    for k in sorted(cells):
        s = paired_stats(*aligned_pair(cells[k], "random", "cluster"))
        deltas[f"{k[0]}={k[1]}"] = {"delta_pp": round(100 * s["mean_d"], 4),
                                    "ci_pp": [round(100 * s["ci"][0], 4),
                                              round(100 * s["ci"][1], 4)]}
    vals = [v["delta_pp"] for v in deltas.values()]
    return {"cells": deltas, "min_pp": min(vals), "max_pp": max(vals),
            "n_variants": len(vals)}


def eucore() -> dict:
    rows = read_rows(RESULTS / "exp4_eucore.csv")
    cell = cell_finals(rows, ())[()]
    meta = json.loads((RESULTS / "exp4_eucore.meta.json").read_text())
    # CP3 (D22(a)): the >=10% "ignition share" is retracted — the cut was post
    # hoc and falls inside the low mode. The manuscript now describes the
    # bimodal shape itself: a largest-gap split of the pooled random+cluster
    # terminal rates (descriptive; no tunable threshold — the gap is ~62 pp).
    pooled = np.sort(np.concatenate(
        [np.array(list(cell["random"].values()), dtype=float),
         np.array(list(cell["cluster"].values()), dtype=float)])) * 100.0
    gaps = np.diff(pooled)
    i = int(np.argmax(gaps))
    low, high = pooled[:i + 1], pooled[i + 1:]
    modes = {
        "split": "largest gap in pooled random+cluster terminal rates "
                 "(descriptive; replaces the retracted >=10% ignition share, "
                 "D22(a))",
        "low_median_pct": round(float(np.median(low)), 1),
        "high_median_pct": round(float(np.median(high)), 1),
        "low_max_pct": round(float(low.max()), 1),
        "high_min_pct": round(float(high.min()), 1),
        "gap_pp": round(float(gaps[i]), 1),
        # open interval (ints) containing NO draw, from the unrounded extrema
        "gap_open_interval_pct": [int(np.ceil(low.max())),
                                  int(np.floor(high.min()))],
        "n_low": int(low.size), "n_high": int(high.size),
    }
    return {
        "contrast_random_cluster": _contrast(cell, "random", "cluster"),
        "means": {s: {"mean_pct": round(100 * float(np.mean(list(v.values()))), 1),
                      "sd_pct": round(100 * float(np.std(list(v.values()), ddof=1)), 1)}
                  for s, v in cell.items()},
        "modes": modes,
        "n_draws": 50,
        "graph": {k: meta["graph"][k] for k in
                  ("n_nodes_compiled", "n_departments", "symmetrization")},
    }


def predictor() -> dict:
    v = json.loads((REPO / "paper" / "cp1" / "predictor_validation.json").read_text())
    return {"v1_auc": round(v["v1"]["auc"], 3), "gate_go": 0.80, "gate_partial": 0.70,
            "verdict": v["verdict"]["verdict"],
            "v2_agreement": round(v["v2"]["agreement"], 3),
            "n_units": v["v1"]["n_units"]}


def main() -> int:
    sc = load_scenario(REPO / "experiments" / "scenarios" / "headline.toml")
    numbers = {
        "_source_policy": "paired CSVs for seeded strategies (D19); independent "
                          "panel only for broadcast and the p_innov=0 ablation",
        "scenario": {"n_agents": sc["org"]["n_agents"],
                     "n_departments": sc["org"]["n_departments"],
                     "mean_team_size": sc["org"]["mean_team_size"],
                     "silo": sc["org"]["silo_strength"],
                     "theta_mean": sc["agents"]["theta_mean"],
                     "kappa": sc["agents"]["theta_concentration"],
                     "p_innovator": sc["agents"]["p_innovator"],
                     "p_willing": sc["agents"]["p_willing"][0],
                     "budget": sc["seeding"]["budget"],
                     "replicates": 50, "master_seed": sc["run"]["master_seed"]},
        "paired_headline": paired_headline(),
        "independent_panel": independent_panel(),
        "regime_map": regime_map(),
        "decay": decay(),
        "robustness": robustness(),
        "eucore": eucore(),
        "predictor": predictor(),
        "data_is_synthetic": True,
    }
    out = REPO / "paper" / "numbers.json"
    out.write_text(json.dumps(numbers, indent=2, default=float))
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
