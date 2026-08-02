"""Experiment 4 — email-Eu-core replication (decision D22, pre-declared).

Framing (non-negotiable, D22): a REPLICATION ON A REAL MODULAR TOPOLOGY WITH
SYNTHETIC BEHAVIORAL ATTRIBUTES — never an empirical validation of a real
diffusion. The topology is the SNAP email-Eu-core graph with its 42
ground-truth department labels (never inferred communities); every agent
attribute (thresholds, willingness, ability, credibility weights) is the
frozen headline synthetic recipe (docs/limitations.md #11).

Design (pre-declared in D22 BEFORE execution; seed layout frozen here):
- Directed email graph symmetrized by UNION (an undirected edge iff at least
  one email in either direction — core/ingest.load_edgelist's nx.Graph
  construction does exactly this); self-loops and isolates dropped.
- Fixed real topology; REPLICATES fresh attribute+seed draws. Within one
  draw, every strategy sees exactly the same topology and the same
  theta/willing/able draws (common random numbers, D19): one (s_attr, s_seed,
  s_dyn) triple per draw, reused verbatim by all strategies.
- Strategies: random, cluster, champions (D22: "champions if cheap" — it is).
  Primary contrast: random − cluster. champions is descriptive.
- Department 0 is an ordinary seedable unit on imported graphs (D22; tested).
- Master seed: SeedSequence([20260610, 4]) — the repo master extended with the
  experiment number, giving a spawn space disjoint from exp1/exp3 by
  construction. Deviation from D14 recorded in D22: the topology is fixed
  across replicates (intrinsic to a real-graph arm), so error bands mean
  "across attribute draws on THIS topology".
- Commitment (D22): the result is reported whichever way it comes out.

ALL AGENT DATA SYNTHETIC. Stack policy: networkx + numpy + stdlib only.
"""

from __future__ import annotations

import gzip
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from core.dynamics import draw_agents, run_simulation  # noqa: E402
from core.ingest import as_org, load_edgelist  # noqa: E402
from core.scenario import build_sim_params, load_scenario, save_results  # noqa: E402
from core.seeding import make_seeding  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
RAW = HERE.parent / "data" / "raw"
GRAPH_FILE = RAW / "email-Eu-core.txt.gz"
LABEL_FILE = RAW / "email-Eu-core-department-labels.txt.gz"

MASTER_ENTROPY = (20260610, 4)          # frozen pre-execution (D22)
STRATEGIES = ("random", "champions", "cluster")
REPLICATES = 50


def load_eucore():
    """Load the SNAP graph + ground-truth department labels as a CompiledOrg.

    Returns (compiled, provenance_dict). Raises FileNotFoundError with the
    fetch command if the raw files are absent."""
    if not GRAPH_FILE.exists() or not LABEL_FILE.exists():
        raise FileNotFoundError(
            "email-Eu-core raw files missing — run: python experiments/fetch_eucore.py"
        )
    g = load_edgelist(GRAPH_FILE)          # union symmetrization, self-loops dropped
    n_raw_nodes, n_raw_edges = g.number_of_nodes(), g.number_of_edges()
    labels: dict[str, str] = {}
    with gzip.open(LABEL_FILE, "rt") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            node, dept = line.split()[:2]
            labels[node] = dept
    missing = [n for n in g.nodes() if n not in labels]
    if missing:
        raise ValueError(f"{len(missing)} nodes lack a department label")
    for n in g.nodes():
        g.nodes[n]["snap_dept"] = labels[n]
    org = as_org(g, source="snap-email-Eu-core", team_attr="snap_dept")
    compiled = org.compile()
    dept_sizes = np.bincount(compiled.team)
    provenance = {
        "source": "https://snap.stanford.edu/data/email-Eu-core.html",
        "symmetrization": "union (undirected edge iff >=1 email either direction)",
        "n_nodes_after_symmetrization": n_raw_nodes,
        "n_edges_after_symmetrization": n_raw_edges,
        "n_nodes_compiled": int(compiled.n),
        "dropped_isolates": org.params["dropped_isolates"],
        "n_departments": int(compiled.n_teams),
        "dept_size_min_median_max": [int(dept_sizes.min()),
                                     float(np.median(dept_sizes)),
                                     int(dept_sizes.max())],
        "labels": "SNAP ground-truth departments (never inferred communities)",
    }
    return compiled, provenance


