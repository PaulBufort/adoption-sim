"""Experiment 1 — broadcast vs cluster seeding (the headline experiment).

Shared by the notebook (experiments/01_broadcast_vs_cluster.ipynb) and the CLI
(experiments/run_experiment1.py): one code path, two front ends, so CI smoke
runs and the published figure cannot drift apart.

ALL DATA IN THIS EXPERIMENT IS SYNTHETIC (docs/limitations.md #1).
"""

from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from core.scenario import load_scenario, save_results, set_path  # noqa: E402
from core.sweep import expand_jobs, expand_paired_jobs, sweep, sweep_meta  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
STRATEGY_ORDER = ["broadcast", "random", "champions", "cluster", "line_manager_first"]
SILO_AXIS = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]


def headline_scenario() -> dict:
    return load_scenario(HERE / "scenarios" / "headline.toml")


def smoke_variant(sc: dict) -> dict:
    """CI-sized: same structure, minutes -> seconds. Not for scientific claims."""
    sc = set_path(sc, "org.n_agents", 400)
    sc = set_path(sc, "org.n_departments", 4)
    sc = set_path(sc, "run.replicates", 2)
    sc = set_path(sc, "dynamics.max_steps", 40)
    return sc


def run_strategy_comparison(sc: dict, n_jobs: int | None = None) -> list[dict]:
    """Panel A data: all five strategies at the frozen headline parameters."""
    axes = {"seeding.strategy": STRATEGY_ORDER}
    jobs = expand_jobs(sc, axes)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_strategies_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, axes))
    return rows


def run_kappa_companion(sc: dict, n_jobs: int | None = None) -> list[dict]:
    """Dual-regime headline, right panel (D1 arbitration): same scenario at
    κ = 12 — the 'lottery' regime where broadcast is a high-variance gamble."""
    sc = set_path(sc, "agents.theta_concentration", 12.0)
    axes = {"seeding.strategy": STRATEGY_ORDER}
    jobs = expand_jobs(sc, axes)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_kappa12_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, axes))
    return rows


PINNOV_AXIS = [0.0, 0.01, 0.025, 0.05]


def run_pinnov_sweep(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """D2 arbitration: first-class innovator-share sweep. The p = 0 cell is the
    clearly-labeled 'no-innovators' variant from D16 — never the default."""
    axes = {"seeding.strategy": ["broadcast", "random", "cluster"],
            "agents.p_innovator": PINNOV_AXIS}
    jobs = expand_jobs(sc, axes, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_pinnov_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, axes))
    return rows


TB_AXIS = [1, 5, 20]


def run_broadcast_duration_sweep(sc: dict, n_jobs: int | None = None) -> list[dict]:
    """D8 arbitration: the 'what about repeated campaigns?' objection — broadcast
    with the comms term active for T_b ∈ {1, 5, 20} steps."""
    sc = set_path(sc, "seeding.strategy", "broadcast")
    axes = {"dynamics.broadcast_steps": TB_AXIS}
    jobs = expand_jobs(sc, axes)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_tb_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, axes))
    return rows


def run_silo_panel(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """Panel B data: final adoption vs silo strength for three strategies."""
    axes = {"seeding.strategy": ["broadcast", "random", "cluster"],
            "org.silo_strength": SILO_AXIS}
    jobs = expand_jobs(sc, axes, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_silo_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, axes))
    return rows


def run_decay_demo(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """De-adoption switched on (D7: relapse when share < theta, prob 0.25/step).

    Finding (D7 amendment): no visible spike-then-relapse exists in this model —
    instead decay differentially punishes scattered adoption while cluster-seeded
    adoption, reinforced by local critical mass, is nearly decay-proof."""
    sc = set_path(sc, "dynamics.relapse_prob", 0.25)
    sc = set_path(sc, "dynamics.retention_factor", 1.0)
    sc = set_path(sc, "dynamics.max_steps", 80)
    axes = {"seeding.strategy": ["broadcast", "random", "champions", "cluster"]}
    jobs = expand_jobs(sc, axes, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_decay_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, axes))
    return rows


# Regime map (referee request 2026-08-01): axes chosen to bracket the frozen
# headline point (θ̄=0.30, budget 0.05). D18 RATIFIED 2026-08-02 (CP1) as the
# paired n=50 3-class upgrade (run_paired_regime below); this n=12 harness is
# the superseded exploratory version.
REGIME_THETA_AXIS = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
REGIME_BUDGET_AXIS = [0.01, 0.02, 0.05, 0.10, 0.15]


