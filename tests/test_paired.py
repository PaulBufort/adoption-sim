"""expand_paired_jobs (decision D19): common-random-numbers guarantees.

The contract under test: within one (base-combo, replicate) pair block, every
paired-axes condition sees the SAME organization, the SAME theta/willing/able
draws, and the SAME seed set when the strategy coincides — so contrasts are
within-replicate paired differences. Across replicates and base combos,
everything is freshly drawn (D14 untouched)."""

import numpy as np
import pytest

from core.dynamics import run_simulation
from core.orggen import generate_org
from core.scenario import build_sim_params, default_scenario, org_kwargs
from core.seeding import make_seeding
from core.sweep import expand_paired_jobs, sweep


def toy_scenario(reps=2):
    sc = default_scenario()
    sc["org"]["n_agents"] = 300
    sc["org"]["n_departments"] = 3
    sc["run"]["replicates"] = reps
    sc["run"]["master_seed"] = 7
    return sc


def seeds_key(ss):
    return (ss.entropy, ss.spawn_key)


def run_from_job(job):
    """Reproduce run_job's seed handling inline to expose the RunResult."""
    s_org, s_seed, s_dyn = job["seeds"]
    sc = job["scenario"]
    compiled = generate_org(**org_kwargs(sc), seed=np.random.default_rng(s_org)).compile()
    seeding = make_seeding(sc["seeding"]["strategy"], compiled, sc["seeding"]["budget"],
                           rng=np.random.default_rng(s_seed))
    result = run_simulation(compiled, build_sim_params(sc), seeding,
                            rng=np.random.default_rng(s_dyn))
    return compiled, seeding, result


def test_paired_blocks_share_the_seed_triple():
    jobs = expand_paired_jobs(toy_scenario(), {"seeding.strategy": ["random", "cluster"]},
                              replicates=2)
    assert len(jobs) == 4
    by_pair = {}
    for j in jobs:
        by_pair.setdefault(j["labels"]["pair_id"], []).append(j)
    assert set(by_pair) == {"0:0", "0:1"}
    for block in by_pair.values():
        assert len(block) == 2
        for a, b in zip(block[0]["seeds"], block[1]["seeds"]):
            assert seeds_key(a) == seeds_key(b)
    # Across replicates the triples differ (fresh org per replicate, D14).
    assert seeds_key(by_pair["0:0"][0]["seeds"][0]) != seeds_key(by_pair["0:1"][0]["seeds"][0])


def test_paired_determinism_and_base_axes():
    axes_p = {"seeding.strategy": ["random", "cluster"]}
    axes_b = {"agents.theta_mean": [0.25, 0.35]}
    j1 = expand_paired_jobs(toy_scenario(), axes_p, base_axes=axes_b, replicates=2)
    j2 = expand_paired_jobs(toy_scenario(), axes_p, base_axes=axes_b, replicates=2)
    assert len(j1) == 2 * 2 * 2
    for a, b in zip(j1, j2):
        assert seeds_key(a["seeds"][0]) == seeds_key(b["seeds"][0])
        assert a["labels"] == b["labels"]
    # Labels and scenario both carry the axis values.
    got = {(j["labels"]["agents.theta_mean"], j["labels"]["seeding.strategy"]) for j in j1}
    assert got == {(t, s) for t in (0.25, 0.35) for s in ("random", "cluster")}
    for j in j1:
        assert j["scenario"]["agents"]["theta_mean"] == j["labels"]["agents.theta_mean"]
        assert j["scenario"]["seeding"]["strategy"] == j["labels"]["seeding.strategy"]
    # Different base combos draw different organizations.
    assert seeds_key(j1[0]["seeds"][0]) != seeds_key(j1[4]["seeds"][0])


def test_paired_validation():
    sc = toy_scenario()
    sc["run"]["share_graph"] = True
    with pytest.raises(ValueError, match="share_graph"):
        expand_paired_jobs(sc, {"seeding.strategy": ["random"]})
    with pytest.raises(ValueError):
        expand_paired_jobs(toy_scenario(), {})


