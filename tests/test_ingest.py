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