def run_regime_map(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """ΔR map: mean final reach, random − cluster, over θ̄ × seed budget at
    otherwise-frozen headline parameters (κ=20). Turns the scoped claim
    "scattered wins in this regime" into an explicit boundary.

    SUPERSEDED by run_paired_regime (D19: 50 paired replicates, Holm-corrected
    3-class cells). Notebook 01 dropped its call at S4 (2026-08-03); kept as
    the documented exploratory harness only. Its n=12 CSV was never
    committed and the stray artifacts were deleted at S4."""
    axes = {"agents.theta_mean": REGIME_THETA_AXIS,
            "seeding.budget": REGIME_BUDGET_AXIS,
            "seeding.strategy": ["random", "cluster"]}
    jobs = expand_jobs(sc, axes, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_regime_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, axes))
    return rows


# --- Paired protocol (D19, RATIFIED 2026-08-02 CP1): common random numbers ------
# Same organizations + same theta/willing/able draws across the conditions of a
# pair block (core/sweep.expand_paired_jobs); contrasts analyzed as paired
# differences (experiments/stats.py). Seed layout frozen at implementation time
# (2026-08-02), BEFORE any paired result was inspected — no seed-fishing.

PAIRED_STRATEGIES = ["random", "champions", "cluster", "one_per_team"]
DECAY_R_AXIS = [0.5, 1.0]
DECAY_RHO_AXIS = [0.0, 0.10, 0.25, 0.40]
# One-at-a-time axes. The headline configuration appears exactly ONCE, as
# n_agents=2000; the other axes omit their headline value on purpose (user
# arbitration 2026-08-02): re-including team_size=8 would reproduce the
# n_agents=2000 arm BIT-IDENTICALLY (same spawn index -> same organizations),
# and silo=0.85 would triplicate the configuration under fresh seeds — silent
# duplication either way.
ROBUSTNESS_AXES = {
    "org.n_agents": [500, 2000, 8000],
    "org.mean_team_size": [5, 12],
    "org.silo_strength": [0.5, 0.7, 0.95],
}


def run_paired_headline(sc: dict, n_jobs: int | None = None,
                        replicates: int | None = None) -> list[dict]:
    """Paired strategy contrasts at the frozen headline point: the four seeded
    strategies evaluated on identical organizations (broadcast excluded — its
    zero-seed floor is established by the independent panel)."""
    axes = {"seeding.strategy": PAIRED_STRATEGIES}
    jobs = expand_paired_jobs(sc, axes, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_paired_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, {}, pair_axes=axes))
    return rows


def run_paired_regime(sc: dict, n_jobs: int | None = None,
                      replicates: int | None = None) -> list[dict]:
    """D18 upgraded: paired ΔR map over θ̄ × budget — random vs cluster on
    identical organizations in every cell, 50 pairs/cell by default. Analyzed
    with the 3-class Holm-corrected scheme (stats.classify_cells)."""
    base = {"agents.theta_mean": REGIME_THETA_AXIS,
            "seeding.budget": REGIME_BUDGET_AXIS}
    paired = {"seeding.strategy": ["random", "cluster"]}
    jobs = expand_paired_jobs(sc, paired, base_axes=base, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_regime_paired_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, base, pair_axes=paired))
    return rows


def run_paired_decay(sc: dict, n_jobs: int | None = None,
                     replicates: int | None = None) -> list[dict]:
    """Paired decay grid (D7 × D19): strategies × retention_factor r × relapse ρ
    on identical organizations. max_steps stays at the headline 100 (supersedes
    the 80-step n=12 demo).

    Arms vs contrasts (D19 amendment, pre-declared): the grid EXECUTES 24 arms
    (3 strategies × 2 r × 4 ρ; 1 200 sims at n=50) but the primary Holm family
    contains only the 7 UNIQUE random − cluster contrasts — one per (r, ρ>0)
    cell (2 × 3) plus ρ=0 counted once, because r is inert without relapse and
    its two ρ=0 arms are bit-identical (kept as a free self-check for the
    notebook). Primary endpoint: **final_rate**. cumulative_rate and
    retention_rate are secondary, descriptive-only metrics (paired CIs, no
    corrected win/equivalence claims); champions contrasts are descriptive too."""
    paired = {"seeding.strategy": ["random", "champions", "cluster"],
              "dynamics.retention_factor": DECAY_R_AXIS,
              "dynamics.relapse_prob": DECAY_RHO_AXIS}
    jobs = expand_paired_jobs(sc, paired, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_decay_paired_{sc['meta']['name']}.csv", sc,
                 extra_meta=sweep_meta(jobs, {}, pair_axes=paired))
    return rows


