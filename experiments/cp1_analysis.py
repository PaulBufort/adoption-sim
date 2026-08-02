"""CP1 arbitration package: every table and figure, machine-derived.

Usage:
    python experiments/cp1_analysis.py

Reads ONLY the official paired CSVs produced by the single S2 execution
(exp1_paired_headline, exp1_regime_paired_headline, exp1_decay_paired_headline,
exp1_robustness_headline, exp4_eucore) plus the committed independent panel for
the broadcast floor, recomputes all statistics with experiments/stats.py
(paired t, Holm two families, TOST band, 3-class cells — the pre-declared
schemes), and writes:

    paper/cp1/cp1_tables.json      every number in the CP1 package
    paper/cp1/fig_regime_3class.png
    paper/cp1/fig_decay_family.png
    paper/cp1/fig_robustness.png
    paper/cp1/fig_eucore.png

Pre-declared analysis constants: BAND = ±2 pp practical-significance band,
ALPHA = 0.05, decay family = the 7 unique random−cluster contrasts on
final_rate (D19 amendment), regime family = the 40 cells (D18 upgrade).
This script contains NO simulation — pure re-analysis of the versioned CSVs.

ALL DATA SYNTHETIC (topology real for exp4 only; D22 framing).
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from experiments.paired_io import aligned_pair, cell_finals, read_rows  # noqa: E402
from experiments.stats import classify_cells, paired_stats  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT = HERE.parent / "paper" / "cp1"
BAND, ALPHA = 0.02, 0.05

THETA_AXIS = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
BUDGET_AXIS = [0.01, 0.02, 0.05, 0.10, 0.15]
DECAY_FAMILY = ([("0.5", "0.0")]
                + [(r, rho) for r in ("0.5", "1.0") for rho in ("0.1", "0.25", "0.4")])
STAMP = "SYNTHETIC DATA — paired protocol D19, n=50 organizations/cell"


def _ps(x, y):
    s = paired_stats(x, y)
    return {"mean_d_pp": round(100 * s["mean_d"], 2),
            "ci_pp": [round(100 * s["ci"][0], 2), round(100 * s["ci"][1], 2)],
            "sd_d_pp": round(100 * s["sd_d"], 2), "p": s["p"], "n": s["n"]}


def _cell_export(c):
    return {"delta_pp": round(100 * c["mean_d"], 2),
            "ci_pp": [round(100 * c["ci"][0], 2), round(100 * c["ci"][1], 2)],
            "ci_tost_pp": [round(100 * c["ci_tost"][0], 2), round(100 * c["ci_tost"][1], 2)],
            "p_diff_holm": c["p_diff_holm"], "p_tost_holm": c["p_tost_holm"],
            "cls": c["cls"], "exceeds_band": bool(c["exceeds_band"]),
            "sd_d_pp": round(100 * c["sd_d"], 2)}


def analyze_headline() -> dict:
    rows = read_rows(RESULTS / "exp1_paired_headline.csv")
    cell = cell_finals(rows, ())[()]
    means = {s: {"mean_pct": round(100 * float(np.mean(list(v.values()))), 2),
                 "sd_pct": round(100 * float(np.std(list(v.values()), ddof=1)), 2),
                 "n": len(v)}
             for s, v in cell.items()}
    contrasts = {}
    for a, b in (("random", "cluster"), ("champions", "random"),
                 ("one_per_team", "random"), ("champions", "cluster")):
        contrasts[f"{a}-{b}"] = _ps(*aligned_pair(cell, a, b))
    return {"means": means, "paired_contrasts": contrasts,
            "note": "descriptive contrasts — only the decay and regime families "
                    "carry pre-declared corrected claims (D19)"}


def analyze_regime() -> dict:
    rows = read_rows(RESULTS / "exp1_regime_paired_headline.csv")
    cells = cell_finals(rows, ("agents.theta_mean", "seeding.budget"))
    keys = sorted(cells, key=lambda c: (float(c[0]), float(c[1])))
    classified = classify_cells([aligned_pair(cells[k], "random", "cluster") for k in keys],
                                band=BAND, alpha=ALPHA)
    table, counts = {}, {}
    for k, c in zip(keys, classified):
        counts[c["cls"]] = counts.get(c["cls"], 0) + 1
        x, y = aligned_pair(cells[k], "random", "cluster")
        table[f"theta={k[0]},budget={k[1]}"] = {
            **_cell_export(c),
            "random_mean_pct": round(100 * float(x.mean()), 1),
            "cluster_mean_pct": round(100 * float(y.mean()), 1),
        }
    return {"class_counts": counts, "cells": table,
            "band_pp": 100 * BAND, "alpha": ALPHA,
            "keys_sorted": [list(k) for k in keys], "classified": classified}


def analyze_decay() -> dict:
    rows = read_rows(RESULTS / "exp1_decay_paired_headline.csv")
    cells = cell_finals(rows, ("dynamics.retention_factor", "dynamics.relapse_prob"))
    x05, _ = aligned_pair(cells[("0.5", "0.0")], "random", "cluster")
    x10, _ = aligned_pair(cells[("1.0", "0.0")], "random", "cluster")
    self_check = bool(np.array_equal(x05, x10))
    pairs = [aligned_pair(cells[k], "random", "cluster") for k in DECAY_FAMILY]
    classified = classify_cells(pairs, band=BAND, alpha=ALPHA)
    family = {}
    for k, c in zip(DECAY_FAMILY, classified):
        x, y = aligned_pair(cells[k], "random", "cluster")
        family[f"r={k[0]},rho={k[1]}"] = {
            **_cell_export(c),
            "random_mean_pct": round(100 * float(x.mean()), 1),
            "cluster_mean_pct": round(100 * float(y.mean()), 1),
        }
    # Secondary descriptive metrics (pre-declared secondary — no corrected claims).
    secondary = {}
    for key, cell in cells.items():
        rr = [r for r in rows
              if (r["dynamics.retention_factor"], r["dynamics.relapse_prob"]) == key]
        for s in ("random", "champions", "cluster"):
            sub = [r for r in rr if r["strategy"] == s]
            cum = [r["cumulative_rate"] for r in sub]
            ret = [r["retention_rate"] for r in sub if not np.isnan(r["retention_rate"])]
            secondary[f"r={key[0]},rho={key[1]},{s}"] = {
                "cumulative_mean_pct": round(100 * float(np.mean(cum)), 1),
                "retention_mean": round(float(np.mean(ret)), 3) if ret else None,
                "n_retention_defined": len(ret),
            }
    return {"rho0_bit_identity_self_check": self_check,
            "family_final_rate": family,
            "secondary_descriptive": secondary,
            "classified": classified}


def analyze_robustness() -> dict:
    rows = read_rows(RESULTS / "exp1_robustness_headline.csv")
    cells = cell_finals(rows, ("param", "value"))
    out = {}
    for k in sorted(cells):
        out[f"{k[0]}={k[1]}"] = _ps(*aligned_pair(cells[k], "random", "cluster"))
    return out


def analyze_eucore() -> dict:
    rows = read_rows(RESULTS / "exp4_eucore.csv")
    cell = cell_finals(rows, ())[()]
    means = {s: {"mean_pct": round(100 * float(np.mean(list(v.values()))), 2),
                 "sd_pct": round(100 * float(np.std(list(v.values()), ddof=1)), 2)}
             for s, v in cell.items()}
    x, y = aligned_pair(cell, "random", "cluster")
    ign = {s: round(float(np.mean([v >= 0.10 for v in cell[s].values()])), 3)
           for s in cell}
    return {"means": means,
            "contrast_random_cluster": _ps(x, y),
            "share_of_draws_above_10pct": ign,
            "per_draw_random_pct": [round(100 * v, 1) for _, v in sorted(cell["random"].items())],
            "per_draw_cluster_pct": [round(100 * v, 1) for _, v in sorted(cell["cluster"].items())],
            "framing": "replication on a real modular topology with synthetic "
                       "behavioral attributes (D22) — NOT an empirical validation"}


# --- Figures --------------------------------------------------------------------

CLS_COLOR = {"win_x": None, "win_y": None, "equivalent": "#d9d9d9", "uncertain": "#ffffff"}


def fig_regime(reg: dict) -> None:
    keys = [tuple(k) for k in reg["keys_sorted"]]
    classified = reg["classified"]
    delta = np.full((len(THETA_AXIS), len(BUDGET_AXIS)), np.nan)
    cls_grid = np.empty((len(THETA_AXIS), len(BUDGET_AXIS)), dtype=object)
    for k, c in zip(keys, classified):
        i = THETA_AXIS.index(float(k[0])); j = BUDGET_AXIS.index(float(k[1]))
        delta[i, j] = 100 * c["mean_d"]
        cls_grid[i, j] = c["cls"]
    fig, ax = plt.subplots(figsize=(7.0, 4.6), dpi=200)
    vmax = np.nanmax(np.abs(delta))
    masked = np.where(np.isin(cls_grid, ["win_x", "win_y"]), delta, np.nan)
    im = ax.imshow(masked, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto",
                   origin="lower")
    for i in range(len(THETA_AXIS)):
        for j in range(len(BUDGET_AXIS)):
            c = cls_grid[i, j]
            if c == "equivalent":
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, color="#d9d9d9"))
                ax.text(j, i, "≈", ha="center", va="center", fontsize=9, color="#555")
            elif c == "uncertain":
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                           hatch="///", edgecolor="#999", lw=0))
                ax.text(j, i, "?", ha="center", va="center", fontsize=9, color="#777")
            else:
                ax.text(j, i, f"{delta[i, j]:+.0f}", ha="center", va="center",
                        fontsize=9, fontweight="bold",
                        color="white" if abs(delta[i, j]) > 25 else "black")
    hi, hj = THETA_AXIS.index(0.30), BUDGET_AXIS.index(0.05)
    ax.add_patch(plt.Rectangle((hj - .5, hi - .5), 1, 1, fill=False, lw=2.2, edgecolor="k"))
    ax.set_xticks(range(len(BUDGET_AXIS)), [f"{100*b:.0f}%" for b in BUDGET_AXIS])
    ax.set_yticks(range(len(THETA_AXIS)), [f"{t:.2f}" for t in THETA_AXIS])
    ax.set_xlabel("seed budget"); ax.set_ylabel("mean threshold θ̄")
    ax.set_title("Paired Δ final reach (random − cluster, pp) — 3-class verdict\n"
                 "Holm two families, ±2 pp band, n=50 pairs/cell; box = frozen headline point",
                 fontsize=10)
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Δ pp (wins only)")
    ax.legend(handles=[Patch(color="#d9d9d9", label="equivalent (Holm-TOST)"),
                       Patch(facecolor="white", hatch="///", edgecolor="#999",
                             label="uncertain")],
              loc="upper right", fontsize=8, framealpha=0.9)
    fig.text(0.01, 0.01, STAMP, fontsize=6, color="#888")
    fig.tight_layout()
    fig.savefig(OUT / "fig_regime_3class.png", bbox_inches="tight")
    plt.close(fig)


def fig_decay(dec: dict) -> None:
    fam = dec["family_final_rate"]
    rhos = [0.0, 0.1, 0.25, 0.4]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.8), dpi=200,
                                  gridspec_kw={"width_ratios": [1.1, 1.0]})
    for r, style in (("0.5", "--o"), ("1.0", "-s")):
        d, lo, hi = [], [], []
        for rho in ("0.0", "0.1", "0.25", "0.4"):
            key = f"r=0.5,rho=0.0" if rho == "0.0" else f"r={r},rho={rho}"
            c = fam[key]
            d.append(c["delta_pp"]); lo.append(c["ci_pp"][0]); hi.append(c["ci_pp"][1])
        d, lo, hi = map(np.array, (d, lo, hi))
        ax.errorbar(rhos, d, yerr=[d - lo, hi - d], fmt=style, capsize=3,
                    label=f"r = {r}", lw=1.6)
    ax.axhspan(-2, 2, color="#eee", zorder=0)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("relapse probability ρ"); ax.set_ylabel("paired Δ final reach (pp)")
    ax.set_title("random − cluster under decay (95% CI)\nshaded = ±2 pp practical band",
                 fontsize=10)
    ax.legend(fontsize=9)
    for r, style in (("0.5", "--"), ("1.0", "-")):
        rnd = [fam["r=0.5,rho=0.0" if rho == "0.0" else f"r={r},rho={rho}"]["random_mean_pct"]
               for rho in ("0.0", "0.1", "0.25", "0.4")]
        clu = [fam["r=0.5,rho=0.0" if rho == "0.0" else f"r={r},rho={rho}"]["cluster_mean_pct"]
               for rho in ("0.0", "0.1", "0.25", "0.4")]
        ax2.plot(rhos, rnd, style, color="#1f77b4", label=f"random r={r}", lw=1.6)
        ax2.plot(rhos, clu, style, color="#d62728", label=f"cluster r={r}", lw=1.6)
    ax2.set_xlabel("relapse probability ρ"); ax2.set_ylabel("mean final reach (%)")
    ax2.set_title("absolute reach: random collapses,\ncluster barely moves", fontsize=10)
    ax2.legend(fontsize=8)
    fig.text(0.01, 0.01, STAMP, fontsize=6, color="#888")
    fig.tight_layout()
    fig.savefig(OUT / "fig_decay_family.png", bbox_inches="tight")
    plt.close(fig)


def fig_robustness(rob: dict) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=200)
    labels = list(rob)
    y = np.arange(len(labels))[::-1]
    for yi, lab in zip(y, labels):
        c = rob[lab]
        ax.errorbar(c["mean_d_pp"], yi,
                    xerr=[[c["mean_d_pp"] - c["ci_pp"][0]], [c["ci_pp"][1] - c["mean_d_pp"]]],
                    fmt="o", color="#1f77b4", capsize=3)
    ax.axvline(0, color="k", lw=0.8); ax.axvspan(-2, 2, color="#eee", zorder=0)
    ax.set_yticks(y, labels, fontsize=8)
    ax.set_xlabel("paired Δ final reach, random − cluster (pp, 95% CI)")
    ax.set_title("Robustness: the dispersion advantage across org variants", fontsize=10)
    fig.text(0.01, 0.01, STAMP, fontsize=6, color="#888")
    fig.tight_layout()
    fig.savefig(OUT / "fig_robustness.png", bbox_inches="tight")
    plt.close(fig)


def fig_eucore(euc: dict) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=200)
    rnd = euc["per_draw_random_pct"]; clu = euc["per_draw_cluster_pct"]
    jitter = np.linspace(-0.12, 0.12, len(rnd))
    ax.scatter(np.zeros(len(rnd)) + jitter, rnd, s=14, alpha=0.7, label="random")
    ax.scatter(np.ones(len(clu)) + jitter, clu, s=14, alpha=0.7, label="cluster")
    ax.set_xticks([0, 1], ["random", "cluster"])
    ax.set_ylabel("final reach (%) per attribute draw")
    ax.set_title("email-Eu-core (real topology, synthetic agents, 50 paired draws)\n"
                 "bimodal ignition lottery — paired Δ "
                 f"{euc['contrast_random_cluster']['mean_d_pp']:+.1f} pp "
                 f"CI {euc['contrast_random_cluster']['ci_pp']}", fontsize=9)
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "TOPOLOGY REAL (SNAP email-Eu-core), ALL AGENT ATTRIBUTES SYNTHETIC — D22",
             fontsize=6, color="#888")
    fig.tight_layout()
    fig.savefig(OUT / "fig_eucore.png", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    headline = analyze_headline()
    regime = analyze_regime()
    decay = analyze_decay()
    robustness = analyze_robustness()
    eucore = analyze_eucore()
    fig_regime(regime); fig_decay(decay); fig_robustness(robustness); fig_eucore(eucore)
    tables = {
        "band_pp": 100 * BAND, "alpha": ALPHA,
        "headline_paired": headline,
        "regime_map": {k: v for k, v in regime.items() if k != "classified"},
        "decay": {k: v for k, v in decay.items() if k != "classified"},
        "robustness": robustness,
        "eucore": eucore,
        "provenance": {
            "csvs": ["exp1_paired_headline.csv", "exp1_regime_paired_headline.csv",
                     "exp1_decay_paired_headline.csv", "exp1_robustness_headline.csv",
                     "exp4_eucore.csv"],
            "analysis": "experiments/cp1_analysis.py (pure re-analysis, no simulation)",
            "stats": "experiments/stats.py (paired t, Holm x2 families, TOST ±2 pp)",
        },
        "data_is_synthetic": True,
    }
    (OUT / "cp1_tables.json").write_text(json.dumps(tables, indent=2, default=float))
    print(f"written: {OUT / 'cp1_tables.json'} + 4 figures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
