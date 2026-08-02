"""run_job's D19 outcome columns: cumulative/retention (ever_adopted tracker,
active-agent denominator) and seeded_teams (meso provenance).

NOTE: written alongside the run_job column change; both land together in the
CP1 regeneration commit (they change every results CSV, hence the bit-for-bit
CI gate requires the coordinated regeneration)."""

import json

import numpy as np

from core.sweep import expand_jobs, expand_paired_jobs, run_job


def toy_scenario(reps=1):
    from core.scenario import default_scenario
    sc = default_scenario()
    sc["org"]["n_agents"] = 300
    sc["org"]["n_departments"] = 3
    sc["run"]["replicates"] = reps
    sc["run"]["master_seed"] = 7
    return sc


def test_columns_present_and_consistent_without_decay():
    row = run_job(expand_jobs(toy_scenario(), {"seeding.strategy": ["random"]})[0])
    # No decay: nobody ever relapses, so cumulative == final and retention == 1.
    assert row["cumulative_rate"] == row["final_rate"]
    assert row["retention_rate"] == 1.0
    teams = json.loads(row["seeded_teams"])
    assert teams == sorted(set(teams)) and len(teams) >= 1
    # (random may legitimately seed any team, incl. leadership — no invariant here)


def test_cumulative_reads_the_ever_adopted_tracker_under_decay():
    """cumulative_rate must equal ever_adopted among active agents EXACTLY.

    Deliberately NOT the attribution shortcut (n_adopted + n_relapsed)/n: seeds
    adopt unconditionally (D9), so a non-willing seed that relapses is
    attributed NOT_WILLING, not RELAPSED — the shortcut undercounts. This test
    documents why D19 mandates reading the tracker directly."""
    sc = toy_scenario()
    sc["dynamics"]["relapse_prob"] = 0.3
    sc["dynamics"]["retention_factor"] = 1.0
    job = expand_jobs(sc, {"seeding.strategy": ["random"]})[0]
    row = run_job(job)
    n = 300
    shortcut = (row["n_adopted"] + row["n_relapsed"]) / n
    k_seeds = int(np.floor(sc["seeding"]["budget"] * n))
    # The tracker dominates the shortcut; the gap is at most the seed count
    # (only unconditional seeds can be ever-adopters outside willing&able).
    assert row["cumulative_rate"] >= shortcut - 1e-9
    assert row["cumulative_rate"] - shortcut <= k_seeds / n + 1e-9
    # Exact check against the engine state, reproduced inline from the job.
    from core.orggen import generate_org
    from core.scenario import build_sim_params, org_kwargs
    from core.seeding import make_seeding
    from core.dynamics import run_simulation
    s_org, s_seed, s_dyn = job["seeds"]
    compiled = generate_org(**org_kwargs(job["scenario"]),
                            seed=np.random.default_rng(s_org)).compile()
    seeding = make_seeding("random", compiled, job["scenario"]["seeding"]["budget"],
                           rng=np.random.default_rng(s_seed))
    res = run_simulation(compiled, build_sim_params(job["scenario"]), seeding,
                         rng=np.random.default_rng(s_dyn))
    assert abs(row["cumulative_rate"] - res.ever_adopted[compiled.active].mean()) < 1e-6
    assert row["cumulative_rate"] >= row["final_rate"]
    if row["cumulative_rate"] > 0:
        # retention is computed from EXACT values then rounded to 6 dp; the
        # ratio of the rounded columns differs by up to ~1e-5.
        assert abs(row["retention_rate"] - row["final_rate"] / row["cumulative_rate"]) < 5e-5


def test_retention_blank_when_nothing_ever_adopts():
    sc = toy_scenario()
    sc["agents"]["p_innovator"] = 0.0
    sc["agents"]["theta_mean"] = 0.9   # broadcast alone cannot ignite anyone
    row = run_job(expand_jobs(sc, {"seeding.strategy": ["broadcast"]})[0])
    assert row["cumulative_rate"] == 0.0
    assert row["retention_rate"] == ""
    assert json.loads(row["seeded_teams"]) == []


def test_seeded_teams_matches_strategy_semantics():
    jobs = expand_paired_jobs(toy_scenario(),
                              {"seeding.strategy": ["cluster", "one_per_team"]},
                              replicates=1)
    rows = {r["strategy"]: r for r in map(run_job, jobs)}
    cl = json.loads(rows["cluster"]["seeded_teams"])
    opt = json.loads(rows["one_per_team"]["seeded_teams"])
    assert len(cl) < len(opt)          # concentration vs coverage
    assert 0 not in cl and 0 not in opt  # synthetic org: leadership excluded
