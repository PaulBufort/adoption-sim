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
from core.sweep import expand_jobs, sweep  # noqa: E402

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
    jobs = expand_jobs(sc, {"seeding.strategy": STRATEGY_ORDER})
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_strategies_{sc['meta']['name']}.csv", sc)
    return rows


def run_kappa_companion(sc: dict, n_jobs: int | None = None) -> list[dict]:
    """Dual-regime headline, right panel (D1 arbitration): same scenario at
    κ = 12 — the 'lottery' regime where broadcast is a high-variance gamble."""
    sc = set_path(sc, "agents.theta_concentration", 12.0)
    jobs = expand_jobs(sc, {"seeding.strategy": STRATEGY_ORDER})
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_kappa12_{sc['meta']['name']}.csv", sc)
    return rows


PINNOV_AXIS = [0.0, 0.01, 0.025, 0.05]


def run_pinnov_sweep(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """D2 arbitration: first-class innovator-share sweep. The p = 0 cell is the
    clearly-labeled 'no-innovators' variant from D16 — never the default."""
    jobs = expand_jobs(
        sc,
        {"seeding.strategy": ["broadcast", "random", "cluster"],
         "agents.p_innovator": PINNOV_AXIS},
        replicates=replicates,
    )
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_pinnov_{sc['meta']['name']}.csv", sc)
    return rows


TB_AXIS = [1, 5, 20]


def run_broadcast_duration_sweep(sc: dict, n_jobs: int | None = None) -> list[dict]:
    """D8 arbitration: the 'what about repeated campaigns?' objection — broadcast
    with the comms term active for T_b ∈ {1, 5, 20} steps."""
    sc = set_path(sc, "seeding.strategy", "broadcast")
    jobs = expand_jobs(sc, {"dynamics.broadcast_steps": TB_AXIS})
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_tb_{sc['meta']['name']}.csv", sc)
    return rows


def run_silo_panel(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """Panel B data: final adoption vs silo strength for three strategies."""
    jobs = expand_jobs(
        sc,
        {"seeding.strategy": ["broadcast", "random", "cluster"],
         "org.silo_strength": SILO_AXIS},
        replicates=replicates,
    )
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_silo_{sc['meta']['name']}.csv", sc)
    return rows


def run_decay_demo(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """De-adoption switched on (D7: relapse when share < theta, prob 0.25/step).

    Finding (D7 amendment): no visible spike-then-relapse exists in this model —
    instead decay differentially punishes scattered adoption while cluster-seeded
    adoption, reinforced by local critical mass, is nearly decay-proof."""
    sc = set_path(sc, "dynamics.relapse_prob", 0.25)
    sc = set_path(sc, "dynamics.retention_factor", 1.0)
    sc = set_path(sc, "dynamics.max_steps", 80)
    jobs = expand_jobs(
        sc,
        {"seeding.strategy": ["broadcast", "random", "champions", "cluster"]},
        replicates=replicates,
    )
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_decay_{sc['meta']['name']}.csv", sc)
    return rows


# Regime map (referee request 2026-08-01): axes chosen to bracket the frozen
# headline point (θ̄=0.30, budget 0.05). PROVISIONAL D18 — pending arbitration.
REGIME_THETA_AXIS = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
REGIME_BUDGET_AXIS = [0.01, 0.02, 0.05, 0.10, 0.15]


def run_regime_map(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """ΔR map: mean final reach, random − cluster, over θ̄ × seed budget at
    otherwise-frozen headline parameters (κ=20). Turns the scoped claim
    "scattered wins in this regime" into an explicit boundary."""
    jobs = expand_jobs(
        sc,
        {"agents.theta_mean": REGIME_THETA_AXIS,
         "seeding.budget": REGIME_BUDGET_AXIS,
         "seeding.strategy": ["random", "cluster"]},
        replicates=replicates,
    )
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / f"exp1_regime_{sc['meta']['name']}.csv", sc)
    return rows


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
