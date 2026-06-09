"""Contagion engine: threshold rule, R/W/A gating, conservation, decay, determinism."""

import numpy as np
import pytest

from core.dynamics import (
    ATTR_ADOPTED,
    ATTR_NOT_ABLE,
    ATTR_NOT_READY,
    ATTR_NOT_WILLING,
    ATTR_RELAPSED,
    SimParams,
    run_simulation,
)
from core.orggen import generate_org
from core.seeding import Seeding, make_seeding
from tests.helpers import fixed_agents, tiny_org

NO_SEEDS = lambda *ids: Seeding("random", np.array(ids, dtype=np.int64), False, {})
BROADCAST = Seeding("broadcast", np.empty(0, dtype=np.int64), True, {})


def run(compiled, theta, seeding, willing=None, able=None, **params):
    agents = fixed_agents(compiled.n, theta, willing, able)
    return run_simulation(compiled, SimParams(**params), seeding, rng=1, agents=agents)


def test_fractional_threshold_exact_boundary():
    # Node 0 has two equal-weight contacts; one adopts -> share = 0.5.
    edges = [(0, 1, 1.0), (0, 2, 1.0)]
    res = run(tiny_org(edges), [0.5, 0.9, 0.9], NO_SEEDS(1))
    assert res.adopted[0]  # share 0.5 >= theta 0.5 (boundary adopts)
    res = run(tiny_org(edges), [0.51, 0.9, 0.9], NO_SEEDS(1))
    assert not res.adopted[0]  # share 0.5 < theta 0.51


def test_credibility_weights_change_the_outcome():
    # Same topology, different source credibility: a comms-like weak tie (0.3)
    # vs a close peer (1.0) endorsing to a theta=0.4 agent with one other contact.
    weak = tiny_org([(0, 1, 0.3), (0, 2, 1.0)])
    strong = tiny_org([(0, 1, 1.0), (0, 2, 1.0)])
    assert not run(weak, [0.4] * 3, NO_SEEDS(1)).adopted[0]   # 0.3/1.3 = 0.23 < 0.4
    assert run(strong, [0.4] * 3, NO_SEEDS(1)).adopted[0]     # 1/2 = 0.5 >= 0.4


def test_awareness_gate_blocks_zero_threshold_spontaneity():
    # theta = 0 innovators do NOT ignite without any exposure (D4)...
    edges = [(0, 1, 1.0), (1, 2, 1.0)]
    res = run(tiny_org(edges), [0.0, 0.9, 0.9], Seeding("random", np.empty(0, np.int64), False, {}))
    assert res.final_rate == 0.0
    # ...but a broadcast makes them aware and they adopt (D8).
    res = run(tiny_org(edges), [0.0, 0.9, 0.9], BROADCAST)
    assert res.adopted[0] and not res.adopted[1] and not res.adopted[2]


def test_broadcast_share_includes_comms_term():
    # Node 0: one contact of weight 1.0, non-adopted. During broadcast:
    # share = 0.3 / 1.3 ~ 0.2308. theta just below adopts, just above does not.
    edges = [(0, 1, 1.0)]
    assert run(tiny_org(edges), [0.23, 0.9], BROADCAST).adopted[0]
    assert not run(tiny_org(edges), [0.24, 0.9], BROADCAST).adopted[0]


def test_willing_able_gates_and_attribution():
    edges = [(0, 1, 1.0), (2, 1, 1.0), (3, 1, 1.0)]
    theta = [0.3, 0.0, 0.3, 0.3]
    willing = [False, True, True, True]
    able = [True, True, False, True]
    res = run(tiny_org(edges), theta, NO_SEEDS(1), willing=willing, able=able)
    assert not res.adopted[0] and res.attribution_code[0] == ATTR_NOT_WILLING
    assert not res.adopted[2] and res.attribution_code[2] == ATTR_NOT_ABLE
    assert res.adopted[3] and res.attribution_code[3] == ATTR_ADOPTED
    counts = res.attribution_counts()
    assert sum(counts.values()) == 4


def test_attribution_partitions_population():
    org = generate_org(n_agents=400, seed=7)
    c = org.compile()
    seeding = make_seeding("random", c, budget=0.05, rng=7)
    res = run_simulation(c, SimParams(), seeding, rng=7)
    counts = res.attribution_counts()
    assert sum(counts.values()) == c.n
    assert counts["adopted"] == int(res.adopted.sum())


