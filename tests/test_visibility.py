"""D17 visibility: hand-computed cases, the theta/v equivalence, pilot override."""

import numpy as np
import pytest

from core.dynamics import SimParams, draw_agents, run_simulation
from core.orggen import generate_org
from core.seeding import Seeding, make_seeding
from tests.helpers import fixed_agents, tiny_org

SEED = lambda *ids: Seeding("random", np.array(ids, dtype=np.int64), False, {})
BROADCAST = Seeding("broadcast", np.empty(0, dtype=np.int64), True, {})


def run(compiled, theta, seeding, vis_array=None, **params):
    agents = fixed_agents(compiled.n, theta)
    return run_simulation(compiled, SimParams(**params), seeding, rng=1,
                          agents=agents, visibility=vis_array)


def test_global_visibility_attenuates_exposure():
    # Node 0 has two unit-weight contacts, one adopted.
    # v=0.5 -> visible share = 0.25: theta 0.25 adopts, 0.26 does not.
    edges = [(0, 1, 1.0), (0, 2, 1.0)]
    res = run(tiny_org(edges), [0.25, 0.9, 0.9], SEED(1), **{"visibility": 0.5})
    assert res.adopted[0]
    res = run(tiny_org(edges), [0.26, 0.9, 0.9], SEED(1), **{"visibility": 0.5})
    assert not res.adopted[0]


def test_visibility_zero_blocks_awareness_except_broadcast():
    edges = [(0, 1, 1.0)]
    # v=0: an adopted contact is invisible -> no awareness, no adoption ever.
    res = run(tiny_org(edges), [0.0, 0.9], SEED(1), **{"visibility": 0.0})
    assert not res.adopted[0]
    # ...but a broadcast is fully visible by nature (D17): innovators still ignite.
    res = run(tiny_org(edges), [0.0, 0.9], BROADCAST, **{"visibility": 0.0})
    assert res.adopted[0]


def test_theta_over_v_equivalence_exact():
    """D17 proposition: global v with thresholds theta == v=1 with thresholds theta/v,
    exactly, for any no-broadcast scenario (including decay)."""
    org = generate_org(n_agents=400, seed=21)
    c = org.compile()
    v = 0.5
    base = SimParams(relapse_prob=0.2, retention_factor=0.8, max_steps=60)
    theta, willing, able = draw_agents(c, base, np.random.default_rng(5))
    seeding = make_seeding("cluster", c, 0.05, rng=5)

    p_v = SimParams(relapse_prob=0.2, retention_factor=0.8, max_steps=60, visibility=v)
    r_attenuated = run_simulation(c, p_v, seeding, rng=7, agents=(theta, willing, able))
    p_1 = SimParams(relapse_prob=0.2, retention_factor=0.8, max_steps=60, visibility=1.0)
    r_rescaled = run_simulation(c, p_1, seeding, rng=7, agents=(theta / v, willing, able))

    np.testing.assert_array_equal(r_attenuated.curve, r_rescaled.curve)
    np.testing.assert_array_equal(r_attenuated.adopted, r_rescaled.adopted)
    np.testing.assert_array_equal(r_attenuated.attribution_code, r_rescaled.attribution_code)


def test_per_agent_visibility_override():
    # Two identical stars: hub 0 with leaves 1,2; hub 3 with leaves 4,5.
    # Leaves 1 and 4 are seeded adopters; only leaf 1 is "loud" (v=1).
    edges = [(0, 1, 1.0), (0, 2, 1.0), (3, 4, 1.0), (3, 5, 1.0)]
    c = tiny_org(edges)
    vis = np.array([0.3, 1.0, 0.3, 0.3, 0.3, 0.3])
    res = run(c, [0.5, 0.0, 0.9, 0.5, 0.0, 0.9], SEED(1, 4), vis_array=vis)
    assert res.adopted[0]        # sees loud seed: share = 1.0/2 = 0.5 >= 0.5
    assert not res.adopted[3]    # sees quiet seed: share = 0.3/2 = 0.15 < 0.5


def test_visibility_validation():
    c = tiny_org([(0, 1, 1.0)])
    with pytest.raises(ValueError):
        run(c, [0.5, 0.5], SEED(1), **{"visibility": 1.5})
    with pytest.raises(ValueError):
        run(c, [0.5, 0.5], SEED(1), vis_array=np.array([0.5]))  # wrong shape
    with pytest.raises(ValueError):
        run(c, [0.5, 0.5], SEED(1), vis_array=np.array([0.5, 2.0]))  # out of range


def test_default_visibility_is_inert():
    """v = 1.0 must reproduce pre-D17 results bit-for-bit (ratified D16 re-check)."""
    org = generate_org(n_agents=400, seed=3)
    c = org.compile()
    s = make_seeding("cluster", c, 0.05, rng=3)
    r1 = run_simulation(c, SimParams(), s, rng=3)
    r2 = run_simulation(c, SimParams(visibility=1.0), s, rng=3,
                        visibility=np.ones(c.n))
    np.testing.assert_array_equal(r1.curve, r2.curve)
