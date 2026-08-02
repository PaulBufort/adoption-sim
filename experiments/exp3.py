"""Experiment 3 — Observability of adoption (decision D17).

Question (scientist, arbitration 2026-06-10): real AI usage is largely invisible —
colleagues see outputs, not methods. Does visibility v < 1 change the
scattered-vs-cluster ordering from D16, and can the "observable pilots"
intervention (seeds work out loud at v = 1 while the world sits at v < 1)
rescue cluster seeding?

Known before running (D17 proposition, exactly verified in
tests/test_visibility.py): a *global* v is equivalent to rescaling every
threshold by 1/v, so it cannot reorder the seeded strategies. The sweep below
confirms it empirically; the intervention is the scientifically live part.

ALL DATA SYNTHETIC.
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from core.scenario import load_scenario, save_results, set_path  # noqa: E402
from core.sweep import expand_jobs, sweep, sweep_meta  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"

V_AXIS = [0.4, 0.6, 0.8, 1.0]
PILOT_V_GLOBALS = [0.4, 0.6, 0.8]
PILOT_STRATEGIES = ["cluster", "random", "champions"]
ALL_STRATEGIES = ["broadcast", "random", "champions", "cluster", "line_manager_first"]


def base_scenario() -> dict:
    sc = load_scenario(HERE / "scenarios" / "headline.toml")
    sc["meta"]["name"] = "observability"
    return sc


def run_global_v_sweep(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """All five strategies × global visibility. Prediction (D17 proposition):
    orderings preserved — global v only slides everyone along the θ̄ axis."""
    axes = {"seeding.strategy": ALL_STRATEGIES, "agents.visibility": V_AXIS}
    jobs = expand_jobs(sc, axes, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / "exp3_globalv.csv", sc, extra_meta=sweep_meta(jobs, axes))
    return rows


def run_observable_pilots(sc: dict, n_jobs: int | None = None, replicates: int = 12) -> list[dict]:
    """The intervention: seeds carry v = 1.0 (work-out-loud rituals) while the
    rest of the organization sits at v_global < 1. An intervention on the pilot
    cohort, not a structural assumption (D17)."""
    sc = set_path(sc, "seeding.pilot_visibility", 1.0)
    axes = {"seeding.strategy": PILOT_STRATEGIES, "agents.visibility": PILOT_V_GLOBALS}
    jobs = expand_jobs(sc, axes, replicates=replicates)
    rows = sweep(jobs, n_jobs)
    save_results(rows, RESULTS / "exp3_pilots.csv", sc, extra_meta=sweep_meta(jobs, axes))
    return rows
