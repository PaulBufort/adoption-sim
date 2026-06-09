"""Org generator: structure, attributes, determinism, silo knob, compilation."""

import networkx as nx
import numpy as np
import pytest

from core import defaults
from core.orggen import LEADERSHIP_TEAM, generate_org


def small_org(**kw):
    args = dict(n_agents=400, n_departments=4, seed=42)
    args.update(kw)
    return generate_org(**args)


def test_node_count_and_attributes():
    org = small_org()
    assert org.n == 400
    assert org.formal.number_of_nodes() == 400
    for i in (0, 1, 399):
        attrs = org.informal.nodes[i]
        assert set(attrs) >= {"team", "dept", "role", "tenure"}
    roles = nx.get_node_attributes(org.informal, "role")
    n_lead = sum(1 for r in roles.values() if r == defaults.ROLE_LEADERSHIP)
    assert n_lead == 1 + 4  # CEO + one head per department


def test_every_line_team_has_exactly_one_manager():
    org = small_org()
    team = nx.get_node_attributes(org.informal, "team")
    role = nx.get_node_attributes(org.informal, "role")
    by_team = {}
    for node, t in team.items():
        by_team.setdefault(t, []).append(role[node])
    for t, rs in by_team.items():
        if t == LEADERSHIP_TEAM:
            continue
        assert rs.count(defaults.ROLE_MANAGER) == 1, f"team {t}"
        assert len(rs) >= 3


def test_formal_layer_is_a_tree_informal_is_denser():
    org = small_org()
    assert nx.is_tree(org.formal)
    assert org.informal.number_of_edges() > org.formal.number_of_edges()
    formal_edges = {frozenset(e) for e in org.formal.edges()}
    informal_edges = {frozenset(e) for e in org.informal.edges()}
    assert informal_edges != formal_edges


def test_determinism():
    a, b = small_org(), small_org()
    assert set(a.informal.edges()) == set(b.informal.edges())
    assert nx.get_node_attributes(a.informal, "tenure") == nx.get_node_attributes(
        b.informal, "tenure"
    )
    c = small_org(seed=43)
    assert set(c.informal.edges()) != set(a.informal.edges())


def cross_dept_edges(org):
    dept = nx.get_node_attributes(org.informal, "dept")
    return sum(1 for u, v in org.informal.edges() if dept[u] != dept[v] and dept[u] >= 0 and dept[v] >= 0)


def test_silo_strength_controls_cross_department_ties():
    counts = [cross_dept_edges(small_org(silo_strength=s)) for s in (0.0, 0.5, 1.0)]
    assert counts[0] > counts[1] > counts[2]
    # At s=1 only the constant noise leak (and no connector cross ties) remains.
    assert counts[2] < 0.05 * small_org().informal.number_of_edges()


def test_edge_weights_follow_relationship_types():
    org = small_org()
    w = defaults.WEIGHTS
    seen = set()
    dept_weights = set()
    for u, v, d in org.informal.edges(data=True):
        seen.add(d["kind"])
        if d["kind"] == "manager":
            assert d["weight"] == w["manager_report"]
        elif d["kind"] == "team":
            assert d["weight"] == w["peer_close"]
        elif d["kind"] == "dept":
            # Closeness-graded (D3 amendment): sister teams close, others far.
            assert d["weight"] in (w["peer_close"], w["peer_far"])
            dept_weights.add(d["weight"])
        else:
            assert d["weight"] == w["peer_far"]
    assert {"manager", "team", "dept"} <= seen
    assert dept_weights == {w["peer_close"], w["peer_far"]}


def test_sister_close_flag_off_gives_flat_dept_weights():
    org = small_org(sister_close=False)
    w = defaults.WEIGHTS
    for _, _, d in org.informal.edges(data=True):
        if d["kind"] == "dept":
            assert d["weight"] == w["peer_far"]


def test_compile_matches_networkx():
    org = small_org()
    c = org.compile()
    assert c.n == 400
    assert c.indptr[-1] == 2 * org.informal.number_of_edges()
    degs = dict(org.informal.degree())
    np.testing.assert_array_equal(c.degrees(), [degs[i] for i in range(c.n)])
    strength = dict(org.informal.degree(weight="weight"))
    np.testing.assert_allclose(c.total_weight, [strength[i] for i in range(c.n)])
    # CSR symmetry: every directed arc has its mirror with equal weight.
    for node in (0, 5, 200):
        for j in range(c.indptr[node], c.indptr[node + 1]):
            nb = c.indices[j]
            mirror = c.indices[c.indptr[nb]:c.indptr[nb + 1]]
            assert node in mirror


def test_without_node_knockout():
    c = small_org().compile()
    v = 10
    neighbors = c.indices[c.indptr[v]:c.indptr[v + 1]].copy()
    assert neighbors.size > 0
    k = c.without_node(v)
    assert not k.active[v]
    assert k.total_weight[v] == 0
    for nb in neighbors:
        assert k.total_weight[nb] < c.total_weight[nb]
    assert c.active.all()  # original untouched


def test_size_bounds_enforced():
    with pytest.raises(ValueError):
        generate_org(n_agents=50)
    with pytest.raises(ValueError):
        generate_org(n_agents=400, silo_strength=1.5)


def test_team_locality_concentrates_bridges():
    """D15: high locality -> within-dept ties land on ring-adjacent sister teams,
    yielding wide bridges (several ties between the same team pair)."""

    def bridge_widths(org):
        team = nx.get_node_attributes(org.informal, "team")
        pair_counts = {}
        for u, v, d in org.informal.edges(data=True):
            if d["kind"] == "dept":
                key = frozenset((team[u], team[v]))
                pair_counts[key] = pair_counts.get(key, 0) + 1
        return np.array(list(pair_counts.values()))

    wide = bridge_widths(small_org(n_agents=800, team_locality=0.9))
    narrow = bridge_widths(small_org(n_agents=800, team_locality=0.0))
    assert wide.mean() > 2 * narrow.mean()
    with pytest.raises(ValueError):
        small_org(team_locality=1.5)


def test_mean_team_size_roughly_respected():
    org = small_org(mean_team_size=10)
    team = nx.get_node_attributes(org.informal, "team")
    sizes = {}
    for node, t in team.items():
        if t != LEADERSHIP_TEAM:
            sizes[t] = sizes.get(t, 0) + 1
    mean = np.mean(list(sizes.values()))
    assert 8 <= mean <= 12
