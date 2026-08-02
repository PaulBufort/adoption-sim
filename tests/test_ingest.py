"""Real-graph import: edgelist/GraphML loading, schema mapping, honest guards."""

import gzip

import networkx as nx
import numpy as np
import pytest

from core.dynamics import SimParams, run_simulation
from core.ingest import as_org, load_edgelist, load_graphml
from core.seeding import make_seeding


def karate_edgelist(tmp_path, gz=False):
    g = nx.karate_club_graph()
    lines = "\n".join(f"{u} {v}" for u, v in g.edges()) + "\n# trailing comment\n"
    p = tmp_path / ("k.txt.gz" if gz else "k.txt")
    if gz:
        with gzip.open(p, "wt") as fh:
            fh.write(lines)
    else:
        p.write_text(lines)
    return p


def test_edgelist_roundtrip(tmp_path):
    g = load_edgelist(karate_edgelist(tmp_path))
    assert g.number_of_nodes() == 34
    assert g.number_of_edges() == 78


def test_gzipped_edgelist(tmp_path):
    g = load_edgelist(karate_edgelist(tmp_path, gz=True))
    assert g.number_of_nodes() == 34


def test_graphml_roundtrip(tmp_path):
    g = nx.karate_club_graph()
    p = tmp_path / "k.graphml"
    nx.write_graphml(g, p)
    assert load_graphml(p).number_of_edges() == 78


def test_as_org_schema_and_simulation(tmp_path):
    org = as_org(load_edgelist(karate_edgelist(tmp_path)), source="karate")
    assert org.params["kind"] == "real"
    assert org.params["n_communities"] >= 2
    assert org.params["note"].startswith("topology is real")
    c = org.compile()
    assert c.n == 34
    assert (c.role == 0).all()  # everyone an IC
    weights = {d["weight"] for _, _, d in org.informal.edges(data=True)}
    assert weights <= {0.6, 1.0}
    # The whole pipeline runs on a real topology.
    res = run_simulation(c, SimParams(theta_mean=0.2), make_seeding("cluster", c, 0.1, 1), rng=1)
    assert 0.0 <= res.final_rate <= 1.0


def test_isolates_dropped_and_counted(tmp_path):
    p = tmp_path / "iso.txt"
    p.write_text("a b\nb c\n")
    g = load_edgelist(p)
    g.add_node("hermit")
    org = as_org(g, source="iso")
    assert org.n == 3
    assert org.params["dropped_isolates"] == 1


def test_team_attr_used_when_present(tmp_path):
    g = nx.Graph([(0, 1), (1, 2), (2, 3)])
    for n in g.nodes():
        g.nodes[n]["club"] = "A" if n < 2 else "B"
    org = as_org(g, source="attr", team_attr="club")
    teams = nx.get_node_attributes(org.informal, "team")
    assert teams[0] == teams[1] != teams[2] == teams[3]


def test_manager_strategy_refuses_real_graphs(tmp_path):
    org = as_org(load_edgelist(karate_edgelist(tmp_path)), source="karate")
    with pytest.raises(ValueError, match="role data"):
        make_seeding("line_manager_first", org.compile(), 0.1, 1)


def test_directed_edgelist_symmetrizes_by_union(tmp_path):
    """D22: a directed email list collapses to undirected-by-union; self-loops
    dropped. '1 2' + '2 1' is ONE edge; '3 3' vanishes; '2 3' single-direction
    still becomes an edge."""
    p = tmp_path / "directed.txt"
    p.write_text("1 2\n2 1\n3 3\n2 3\n")
    g = load_edgelist(p)
    assert set(map(tuple, map(sorted, g.edges()))) == {("1", "2"), ("2", "3")}


def test_unit_zero_is_seedable_on_real_graphs(tmp_path):
    """D22: imported graphs have no leadership semantics — community 0 must be
    reachable by the team-based strategies (unlike synthetic orgs, where team 0
    is the excluded leadership team)."""
    g = nx.Graph()
    for i in range(6):          # community "A" -> team 0 after sorting (6 nodes)
        for j in range(i + 1, 6):
            g.add_edge(f"a{i}", f"a{j}")
    g.add_edge("b0", "b1")      # community "B" -> team 1 (2 nodes)
    g.add_edge("a0", "b0")
    for n in g.nodes():
        g.nodes[n]["dept"] = "A" if str(n).startswith("a") else "B"
    c = as_org(g, source="toy", team_attr="dept").compile()
    assert c.meta["kind"] == "real"
    # one_per_team must cover BOTH units, including unit 0.
    s = make_seeding("one_per_team", c, budget=2.5 / c.n, rng=3)
    assert set(c.team[s.initial_adopters]) == {0, 1}
    # cluster: k=4 > |team 1|, so unit 0 receives seeds whatever the shuffle.
    s2 = make_seeding("cluster", c, budget=0.5, rng=3)
    assert 0 in set(c.team[s2.initial_adopters])
