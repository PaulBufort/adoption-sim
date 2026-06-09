"""Shared test fixtures: hand-built micro-organizations with exact, known structure."""

from __future__ import annotations

import networkx as nx
import numpy as np

from core.orggen import CompiledOrg, OrgGraph


def tiny_org(edges, n=None, team=None, dept=None, role=None) -> CompiledOrg:
    """Compile a small org from an explicit weighted edge list.

    edges: iterable of (u, v, weight). Attributes default to a single team in a
    single department, all ICs, tenure 5.0 — tests override what they need.
    """
    g = nx.Graph()
    nodes = sorted({u for u, v, _ in edges} | {v for _, v, _ in edges} | set(range(n or 0)))
    n = len(nodes)
    assert nodes == list(range(n)), "tiny_org expects contiguous integer node ids"
    team = team if team is not None else [0] * n
    dept = dept if dept is not None else [0] * n
    role = role if role is not None else [0] * n
    for i in nodes:
        g.add_node(i, team=int(team[i]), dept=int(dept[i]), role=int(role[i]), tenure=5.0)
    for u, v, w in edges:
        g.add_edge(u, v, weight=float(w))
    return OrgGraph(formal=g, informal=g, params={"kind": "test"}).compile()


def fixed_agents(n, theta, willing=None, able=None):
    """Exact agent draws for deterministic dynamics tests."""
    theta = np.full(n, theta, dtype=float) if np.isscalar(theta) else np.asarray(theta, dtype=float)
    willing = np.ones(n, dtype=bool) if willing is None else np.asarray(willing, dtype=bool)
    able = np.ones(n, dtype=bool) if able is None else np.asarray(able, dtype=bool)
    return theta, willing, able