def test_crn_same_org_and_agents_across_strategies():
    jobs = expand_paired_jobs(toy_scenario(), {"seeding.strategy": ["random", "cluster"]},
                              replicates=1)
    (ca, _, ra), (cb, _, rb) = run_from_job(jobs[0]), run_from_job(jobs[1])
    np.testing.assert_array_equal(ca.indptr, cb.indptr)      # identical graph
    np.testing.assert_array_equal(ca.indices, cb.indices)
    np.testing.assert_array_equal(ca.weights, cb.weights)
    np.testing.assert_array_equal(ca.team, cb.team)
    np.testing.assert_array_equal(ra.theta, rb.theta)        # identical agent draws
    np.testing.assert_array_equal(ra.willing, rb.willing)
    np.testing.assert_array_equal(ra.able, rb.able)


def test_crn_decay_arms_share_agents_and_seeds():
    jobs = expand_paired_jobs(toy_scenario(), {"dynamics.relapse_prob": [0.0, 0.3]},
                              replicates=1)
    (_, sa, ra), (_, sb, rb) = run_from_job(jobs[0]), run_from_job(jobs[1])
    np.testing.assert_array_equal(sa.initial_adopters, sb.initial_adopters)
    np.testing.assert_array_equal(ra.theta, rb.theta)
    np.testing.assert_array_equal(ra.willing, rb.willing)
    np.testing.assert_array_equal(ra.able, rb.able)
    assert ra.curve[0] == rb.curve[0]
    # ever_adopted (the cumulative-reach tracker) always dominates final adoption.
    assert (ra.ever_adopted | ~ra.adopted).all() and (rb.ever_adopted | ~rb.adopted).all()


def test_run_robustness_pair_ids_are_globally_unique(tmp_path, monkeypatch):
    """User arbitration 2026-08-02: expand_paired_jobs restarts its block index
    per call, so run_robustness must prefix pair_id with the axis — otherwise
    '0:0' names different organizations in different axes of the same CSV."""
    import experiments.exp1 as exp1
    monkeypatch.setattr(exp1, "RESULTS", tmp_path)
    sc = exp1.smoke_variant(exp1.headline_scenario())
    sc["meta"]["name"] = "smoke"
    rows = exp1.run_robustness(
        sc, n_jobs=1, replicates=2,
        axes={"org.n_agents": [300, 350], "org.silo_strength": [0.5]},
    )
    assert len(rows) == (2 + 1) * 2 * 2          # cells x strategies x reps
    from collections import Counter
    counts = Counter(r["pair_id"] for r in rows)
    # Every pair block holds exactly the two strategies — no cross-axis merge.
    assert set(counts.values()) == {2}
    assert all(":" in pid for pid in counts)
    assert {r["pair_id"].split(":")[0] for r in rows} == {"n_agents", "silo_strength"}
    # Within a block the two rows are the two strategies on the same org.
    by_pid = {}
    for r in rows:
        by_pid.setdefault(r["pair_id"], []).append(r["strategy"])
    assert all(sorted(v) == ["cluster", "random"] for v in by_pid.values())
    assert (tmp_path / "exp1_robustness_smoke.csv").exists()


def test_robustness_axes_contain_the_headline_reference_exactly_once():
    """The duplicated-reference fix: 2000/8/0.85 is the headline configuration;
    it must be reachable through exactly one axis value (n_agents=2000)."""
    import experiments.exp1 as exp1
    sc = exp1.headline_scenario()
    hits = []
    for axis, values in exp1.ROBUSTNESS_AXES.items():
        current = sc[axis.split(".", 1)[0]][axis.split(".", 1)[1]]
        hits += [(axis, v) for v in values if v == current]
    assert hits == [("org.n_agents", 2000)]


def test_sweep_rows_carry_pair_id_and_parallel_equals_serial():
    jobs = expand_paired_jobs(toy_scenario(), {"seeding.strategy": ["random", "cluster"]},
                              replicates=2)
    serial = sweep(jobs, n_jobs=1)
    assert serial[0]["pair_id"] == "0:0"
    assert {r["pair_id"] for r in serial} == {"0:0", "0:1"}
    parallel = sweep(jobs, n_jobs=2)
    assert [r["final_rate"] for r in serial] == [r["final_rate"] for r in parallel]
