"""Metrics: curve summaries, dead pockets, pivot-node knockouts."""

import numpy as np

from core.dynamics import SimParams, run_simulation
from core.metrics import (
    PivotReport,
    dead_pockets,
    dept_rates,
    pivot_nodes,
    plateau,
    relapse_magnitude,
    time_to_level,
)
from core.seeding import Seeding
from tests.helpers import fixed_agents, tiny_org


def test_curve_summaries():
    curve = np.array([0.0, 0.2, 0.5, 0.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3])
    assert plateau(curve, tail=5) == 0.3
    assert relapse_magnitude(curve, tail=5) == 0.5 - 0.3
    assert time_to_level(curve, 0.45) == 2
    assert time_to_level(curve, 0.9) is None


def test_dead_pockets_both_forms():
    assert dead_pockets({0: 0.9, 1: 0.1, 2: 0.24, 3: 0.25}, cutoff=0.25) == [1, 2]
    assert dead_pockets(np.array([0.9, 0.1, 0.3]), cutoff=0.25) == [1]


def barbell():
    """Two 5-cliques joined only through node 5 (the relay)."""
    edges = []
    a, b = range(5), range(6, 11)
    edges += [(i, j, 1.0) for i in a for j in a if i < j]
    edges += [(i, j, 1.0) for i in b for j in b if i < j]
    edges += [(0, 5, 1.0), (1, 5, 1.0), (5, 6, 1.0), (5, 7, 1.0)]
    team = [0] * 5 + [0] + [1] * 5
    dept = [0] * 5 + [0] + [1] * 5
    return tiny_org(edges, team=team, dept=dept)


def explicit_seeds(*ids):
    def factory(compiled, rng):
        return Seeding("random", np.array(ids, dtype=np.int64), False, {})
    return factory


def test_pivot_node_knockout_finds_the_relay():
    c = barbell()
    params = SimParams(max_steps=30)
    agents_theta = 0.2

    def factory(compiled, rng):
        return Seeding("random", np.array([0, 1], dtype=np.int64), False, {})

    # Monkeypatch-free determinism: force theta via a wrapper factory is not
    # possible, so use a params trick: extremely concentrated Beta at 0.2.
    params = SimParams(theta_mean=0.2, theta_concentration=10000, p_innovator=0.0,
                       p_willing=(1.0, 1.0, 1.0), max_steps=30)
    reports = pivot_nodes(c, params, factory, candidates=[5, 2], reps=3, rng_seed=1)
    by_node = {r.node: r for r in reports}
    # Removing the relay (5) cuts clique B off entirely; removing 2 changes ~nothing.
    assert by_node[5].is_pivot
    assert by_node[5].delta_plateau > 0.3
    assert not by_node[2].is_pivot
    assert reports[0].node == 5  # sorted by impact


def test_dept_rates_and_attribution_partition():
    c = barbell()
    params = SimParams(theta_mean=0.2, theta_concentration=10000, p_innovator=0.0,
                       p_willing=(1.0, 1.0, 1.0), max_steps=30)
    seeding = Seeding("random", np.array([0, 1], dtype=np.int64), False, {})
    res = run_simulation(c, params, seeding, rng=3)
    rates = dept_rates(res, c)
    assert rates[0] == 1.0 and rates[1] == 1.0  # cascade crosses the relay
    assert isinstance(res, type(res))
