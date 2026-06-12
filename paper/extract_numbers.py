"""Extract every statistic cited in the paper from the versioned result CSVs.

    python paper/extract_numbers.py        # writes paper/numbers.json

The paper text must contain no number that is not derivable from this file
(anti-narrative-drift contract; REVIEW_B.md maps claims to these keys).
The outward-credibility measurement is recomputed here exactly as in
notebook 03 (same seeds), since it is computed inline there rather than
saved to CSV.
"""

from __future__ import annotations

import csv
import json
import pathlib
import sys
from collections import defaultdict

import numpy as np

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
RES = REPO / "experiments" / "results"


def finals(path, *keys):
    rows = list(csv.DictReader(open(RES / path)))
    acc = defaultdict(list)
    for r in rows:
        acc[tuple(r[k] for k in keys)].append(float(r["final_rate"]))
    return acc


def stats(vals):
    a = np.array(vals)
    return {
        "mean": round(float(a.mean()), 4),
        "sd": round(float(a.std()), 4),
        "min": round(float(a.min()), 4),
        "max": round(float(a.max()), 4),
        "n": len(vals),
    }


out = {"_provenance": "derived from experiments/results/*.csv (50-replicate headline, "
                      "12-replicate sweeps unless stated); regenerate via figures/make_all.py"}

# Headline, both regimes (50 replicates each)
for name, path in (("headline_k20", "exp1_strategies_headline.csv"),
                   ("headline_k12", "exp1_kappa12_headline.csv")):
    acc = finals(path, "strategy")
    out[name] = {k[0]: stats(v) for k, v in acc.items()}
out["nonoverlap_k20"] = {
    "broadcast_max": out["headline_k20"]["broadcast"]["max"],
    "cluster_min": out["headline_k20"]["cluster"]["min"],
    "holds": out["headline_k20"]["broadcast"]["max"] < out["headline_k20"]["cluster"]["min"],
}

# Innovator sweep (12 replicates; p=0 is the no-innovators variant)
acc = finals("exp1_pinnov_headline.csv", "seeding.strategy", "agents.p_innovator")
out["pinnov"] = {f"{s}@p={float(p):g}": stats(v) for (s, p), v in acc.items()}

# Broadcast duration sweep (50 replicates)
acc = finals("exp1_tb_headline.csv", "dynamics.broadcast_steps")
out["tb"] = {f"Tb={t[0]}": stats(v) for t, v in sorted(acc.items(), key=lambda kv: int(kv[0][0]))}

# Decay demo (12 replicates) — compare against the 50-rep no-decay headline
acc = finals("exp1_decay_headline.csv", "strategy")
out["decay"] = {k[0]: stats(v) for k, v in acc.items()}
out["decay_drop_pct"] = {
    s: round(100 * (out["decay"][s]["mean"] / out["headline_k20"][s]["mean"] - 1), 1)
    for s in ("random", "champions", "cluster")
}

# Observability (12 replicates)
acc = finals("exp3_globalv.csv", "seeding.strategy", "agents.visibility")
out["globalv"] = {f"{s}@v={float(v):g}": stats(x) for (s, v), x in acc.items()}
acc = finals("exp3_pilots.csv", "seeding.strategy", "agents.visibility")
out["pilots"] = {f"{s}@v={float(v):g}": stats(x) for (s, v), x in acc.items()}
out["pilot_gain_pp_at_v0.8"] = {
    s: round(100 * (out["pilots"][f"{s}@v=0.8"]["mean"] - out["globalv"][f"{s}@v=0.8"]["mean"]), 1)
    for s in ("cluster", "random", "champions")
}

# Outward credibility per seed — recomputed exactly as notebook 03 (seeds 900-904)
from core.orggen import generate_org  # noqa: E402
from core.scenario import load_scenario, org_kwargs  # noqa: E402
from core.seeding import make_seeding  # noqa: E402

sc = load_scenario(REPO / "experiments" / "scenarios" / "headline.toml")
outward = {}
for strat in ("cluster", "random", "champions"):
    vals = []
    for rep in range(5):
        org = generate_org(**org_kwargs(sc), seed=900 + rep)
        c = org.compile()
        s = make_seeding(strat, c, 0.05, rng=900 + rep)
        seeds = set(s.initial_adopters.tolist())
        w_out = sum(
            c.weights[j]
            for v in s.initial_adopters
            for j in range(c.indptr[v], c.indptr[v + 1])
            if int(c.indices[j]) not in seeds
        )
        vals.append(w_out / len(seeds))
    outward[strat] = {"mean": round(float(np.mean(vals)), 2), "sd": round(float(np.std(vals)), 2)}
out["outward_credibility_per_seed"] = outward

# Scenario constants the paper states
out["scenario"] = {k: sc[sect][k] for sect, ks in
                   (("org", ("n_agents", "n_departments", "silo_strength", "team_locality", "dept_degree")),
                    ("agents", ("theta_mean", "theta_concentration", "p_innovator")),
                    ("seeding", ("budget",)), ("run", ("replicates", "master_seed")))
                   for k in ks}

path = REPO / "paper" / "numbers.json"
path.write_text(json.dumps(out, indent=2))
print(f"wrote {path}")
for k in ("headline_k20", "pinnov", "decay_drop_pct", "pilot_gain_pp_at_v0.8"):
    print(k, "->", json.dumps(out[k])[:160], "…")
