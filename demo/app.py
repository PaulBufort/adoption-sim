"""adoption-sim — pedagogical Streamlit demo (spec §3).

Run locally:   streamlit run demo/app.py
Deployed on Streamlit Community Cloud from this repository (see demo/README.md).

EVERY NUMBER SHOWN IS SYNTHETIC: generated organizations, stipulated thresholds,
uncalibrated dynamics. The demo exists to build intuition about complex contagion,
not to predict anything. Full caveats: docs/limitations.md.

Stack note: charts use Altair, which ships as a hard dependency of Streamlit —
no extra requirement beyond the NetworkX + NumPy + Streamlit policy.
"""

from __future__ import annotations

import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import altair as alt  # bundled with streamlit
import pandas as pd   # bundled with streamlit
import streamlit as st

import core
from core import defaults
from core.dynamics import ATTRIBUTION_LABELS, SimParams, run_simulation
from core.metrics import dept_rates
from core.orggen import generate_org
from core.seeding import STRATEGIES, make_seeding

st.set_page_config(page_title="adoption-sim demo", page_icon="🧪", layout="wide")

MAX_STEPS = 60
N_DEPTS = 8


@st.cache_data(show_spinner=False, max_entries=64)
def simulate(n_agents: int, silo: float, theta_mean: float, strategy: str,
             budget: float, replicates: int, seed: int, relapse_on: bool,
             visibility: float = 1.0) -> dict:
    """Pure, cacheable simulation bundle (replicates × one strategy)."""
    curves, dept_mat, attribution = [], [], []
    for rep in range(replicates):
        s_org, s_seed, s_dyn = np.random.SeedSequence((seed, rep)).spawn(3)
        org = generate_org(
            n_agents=n_agents, n_departments=N_DEPTS, silo_strength=silo,
            seed=np.random.default_rng(s_org),
        )
        compiled = org.compile()
        seeding = make_seeding(strategy, compiled, budget, rng=np.random.default_rng(s_seed))
        params = SimParams(
            theta_mean=theta_mean,
            visibility=visibility,
            relapse_prob=0.25 if relapse_on else 0.0,
            retention_factor=1.0,
            max_steps=MAX_STEPS,
        )
        res = run_simulation(compiled, params, seeding, rng=np.random.default_rng(s_dyn))
        curves.append(res.curve)
        rates = dept_rates(res, compiled)
        dept_mat.append([rates[d] for d in sorted(rates)])
        attribution.append(res.attribution_counts())
    return {
        "curves": np.array(curves),
        "dept": np.array(dept_mat),
        "attribution": {k: float(np.mean([a[k] for a in attribution])) / n_agents
                        for k in ATTRIBUTION_LABELS.values()},
        "k_seeds": int(seeding.initial_adopters.size),
    }


def band_frame(curves: np.ndarray, label: str) -> pd.DataFrame:
    return pd.DataFrame({
        "step": np.arange(curves.shape[1]),
        "mean": 100 * curves.mean(axis=0),
        "lo": 100 * np.percentile(curves, 10, axis=0),
        "hi": 100 * np.percentile(curves, 90, axis=0),
        "strategy": label,
    })


# ---------------------------------------------------------------- sidebar ----
st.sidebar.title("🧪 adoption-sim")
st.sidebar.caption(f"v{core.__version__} · complex contagion on synthetic organizations")

strategy = st.sidebar.selectbox(
    "Seeding strategy", list(STRATEGIES), index=3,
    format_func=lambda s: s.replace("_", " "),
    help="; ".join(f"{k}: {v}" for k, v in STRATEGIES.items()),
)
n_agents = st.sidebar.slider("Organization size", 200, 3000, 1000, step=100,
                             help="Agents. 8 departments, teams of ~8 (generator D10).")
silo = st.sidebar.slider("Silo strength", 0.0, 1.0, 0.85, step=0.05,
                         help="1 − cross-department tie rate. 1.0 = near-hermetic departments.")
theta_mean = st.sidebar.slider("Mean adoption threshold θ̄", 0.05, 0.60, 0.30, step=0.01,
                               help="Share of credible contacts that must adopt first "
                                    "(Beta distributed, κ=20, plus 2.5% zero-θ innovators).")
