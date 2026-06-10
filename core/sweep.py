"""Parameter sweeps with multiprocessing (spec §3) and the tornado sensitivity
analysis (spec §2.3).

Reproducibility: jobs are seeded from a master ``numpy.random.SeedSequence``
spawned in the parent, so results are identical for any worker count (D14).
Workers are module-level functions (macOS/Windows spawn-safe; usable from
notebooks because the work lives in this importable module, not in cells).

Stack policy: numpy + stdlib only.
"""

from __future__ import annotations

import itertools
import json
import multiprocessing
import os

import numpy as np

from core.dynamics import run_simulation
from core.metrics import dept_rates, plateau, relapse_magnitude
from core.orggen import generate_org
from core.scenario import build_sim_params, org_kwargs, set_path


def expand_jobs(scenario: dict, axes: dict[str, list] | None = None,
                replicates: int | None = None) -> list[dict]:
    """Cartesian product of dotted-path axes × replicates, with spawned seeds.

    axes example: {"seeding.strategy": ["broadcast", "cluster"],
                   "org.silo_strength": [0.5, 0.85]}
    """
    axes = axes or {}
    reps = replicates if replicates is not None else scenario["run"]["replicates"]
    master = np.random.SeedSequence(scenario["run"]["master_seed"])
    names = list(axes)
    combos = list(itertools.product(*axes.values())) if axes else [()]
    children = master.spawn(len(combos) * reps)
    jobs = []
    for ci, combo in enumerate(combos):
        variant = scenario
        for name, value in zip(names, combo):
            variant = set_path(variant, name, value)
        for rep in range(reps):
            # Pre-spawn the (org, seeding, dynamics) seed triple HERE: run_job must
            # never mutate the job, or re-running the same jobs would silently
            # change results (SeedSequence.spawn advances a counter).
            s_org, s_seed, s_dyn = children[ci * reps + rep].spawn(3)
            jobs.append({
                "scenario": variant,
                "labels": dict(zip(names, combo)),
                "rep": rep,
                "seeds": (s_org, s_seed, s_dyn),
                "condition_index": ci,
            })
    return jobs


def run_job(job: dict) -> dict:
    """One replicate -> one flat result row. Module-level for pickling."""
    from core.seeding import make_seeding  # local import keeps spawn cheap

    sc = job["scenario"]
    # share_graph (D14 option 2): the org seed depends on the condition only,
    # so every replicate of a condition gets the *same* organization.
    s_org, s_seed, s_dyn = job["seeds"]
    if sc["run"].get("share_graph"):
        s_org = np.random.SeedSequence((sc["run"]["master_seed"], job["condition_index"]))
    rng_org = np.random.default_rng(s_org)
    rng_seed = np.random.default_rng(s_seed)
    rng_dyn = np.random.default_rng(s_dyn)

    org = generate_org(**org_kwargs(sc), seed=rng_org)
    compiled = org.compile()
    seeding = make_seeding(
        sc["seeding"]["strategy"], compiled, sc["seeding"]["budget"], rng=rng_seed
    )
    params = build_sim_params(sc)
    # D17 "observable pilots" intervention: seeds carry pilot_visibility while the
    # rest of the organization sits at the global agents.visibility.
    pilot_v = sc["seeding"].get("pilot_visibility")
    visibility = None
    if pilot_v is not None:
        visibility = np.full(compiled.n, float(params.visibility))
        visibility[seeding.initial_adopters] = float(pilot_v)
    result = run_simulation(compiled, params, seeding, rng=rng_dyn, visibility=visibility)
    counts = result.attribution_counts()
    row = {
        **{k: v for k, v in job["labels"].items()},
        "rep": job["rep"],
        "strategy": sc["seeding"]["strategy"],
        "final_rate": round(result.final_rate, 6),
        "peak_rate": round(result.peak_rate, 6),
        "plateau": round(plateau(result.curve), 6),
        "relapse": round(relapse_magnitude(result.curve), 6),
        "steps_to_fixed_point": result.steps_to_fixed_point,
        "converged": result.converged,
        **{f"n_{k}": v for k, v in counts.items()},
        "curve": json.dumps(np.round(result.curve, 5).tolist()),
        "dept_rates": json.dumps({str(k): round(v, 4) for k, v in dept_rates(result, compiled).items()}),
        "team_rates": json.dumps(np.round(result.team_final, 4).tolist()),
    }
    return row


def sweep(jobs: list[dict], n_jobs: int | None = None) -> list[dict]:
    """Run jobs, in order, on n_jobs processes (default: cores - 1, min 1)."""
    if not jobs:
        return []
    if n_jobs is None:
        n_jobs = max(1, (os.cpu_count() or 2) - 1)
    if n_jobs == 1 or len(jobs) == 1:
        return [run_job(j) for j in jobs]
    chunk = max(1, len(jobs) // (4 * n_jobs))
    with multiprocessing.get_context("spawn").Pool(n_jobs) as pool:
        return list(pool.imap(run_job, jobs, chunksize=chunk))


def tornado(scenario: dict, perturb: dict[str, tuple], replicates: int = 10,
            n_jobs: int | None = None) -> list[dict]:
    """One-at-a-time sensitivity: for each dotted param, run (low, high) variants
    and report the plateau swing, sorted descending — tornado chart data."""
    jobs = expand_jobs(scenario, axes=None, replicates=replicates)
    base_rows = sweep(jobs, n_jobs)
    base = float(np.mean([r["plateau"] for r in base_rows]))
    out = []
    for name, (lo, hi) in perturb.items():
        side_means = {}
        for label, value in (("low", lo), ("high", hi)):
            variant = set_path(scenario, name, value)
            rows = sweep(expand_jobs(variant, axes=None, replicates=replicates), n_jobs)
            side_means[label] = float(np.mean([r["plateau"] for r in rows]))
        out.append({
            "param": name, "low_value": lo, "high_value": hi,
            "low_mean": round(side_means["low"], 4),
            "high_mean": round(side_means["high"], 4),
            "base_mean": round(base, 4),
            "swing": round(abs(side_means["high"] - side_means["low"]), 4),
        })
    out.sort(key=lambda r: -r["swing"])
    return out
