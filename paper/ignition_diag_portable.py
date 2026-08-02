#!/usr/bin/env python3
"""
Mesoscopic team-ignition diagnostic (PORTABLE) — adoption-sim.

WHAT IT DOES
  Re-runs the headline path (experiments/scenarios/headline.toml: 50 replicates,
  master_seed 20260610, decay off) for all five strategies, and for each computes,
  per replicate, over the ~249 "line" teams:
    - seeded teams      : distinct teams containing >= 1 seed
    - ignited (>=50%)   : teams reaching majority adoption at the end
    - unseeded ignited  : ignited teams that contained NO seed (inter-team spillover)
  Then prints the means and VALIDATES final_rate against paper/numbers.json
  (headline_k20). All data synthetic; numbers are machine-derived, not typed.

HOW TO RUN  (Python >= 3.11, repo venv active)
    python paper/ignition_diag.py
  Save this file as paper/ignition_diag.py so it finds the repo root automatically,
  OR set the env var ADOPTION_SIM_REPO to the repo path, e.g.
    ADOPTION_SIM_REPO="/path/to/adoption-sim" python ignition_diag_portable.py
"""
import os, sys, json, time, statistics as S
import numpy as np

# tomllib is stdlib on Python >= 3.11; fall back to tomli on 3.10 if needed
try:
    import tomllib  # noqa: F401
except ModuleNotFoundError:
    import tomli
    sys.modules["tomllib"] = tomli  # so `import tomllib` inside core.scenario works

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("ADOPTION_SIM_REPO") or os.path.dirname(HERE)  # parent of paper/
os.chdir(REPO)
sys.path.insert(0, REPO)

from core.scenario import load_scenario, build_sim_params, org_kwargs
from core.orggen import generate_org, LEADERSHIP_TEAM
from core.seeding import make_seeding
from core.dynamics import run_simulation
from core.sweep import expand_jobs

STRATS = ["broadcast", "random", "champions", "cluster", "line_manager_first"]
sc = load_scenario("experiments/scenarios/headline.toml")
jobs = expand_jobs(sc, axes={"seeding.strategy": STRATS})   # 50 reps from the scenario


def run_one(job):
    scj = job["scenario"]
    s_org, s_seed, s_dyn = job["seeds"]
    if scj["run"].get("share_graph"):
        s_org = np.random.SeedSequence((scj["run"]["master_seed"], job["condition_index"]))
    c = generate_org(**org_kwargs(scj), seed=np.random.default_rng(s_org)).compile()
    sd = make_seeding(scj["seeding"]["strategy"], c, scj["seeding"]["budget"],
                      rng=np.random.default_rng(s_seed))
    r = run_simulation(c, build_sim_params(scj), sd, rng=np.random.default_rng(s_dyn))
    line = np.arange(c.n_teams) != LEADERSHIP_TEAM
    tf = r.team_final
    seeded = np.zeros(c.n_teams, bool)
    if sd.initial_adopters.size:
        seeded[np.unique(c.team[sd.initial_adopters])] = True
    seeded[LEADERSHIP_TEAM] = False
    ig = (tf >= 0.5) & line
    return dict(strategy=scj["seeding"]["strategy"], final_rate=float(r.final_rate),
                seeded=int(seeded.sum()), ignited=int(ig.sum()),
                ig_unseeded=int((ig & ~seeded).sum()), n_line=int(line.sum()))


t0 = time.time()
rows = [run_one(j) for j in jobs]
secs = round(time.time() - t0, 1)
pub = json.load(open("paper/numbers.json"))["headline_k20"]

print(f"\nRan {len(jobs)} simulations in {secs}s  |  line teams = {rows[0]['n_line']}\n")
hdr = ("strategy", "final%", "pub%", "d_pp", "seededT", "ignited>=50%", "unseeded")
print("{:20}{:>8}{:>8}{:>7}{:>9}{:>13}{:>10}".format(*hdr))
for s in STRATS:
    rs = [r for r in rows if r["strategy"] == s]
    mean = lambda k: S.mean(r[k] for r in rs)
    fr = mean("final_rate") * 100.0
    d = fr - pub[s]["mean"] * 100.0
    print("{:20}{:8.1f}{:8.1f}{:+7.2f}{:9.1f}{:13.1f}{:10.1f}".format(
        s, fr, pub[s]["mean"] * 100.0, d, mean("seeded"), mean("ignited"), mean("ig_unseeded")))
print("\nIf d_pp is ~0 for every strategy, your run reproduces the published headline,")
print("and the seededT / ignited columns are the mesoscopic mechanism quoted in the abstract.")