budget = st.sidebar.slider("Seed budget (% of org)", 1, 15, 5,
                           help="Initial adopters granted to every seeded strategy. "
                                "Broadcast seeds nobody by definition (D8/D9).") / 100
with st.sidebar.expander("Advanced"):
    replicates = st.slider("Replicates", 1, 10, 5,
                           help="Fresh organization per replicate (D14). Bands = 10–90th pct.")
    seed = st.number_input("Master seed", 0, 99999, 42,
                           help="Same seed ⇒ identical results. Change it to re-roll.")
    relapse_on = st.toggle("Usage decay (relapse when share < θ)", value=False,
                           help="D7: adopters lacking reinforcement quit with prob 0.25/step.")
    visibility = st.slider("Visibility of adoption v", 0.2, 1.0, 1.0, step=0.05,
                           help="D17: how much of a colleague's adoption is visible. "
                                "Global v is exactly equivalent to raising every "
                                "threshold to θ/v — see experiment 3. Comms (broadcast) "
                                "stays fully visible.")
st.sidebar.divider()
st.sidebar.markdown(
    "**Honesty box** — every number here is synthetic and uncalibrated; "
    "curve *shapes and orderings* are the only meaningful output. "
    "[Model](https://github.com/) · [decisions](../docs/decisions.md) · "
    "[limitations](../docs/limitations.md) · AGPL-3.0"
)

# ---------------------------------------------------------------- header -----
st.title("When does a broadcast rollout fail where cluster seeding succeeds?")
st.warning(
    "**Synthetic data.** This demo simulates *generated* organizations with stipulated "
    "thresholds — a reasoning instrument, not a forecast of any real rollout. "
    "Time steps are abstract influence rounds, not days.",
    icon="⚠️",
)

try:
    with st.spinner(f"Simulating {replicates} × {strategy} …"):
        run = simulate(n_agents, silo, theta_mean, strategy, budget, replicates,
                       int(seed), relapse_on, visibility)
    ref = None
    if strategy != "broadcast":
        with st.spinner("Simulating broadcast reference …"):
            ref = simulate(n_agents, silo, theta_mean, "broadcast", budget, replicates,
                           int(seed), relapse_on, visibility)
except ValueError as exc:
    st.error(f"Cannot run this configuration: {exc}")
    st.stop()

final = float(run["curves"].mean(axis=0)[-1])
dead = int(np.sum(run["dept"].mean(axis=0) < defaults.ANALYSIS["dead_pocket_cutoff"]))
cols = st.columns(4)
cols[0].metric("Final adoption", f"{final:.0%}",
               help="Mean over replicates, % of organization, last step.")
if ref is not None:
    ref_final = float(ref["curves"].mean(axis=0)[-1])
    cols[1].metric("Broadcast reference", f"{ref_final:.0%}",
                   delta=f"{final - ref_final:+.0%} vs broadcast", delta_color="normal",
                   help="Reference floor: 0 seeds — broadcast buys awareness, not adopters (D8/D9).")
else:
    cols[1].metric("Broadcast reference", "—",
                   help="You are looking at broadcast itself: 0 seeds — it buys awareness, not adopters.")
cols[2].metric("Dead departments", f"{dead} / {N_DEPTS}",
               help=f"Departments below {defaults.ANALYSIS['dead_pocket_cutoff']:.0%} "
                    "final adoption (D11).")
cols[3].metric("Seeded adopters", f"{run['k_seeds']}",
               help="Agents set to adopted at t=0. Broadcast: 0 by definition.")

# ---------------------------------------------------------------- curves -----
frames = [band_frame(run["curves"], strategy.replace("_", " "))]
if ref is not None:
    frames.append(band_frame(ref["curves"], "broadcast (reference)"))
df = pd.concat(frames, ignore_index=True)
color = alt.Color("strategy:N", legend=alt.Legend(title=None, orient="top"),
                  scale=alt.Scale(range=["#1f77b4", "#d62728"]))