def run_realgraph_paired(compiled, sc: dict, strategies=STRATEGIES,
                         replicates: int = REPLICATES,
                         master_entropy=MASTER_ENTROPY) -> list[dict]:
    """The paired protocol on a fixed real topology (D22 x D19).

    One (s_attr, s_seed, s_dyn) triple per replicate, reused verbatim by every
    strategy: identical theta/willing/able draws; seed sets differ only through
    the strategy mechanism. Deterministic given master_entropy."""
    params = build_sim_params(sc)
    budget = sc["seeding"]["budget"]
    children = np.random.SeedSequence(list(master_entropy)).spawn(replicates)
    rows: list[dict] = []
    for rep in range(replicates):
        s_attr, s_seed, s_dyn = children[rep].spawn(3)
        agents = draw_agents(compiled, params, np.random.default_rng(s_attr))
        for strategy in strategies:
            seeding = make_seeding(strategy, compiled, budget,
                                   rng=np.random.default_rng(s_seed))
            result = run_simulation(compiled, params, seeding,
                                    rng=np.random.default_rng(s_dyn), agents=agents)
            counts = result.attribution_counts()
            cumulative = float(result.ever_adopted[compiled.active].mean())
            retention = (round(result.final_rate / cumulative, 6)
                         if cumulative > 0 else "")
            rows.append({
                "pair_id": str(rep),
                "rep": rep,
                "strategy": strategy,
                "final_rate": round(result.final_rate, 6),
                "peak_rate": round(result.peak_rate, 6),
                "cumulative_rate": round(cumulative, 6),
                "retention_rate": retention,
                "steps_to_fixed_point": result.steps_to_fixed_point,
                "converged": result.converged,
                **{f"n_{k}": v for k, v in counts.items()},
                "seeded_teams": json.dumps(
                    sorted({int(t) for t in compiled.team[seeding.initial_adopters]})),
                "team_rates": json.dumps(np.round(result.team_final, 4).tolist()),
            })
    return rows


def run_eucore(n_jobs: int | None = None) -> list[dict]:
    """Load the real graph, run the paired protocol, save the versioned CSV."""
    compiled, provenance = load_eucore()
    sc = load_scenario(HERE / "scenarios" / "headline.toml")
    sc["meta"]["name"] = "eucore"
    rows = run_realgraph_paired(compiled, sc)
    save_results(
        rows, RESULTS / "exp4_eucore.csv", sc,
        extra_meta={
            "design": "paired_within_replicate",
            "pair_axes": {"seeding.strategy": list(STRATEGIES)},
            "replicates_used": REPLICATES,
            "master_seed_entropy": list(MASTER_ENTROPY),
            "topology_is_real": True,
            "framing": ("replication on a real modular topology with synthetic "
                        "behavioral attributes — NOT an empirical validation of a "
                        "real diffusion (D22, limitations #11)"),
            "d14_deviation": ("topology fixed across replicates; bands mean "
                              "'across attribute draws on this topology'"),
            "graph": provenance,
        },
    )
    return rows


if __name__ == "__main__":
    out = run_eucore()
    finals: dict[str, list] = {}
    for r in out:
        finals.setdefault(r["strategy"], []).append(r["final_rate"])
    for s, v in finals.items():
        print(f"[exp4] {s:10} mean final reach {100 * float(np.mean(v)):5.1f}%  (n={len(v)})")
    print(f"[exp4] rows: {len(out)} -> experiments/results/exp4_eucore.csv")