def run_robustness(sc: dict, n_jobs: int | None = None,
                   replicates: int | None = None,
                   axes: dict[str, list] | None = None) -> list[dict]:
    """One-at-a-time robustness of the paired random − cluster contrast around
    the frozen headline point: org size, team size, silo strength (κ=12 and the
    T_b/p_innov sweeps already exist as independent panels). One CSV, long
    format: (param, value, pair_id, strategy, ...).

    pair_id is prefixed with the axis short name: expand_paired_jobs restarts
    its block index per call, so raw pair_ids would collide across the three
    axes and a join on pair_id alone would silently mix them. The paired join
    key in this CSV is (param, value, pair_id) — pair_id alone stays unique
    only thanks to the prefix."""
    paired = {"seeding.strategy": ["random", "cluster"]}
    axes = ROBUSTNESS_AXES if axes is None else axes
    all_rows: list[dict] = []
    for axis, values in axes.items():
        short = axis.split(".", 1)[1]
        jobs = expand_paired_jobs(sc, paired, base_axes={axis: values},
                                  replicates=replicates)
        for r in sweep(jobs, n_jobs):
            value = r.pop(axis)
            r["pair_id"] = f"{short}:{r['pair_id']}"
            all_rows.append({"param": short, "value": value, **r})
    save_results(all_rows, RESULTS / f"exp1_robustness_{sc['meta']['name']}.csv", sc,
                 extra_meta={"design": "paired_within_replicate",
                             "axes": {k: list(v) for k, v in axes.items()},
                             "pair_axes": {k: list(v) for k, v in paired.items()},
                             "replicates_used": max(r["rep"] for r in all_rows) + 1})
    return all_rows


# --- Aggregation helpers (used by the notebook and the demo) -------------------

def curves_by(rows: list[dict], key: str = "strategy") -> dict[str, np.ndarray]:
    """Stack per-replicate curves: {label: array of shape (reps, T+1)}."""
    out: dict[str, list] = {}
    for r in rows:
        out.setdefault(str(r[key]), []).append(json.loads(r["curve"]))
    return {k: np.array(v) for k, v in out.items()}


def band(stack: np.ndarray, lo: float = 10, hi: float = 90):
    """(mean, low, high) percentile band across replicates."""
    return stack.mean(axis=0), np.percentile(stack, lo, axis=0), np.percentile(stack, hi, axis=0)


def finals_by(rows: list[dict], *keys: str) -> dict[tuple, np.ndarray]:
    out: dict[tuple, list] = {}
    for r in rows:
        out.setdefault(tuple(r[k] for k in keys), []).append(r["final_rate"])
    return {k: np.array(v) for k, v in out.items()}


def dept_rate_means(rows: list[dict]) -> dict[str, np.ndarray]:
    """Mean final adoption per department, per strategy: the unit map."""
    acc: dict[str, list] = {}
    for r in rows:
        rates = json.loads(r["dept_rates"])
        vec = np.array([rates[k] for k in sorted(rates, key=int)])
        acc.setdefault(str(r["strategy"]), []).append(vec)
    return {k: np.mean(v, axis=0) for k, v in acc.items()}


def summary_table(rows: list[dict]) -> list[dict]:
    """One line per strategy: mean +- sd of final rate, attribution means."""
    table = []
    for strat in STRATEGY_ORDER:
        sub = [r for r in rows if r["strategy"] == strat]
        if not sub:
            continue
        finals = np.array([r["final_rate"] for r in sub])
        n = sum(r[f"n_{k}"] for k in ("adopted", "not_able", "not_willing", "not_ready", "relapsed")
                for r in sub[:1])
        table.append({
            "strategy": strat,
            "final_mean": round(float(finals.mean()), 3),
            "final_sd": round(float(finals.std()), 3),
            "final_min": round(float(finals.min()), 3),
            "final_max": round(float(finals.max()), 3),
            "mean_not_ready_share": round(
                float(np.mean([r["n_not_ready"] / n for r in sub])), 3),
            "replicates": len(sub),
        })
    return table