chart = (
    alt.Chart(df).mark_area(opacity=0.15).encode(
        x=alt.X("step:Q", title="simulation step (abstract influence rounds)"),
        y=alt.Y("lo:Q", title="adoption, % of organization", scale=alt.Scale(domain=[0, 100])),
        y2="hi:Q", color=color)
    + alt.Chart(df).mark_line(strokeWidth=2.5).encode(x="step:Q", y="mean:Q", color=color)
).properties(height=320)
st.altair_chart(chart, use_container_width=True)
vis_note = "" if visibility >= 1.0 else (
    f" · visibility v={visibility:.2f} (≡ thresholds θ/v — invisibility starves everyone, D17)")
st.caption(f"Synthetic data · {replicates} replicates, fresh organization each · "
           f"bands = 10–90th percentile · θ ~ Beta(μ={theta_mean}, κ=20) + 2.5% innovators · "
           f"willingness caps adoption at ~85% (D5) · broadcast = 0 seeds, buys awareness "
           f"not adopters (D9){vis_note}.")

# ------------------------------------------------------- unit map + R/W/A ----
left, right = st.columns([3, 2])
with left:
    st.subheader("Department map")
    dmean = run["dept"].mean(axis=0)
    ddf = pd.DataFrame({
        "department": [f"dept {d}" for d in range(len(dmean))],
        "adoption": dmean,
        "dead": dmean < defaults.ANALYSIS["dead_pocket_cutoff"],
    })
    bars = alt.Chart(ddf).mark_bar().encode(
        x=alt.X("department:N", sort=None, title=None),
        y=alt.Y("adoption:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%")),
        color=alt.condition("datum.dead", alt.value("#d62728"), alt.value("#2ca02c")),
        tooltip=[alt.Tooltip("adoption:Q", format=".0%"), "dead:N"],
    ).properties(height=260)
    rule = alt.Chart(pd.DataFrame({"y": [defaults.ANALYSIS["dead_pocket_cutoff"]]})
                     ).mark_rule(strokeDash=[4, 3], color="#888888").encode(y="y:Q")
    st.altair_chart(bars + rule, use_container_width=True)
    st.caption("Red = dead pocket: below 25% critical mass (D11). Synthetic data.")

with right:
    st.subheader("Why people didn't adopt")
    order = ["adopted", "not_ready", "not_willing", "not_able", "relapsed"]
    palette = {"adopted": "#2ca02c", "not_ready": "#d62728", "not_willing": "#ff7f0e",
               "not_able": "#7f7f7f", "relapsed": "#9467bd"}
    adf = pd.DataFrame({
        "outcome": [o.replace("_", " ") for o in order],
        "share": [run["attribution"][o] for o in order],
        "color": [palette[o] for o in order],
    })
    pie = alt.Chart(adf).mark_bar().encode(
        x=alt.X("share:Q", axis=alt.Axis(format="%"), title="share of organization"),
        y=alt.Y("outcome:N", sort=order, title=None),
        color=alt.Color("outcome:N", legend=None,
                        scale=alt.Scale(domain=[o.replace("_", " ") for o in order],
                                        range=[palette[o] for o in order])),
        tooltip=[alt.Tooltip("share:Q", format=".1%")],
    ).properties(height=260)
    st.altair_chart(pie, use_container_width=True)
    st.caption("Ready/willing/able gates (D4–D6): every non-adoption has exactly one cause.")

with st.expander("What am I looking at? (model in five sentences)"):
    st.markdown(
        "1. Agents adopt when the **credibility-weighted share** of their informal contacts "
        "who already adopted crosses their personal threshold θ — and they are willing "
        "(85% lottery) and able (100% here). \n"
        "2. **Broadcast** gives everyone one exposure from a low-credibility channel "
        "(weight 0.3 vs 1.0 for a close peer): it converts the ~2.5% zero-threshold "
        "innovators and stalls. \n"
        "3. **Cluster seeding** saturates whole teams, so neighbors see *several* adopters at "
        "once — local critical mass that can spread until silos cap it. \n"
        "4. **Scattered strategies** (random/champions) often win on raw reach here — every "
        "seed sits inside a dense team already; see the negative result in experiment 1. \n"
        "5. With **decay** on, the ordering changes: scattered gains evaporate, clustered "
        "gains hold (experiment 1, §6). \n\n"
        "Full math: `docs/model.md` · every modeling choice + alternatives: "
        "`docs/decisions.md` · what this cannot tell you: `docs/limitations.md`."
    )
