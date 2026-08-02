"""S2 harness: exp4 real-graph paired protocol, paired CSV loaders, V1 gate.

The strongest test here is test_exp4_crn_identical_strategy_rows: running the
SAME strategy twice inside one pair block must yield bit-identical rows — the
full common-random-numbers guarantee (same attributes, same seeds, same
dynamics) exercised end to end on an imported graph."""

import csv
import json
import math

import networkx as nx
import numpy as np
import pytest

from core.ingest import as_org
from experiments.exp4_realgraph import run_realgraph_paired
from experiments.paired_io import aligned_pair, cell_finals, read_rows
from core.scenario import default_scenario


def toy_real_org(n_comm=3, size=8, seed=0):
    """Small imported-style org: n_comm cliques + a ring of bridges."""
    rng = np.random.default_rng(seed)
    g = nx.Graph()
    for c in range(n_comm):
        members = [f"c{c}n{i}" for i in range(size)]
        for i in range(size):
            for j in range(i + 1, size):
                if rng.random() < 0.9:
                    g.add_edge(members[i], members[j])
        for m in members:
            g.add_node(m, com=str(c))
    for c in range(n_comm):
        g.add_edge(f"c{c}n0", f"c{(c + 1) % n_comm}n0")
    return as_org(g, source="toy", team_attr="com").compile()


def toy_sc():
    sc = default_scenario()
    sc["seeding"]["budget"] = 0.2
    sc["agents"]["theta_mean"] = 0.25
    return sc


def test_exp4_paired_structure_and_determinism():
    c = toy_real_org()
    rows1 = run_realgraph_paired(c, toy_sc(), strategies=("random", "cluster"),
                                 replicates=3, master_entropy=(7, 4))
    rows2 = run_realgraph_paired(c, toy_sc(), strategies=("random", "cluster"),
                                 replicates=3, master_entropy=(7, 4))
    assert rows1 == rows2                       # bit-exact reproducibility
    assert len(rows1) == 6
    by_pid = {}
    for r in rows1:
        by_pid.setdefault(r["pair_id"], []).append(r["strategy"])
    assert all(sorted(v) == ["cluster", "random"] for v in by_pid.values())
    # Decay off: cumulative == terminal, retention == 1 wherever anyone adopted.
    for r in rows1:
        assert r["cumulative_rate"] == r["final_rate"]
        if r["cumulative_rate"] > 0:
            assert r["retention_rate"] == 1.0
    # A different master entropy draws different attributes.
    rows3 = run_realgraph_paired(c, toy_sc(), strategies=("random", "cluster"),
                                 replicates=3, master_entropy=(8, 4))
    assert rows3 != rows1


def test_exp4_crn_identical_strategy_rows():
    """Same strategy twice in one block -> same triple -> bit-identical rows
    (module the strategy label). This is the CRN guarantee end to end."""
    c = toy_real_org()
    rows = run_realgraph_paired(c, toy_sc(), strategies=("random", "random"),
                                replicates=2, master_entropy=(7, 4))
    for pid in {r["pair_id"] for r in rows}:
        a, b = [r for r in rows if r["pair_id"] == pid]
        assert a == b


def test_exp4_department_zero_is_seedable():
    c = toy_real_org()
    rows = run_realgraph_paired(c, toy_sc(), strategies=("cluster",),
                                replicates=4, master_entropy=(7, 4))
    seeded = set()
    for r in rows:
        seeded |= set(json.loads(r["seeded_teams"]))
    assert 0 in seeded                          # D22: unit 0 ordinary on imports


def test_paired_io_roundtrip_and_alignment(tmp_path):
    p = tmp_path / "toy.csv"
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["agents.theta_mean", "pair_id",
                                           "strategy", "final_rate", "retention_rate"])
        w.writeheader()
        for theta in (0.2, 0.3):
            for pid in ("0:0", "0:1"):
                w.writerow({"agents.theta_mean": theta, "pair_id": pid,
                            "strategy": "random", "final_rate": 0.7, "retention_rate": ""})
                w.writerow({"agents.theta_mean": theta, "pair_id": pid,
                            "strategy": "cluster", "final_rate": 0.3, "retention_rate": 0.9})
    rows = read_rows(p)
    assert rows[0]["final_rate"] == 0.7
    assert math.isnan(rows[0]["retention_rate"]) and rows[1]["retention_rate"] == 0.9
    cells = cell_finals(rows, ("agents.theta_mean",))
    assert set(cells) == {("0.2",), ("0.3",)}
    x, y = aligned_pair(cells[("0.2",)], "random", "cluster")
    np.testing.assert_allclose(x, [0.7, 0.7])
    np.testing.assert_allclose(y, [0.3, 0.3])
    broken = {"random": {"0:0": 0.7}, "cluster": {"0:1": 0.3}}
    with pytest.raises(ValueError, match="pair_id sets differ"):
        aligned_pair(broken, "random", "cluster")


def test_v1_harness_smoke_one_replicate():
    """One replicate of the real V1 reconstruction: structure + sane values."""
    from experiments.validate_predictor import v1_on_paired_headline
    v1 = v1_on_paired_headline(replicates=1)
    assert v1["n_units"] > 50                   # 4 strategies' seeded teams
    assert v1["tp"] + v1["fp"] + v1["tn"] + v1["fn"] == v1["n_units"]
    assert (0.0 <= v1["auc"] <= 1.0) or math.isnan(v1["auc"])
    assert set(v1["per_strategy"]) == {"random", "champions", "cluster", "one_per_team"}
    assert 0.0 <= v1["base_rate_observed"] <= 1.0