def test_curve_monotone_without_decay_and_padded():
    org = generate_org(n_agents=400, seed=3)
    c = org.compile()
    res = run_simulation(c, SimParams(max_steps=60), make_seeding("cluster", c, 0.05, 3), rng=3)
    assert len(res.curve) == 61
    assert np.all(np.diff(res.curve) >= -1e-12)
    if res.converged:
        tail = res.curve[res.steps_to_fixed_point:]
        assert np.allclose(tail, tail[0])


def test_relapse_hysteresis():
    # An isolated-among-non-adopters seed has share 0 < r*theta -> certain relapse.
    edges = [(0, 1, 1.0), (1, 2, 1.0), (2, 0, 1.0)]
    res = run(
        tiny_org(edges), [0.9, 0.9, 0.9], NO_SEEDS(0),
        relapse_prob=1.0, retention_factor=0.5, max_steps=10,
    )
    assert not res.adopted[0]
    assert res.ever_adopted[0]
    assert res.attribution_code[0] == ATTR_RELAPSED
    assert res.final_rate == 0.0


def test_no_relapse_when_reinforced():
    # Fully adopted triangle: share = 1 for everyone, never below r*theta.
    edges = [(0, 1, 1.0), (1, 2, 1.0), (2, 0, 1.0)]
    res = run(
        tiny_org(edges), [0.2] * 3, NO_SEEDS(0, 1, 2),
        relapse_prob=0.5, retention_factor=0.9, max_steps=30,
    )
    assert res.final_rate == 1.0


def test_cascade_saturates_clique():
    n = 20
    edges = [(i, j, 1.0) for i in range(n) for j in range(i + 1, n)]
    res = run(tiny_org(edges), 0.2, NO_SEEDS(*range(5)))
    assert res.final_rate == 1.0
    assert res.converged


def test_determinism_same_seed_same_curve():
    org = generate_org(n_agents=400, seed=11)
    c = org.compile()
    p = SimParams(relapse_prob=0.1)
    r1 = run_simulation(c, p, make_seeding("random", c, 0.05, 11), rng=11)
    r2 = run_simulation(c, p, make_seeding("random", c, 0.05, 11), rng=11)
    np.testing.assert_array_equal(r1.curve, r2.curve)
    np.testing.assert_array_equal(r1.adopted, r2.adopted)


def test_knockout_node_cannot_adopt_or_expose():
    edges = [(0, 1, 1.0), (1, 2, 1.0)]
    c = tiny_org(edges).without_node(1)
    res = run(c, [0.1, 0.1, 0.1], NO_SEEDS(0))
    assert not res.adopted[1] and not res.adopted[2]
    assert res.attribution_code[1] == -1  # inactive: excluded from attribution
    with pytest.raises(ValueError):
        run(c, [0.1] * 3, NO_SEEDS(1))  # cannot seed a knocked-out agent


def test_seeds_adopt_unconditionally():
    edges = [(0, 1, 1.0)]
    res = run(tiny_org(edges), [0.9, 0.9], NO_SEEDS(0), willing=[False, True], able=[False, True])
    assert res.adopted[0]


def test_param_validation():
    c = tiny_org([(0, 1, 1.0)])
    with pytest.raises(ValueError):
        run_simulation(c, SimParams(theta_mean=1.5), NO_SEEDS(0), rng=0)
    with pytest.raises(ValueError):
        run_simulation(c, SimParams(p_innovator=-0.1), NO_SEEDS(0), rng=0)


def test_able_rates_per_department():
    team = [0, 0, 1, 1]
    dept = [0, 0, 1, 1]
    edges = [(0, 1, 1.0), (2, 3, 1.0), (1, 2, 0.6)]
    c = tiny_org(edges, team=team, dept=dept)
    params = SimParams(theta_mean=0.05, theta_concentration=50, p_innovator=0,
                       p_willing=(1.0, 1.0, 1.0), able_rates={1: 0.0})
    res = run_simulation(c, params, NO_SEEDS(0), rng=5)
    assert not res.adopted[2] and not res.adopted[3]
    assert res.attribution_code[2] == ATTR_NOT_ABLE
