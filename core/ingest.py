"""Import real public graphs (edgelist / GraphML) onto the simulator's schema.

Honesty contract (limitations.md #11): when a real graph is loaded, the *edges*
are real but every agent attribute — thresholds, willingness, ability, roles,
credibility weights — is still synthetic. Runs on imported graphs demonstrate the
dynamics on a real *topology*; they say nothing about the source organization.

Mapping rules (documented in docs/sanity-checks.md):
- node ids are relabeled to 0..n-1 (sorted original labels, deterministic);
- isolated nodes are dropped (an agent with zero contacts has no defined exposure
  share; under broadcast it would trivially adopt — a known pathology, see D8);
- "teams" are greedy-modularity communities unless a node attribute is supplied;
  departments equal teams (real graphs get one unit level only);
- everyone is an IC: role-based strategies (line_manager_first) raise, by design;
- edge credibility: same-community peer_close, cross-community peer_far,
  multiplied by any edge weights present (normalized to median 1).

Stack policy: networkx + numpy + stdlib only.
"""

from __future__ import annotations

import gzip
import pathlib

import networkx as nx
import numpy as np

from core import defaults
from core.orggen import OrgGraph


def load_edgelist(path: str | pathlib.Path, delimiter: str | None = None) -> nx.Graph:
    """Plain (possibly gzipped) edgelist: one 'u v [weight]' per line, # comments."""
    path = pathlib.Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    g = nx.Graph()
    with opener(path, "rt") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(("#", "%")):
                continue
            parts = line.split(delimiter)
            if len(parts) < 2:
                continue
            u, v = parts[0], parts[1]
            if u == v:
                continue
            w = float(parts[2]) if len(parts) > 2 else 1.0
            g.add_edge(u, v, raw_weight=w)
    return g


def load_graphml(path: str | pathlib.Path) -> nx.Graph:
    g = nx.Graph(nx.read_graphml(path))
    for _, _, d in g.edges(data=True):
        d.setdefault("raw_weight", float(d.get("weight", 1.0)))
    return g


def as_org(
    g: nx.Graph,
    source: str,
    team_attr: str | None = None,
    use_raw_weights: bool = False,
    seed: int = 0,
) -> OrgGraph:
    """Wrap a real graph as an OrgGraph ready for compile()/simulation."""
    g = g.copy()
    isolates = list(nx.isolates(g))
    g.remove_nodes_from(isolates)
    if g.number_of_nodes() == 0:
        raise ValueError("graph has no connected nodes")
    mapping = {old: i for i, old in enumerate(sorted(g.nodes(), key=str))}
    g = nx.relabel_nodes(g, mapping)

    if team_attr:
        raw = nx.get_node_attributes(g, team_attr)
        if len(raw) != g.number_of_nodes():
            raise ValueError(f"node attribute {team_attr!r} missing on some nodes")
        labels = {v: i for i, v in enumerate(sorted(set(raw.values()), key=str))}
        team = {n: labels[raw[n]] for n in g.nodes()}
    else:
        # Louvain above 5k nodes (greedy modularity is quadratic-ish and slow);
        # both are deterministic here (fixed seed).
        if g.number_of_nodes() > 5000:
            communities = nx.community.louvain_communities(g, weight=None, seed=seed)
        else:
            communities = nx.community.greedy_modularity_communities(g, weight=None)
        team = {}
        for tid, members in enumerate(communities):
            for n in members:
                team[n] = tid

    w = defaults.WEIGHTS
    raw_w = np.array([d.get("raw_weight", 1.0) for _, _, d in g.edges(data=True)])
    scale = float(np.median(raw_w)) if use_raw_weights and raw_w.size else 1.0
    for u, v, d in g.edges(data=True):
        base = w["peer_close"] if team[u] == team[v] else w["peer_far"]
        mult = (d.get("raw_weight", 1.0) / scale) if use_raw_weights else 1.0
        d["weight"] = base * min(mult, 3.0)  # cap: one loud channel is not 50 friends
        d["kind"] = "real"

    for n in g.nodes():
        g.nodes[n].update(
            team=int(team[n]), dept=int(team[n]), role=defaults.ROLE_IC, tenure=0.0
        )
    params = {
        "kind": "real",
        "source": source,
        "n_agents": g.number_of_nodes(),
        "n_communities": len(set(team.values())),
        "dropped_isolates": len(isolates),
        "note": "topology is real; ALL agent attributes are synthetic",
    }
    # The formal layer of a real import is unknown: reuse the informal topology
    # as a placeholder so OrgGraph stays well-formed (broadcast does not need it).
    return OrgGraph(formal=g, informal=g, params=params)
