"""Scenario IO (TOML, validation, results) and the multiprocessing sweep."""

import json

import numpy as np
import pytest

from core.scenario import (
    build_sim_params,
    default_scenario,
    load_scenario,
    save_results,
    set_path,
)
from core.sweep import expand_jobs, run_job, sweep

TOY = """
[meta]
name = "toy"
[org]
n_agents = 300
n_departments = 3
[agents]
theta_mean = 0.3
[seeding]
strategy = "cluster"
budget = 0.05
[run]
replicates = 2
master_seed = 7
"""


def write_toml(tmp_path, text):
    p = tmp_path / "s.toml"
    p.write_text(text)
    return p


def test_load_scenario_merges_defaults(tmp_path):
    sc = load_scenario(write_toml(tmp_path, TOY))
    assert sc["org"]["n_agents"] == 300
    assert sc["org"]["silo_strength"] == default_scenario()["org"]["silo_strength"]
    assert sc["agents"]["p_innovator"] == 0.025
    params = build_sim_params(sc)
    assert params.theta_mean == 0.3


def test_typo_in_scenario_fails_loudly(tmp_path):
    bad = TOY.replace("theta_mean = 0.3", "theta_men = 0.3")
    with pytest.raises(ValueError, match="theta_mean"):
        load_scenario(write_toml(tmp_path, bad))
    bad2 = TOY.replace('strategy = "cluster"', 'strategy = "clutser"')
    with pytest.raises(ValueError, match="cluster"):
        load_scenario(write_toml(tmp_path, bad2))


def test_set_path():
    sc = default_scenario()
    v = set_path(sc, "agents.theta_mean", 0.4)
    assert v["agents"]["theta_mean"] == 0.4
    assert sc["agents"]["theta_mean"] != 0.4  # original untouched
    with pytest.raises(ValueError):
        set_path(sc, "agents.no_such_knob", 1)


def toy_scenario(reps=2):
    sc = default_scenario()
    sc["org"]["n_agents"] = 300
    sc["org"]["n_departments"] = 3
    sc["run"]["replicates"] = reps
    sc["run"]["master_seed"] = 7
    return sc


def test_expand_jobs_grid_and_determinism():
    sc = toy_scenario()
    axes = {"seeding.strategy": ["broadcast", "cluster"], "org.silo_strength": [0.5, 0.9]}
    jobs = expand_jobs(sc, axes, replicates=2)
    assert len(jobs) == 2 * 2 * 2
    assert jobs[0]["scenario"]["seeding"]["strategy"] == "broadcast"
    # Deterministic seeding: same master -> same spawned seed tree.
    jobs2 = expand_jobs(sc, axes, replicates=2)
    assert jobs[3]["seeds"][0].spawn_key == jobs2[3]["seeds"][0].spawn_key
    assert jobs[3]["seeds"][0].entropy == jobs2[3]["seeds"][0].entropy


def test_rerunning_same_jobs_reproduces():
    jobs = expand_jobs(toy_scenario(), {"seeding.strategy": ["random"]}, replicates=2)
    first = [run_job(j)["final_rate"] for j in jobs]
    second = [run_job(j)["final_rate"] for j in jobs]
    assert first == second


def test_run_job_row_shape():
    row = run_job(expand_jobs(toy_scenario(), {"seeding.strategy": ["random"]})[0])
    assert 0.0 <= row["final_rate"] <= 1.0
    assert row["strategy"] == "random"
    curve = json.loads(row["curve"])
    assert len(curve) == toy_scenario()["dynamics"]["max_steps"] + 1
    total = sum(row[f"n_{k}"] for k in ("adopted", "not_able", "not_willing", "not_ready", "relapsed"))
    assert total == 300


def test_sweep_parallel_equals_serial():
    sc = toy_scenario()
    jobs = expand_jobs(sc, {"seeding.strategy": ["random", "cluster"]}, replicates=2)
    serial = sweep(jobs, n_jobs=1)
    parallel = sweep(jobs, n_jobs=2)
    assert [r["final_rate"] for r in serial] == [r["final_rate"] for r in parallel]


def test_share_graph_mode_fixes_the_org():
    sc = toy_scenario(reps=3)
    sc["run"]["share_graph"] = True
    sc["seeding"]["strategy"] = "champions"
    rows = sweep(expand_jobs(sc), n_jobs=1)
    # Same org + same degree ranking; champions still differ by tie-break rng,
    # but the underlying graph is identical -> team count in team_rates equal.
    lens = {len(json.loads(r["team_rates"])) for r in rows}
    assert len(lens) == 1


def test_pilot_visibility_intervention_flows_through_sweep():
    """D17 observable pilots: low global visibility suppresses adoption; making the
    seeds loud (pilot_visibility=1.0) recovers part of it. Same seeds throughout."""
    base = toy_scenario(reps=3)
    base["agents"]["visibility"] = 0.4
    base["seeding"]["strategy"] = "cluster"
    quiet = [r["final_rate"] for r in sweep(expand_jobs(base), n_jobs=1)]
    loud_sc = json.loads(json.dumps(base))
    loud_sc["seeding"]["pilot_visibility"] = 1.0
    loud = [r["final_rate"] for r in sweep(expand_jobs(loud_sc), n_jobs=1)]
    full_sc = json.loads(json.dumps(base))
    full_sc["agents"]["visibility"] = 1.0
    full = [r["final_rate"] for r in sweep(expand_jobs(full_sc), n_jobs=1)]
    assert np.mean(full) > np.mean(quiet)          # v<1 suppresses adoption
    assert np.mean(loud) >= np.mean(quiet)         # loud pilots never hurt


def test_visibility_scenario_key_loads(tmp_path):
    toml = TOY + "\n" + "[agents.visibility]\n" if False else TOY.replace(
        "[agents]\ntheta_mean = 0.3", "[agents]\ntheta_mean = 0.3\nvisibility = 0.7")
    sc = load_scenario(write_toml(tmp_path, toml))
    assert build_sim_params(sc).visibility == 0.7


def test_save_results_with_metadata(tmp_path):
    rows = [{"a": 1, "final_rate": 0.5}, {"a": 2, "final_rate": 0.6}]
    out = save_results(rows, tmp_path / "res" / "toy.csv", scenario=toy_scenario())
    assert out.exists()
    meta = json.loads((tmp_path / "res" / "toy.meta.json").read_text())
    assert meta["data_is_synthetic"] is True
    assert meta["scenario"]["org"]["n_agents"] == 300
    assert "numpy" in meta["versions"]
