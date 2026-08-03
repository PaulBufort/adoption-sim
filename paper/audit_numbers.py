"""Audit: every statistic quoted in main.tex must match paper/numbers.json.

Each claim below is a substring REBUILT from numbers.json in the exact
formatting the manuscript uses. If a CSV (hence numbers.json) changes, the
rebuilt substring changes and the audit fails until the manuscript is updated
— the enforcement behind the paper's "machine-extracted and audited" sentence.

Usage: python paper/audit_numbers.py   (exit 0 = every claim found)
"""

from __future__ import annotations

import decimal
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
# Whitespace-normalized: the manuscript wraps lines freely.
TEX = " ".join((HERE / "main.tex").read_text().split())
N = json.loads((HERE / "numbers.json").read_text())


def r1(v: float) -> str:
    """Half-up rounding to 1 decimal — the manuscript's convention. Applied to
    the 4-decimal values in numbers.json, so no double rounding can occur
    (the audit exists because -5.045 once became -5.1 via -5.05)."""
    return str(decimal.Decimal(str(v)).quantize(decimal.Decimal("0.1"),
                                                rounding=decimal.ROUND_HALF_UP))


def claims() -> list[tuple[str, str]]:
    ph = N["paired_headline"]
    rc = ph["contrasts"]["random-cluster"]
    opt = ph["contrasts"]["one_per_team-random"]
    ch = ph["contrasts"]["champions-random"]
    reg = N["regime_map"]
    dec = N["decay"]["family"]
    sec = N["decay"]["secondary_at_r1_rho025"]
    cum25 = N["decay"]["cumulative_contrasts"]["r=1.0,rho=0.25"]
    cum40 = N["decay"]["cumulative_contrasts"]["r=1.0,rho=0.4"]
    edge = reg["largest_cluster_edge"]
    rob = N["robustness"]
    euc = N["eucore"]
    modes = euc["modes"]
    ind = N["independent_panel"]
    pred = N["predictor"]

    out = [
        ("headline contrast", f"+{r1(rc['delta_pp'])}"),
        ("headline CI", f"[{r1(rc['ci_pp'][0])}, {r1(rc['ci_pp'][1])}]"),
        ("random mean±sd", f"{ph['means']['random']['mean_pct']:.1f}\\pm{ph['means']['random']['sd_pct']:.1f}"),
        ("cluster mean±sd", f"{ph['means']['cluster']['mean_pct']:.1f}\\pm{ph['means']['cluster']['sd_pct']:.1f}"),
        ("champions delta", r1(ch["delta_pp"])),
        ("one_per_team delta", r1(opt["delta_pp"])),
        ("one_per_team CI", f"[{r1(opt['ci_pp'][0])}, +{r1(opt['ci_pp'][1])}]"),
        ("map cells won", f"wins {reg['counts']['win_x']} of {reg['n_cells']} cells"),
        ("map equivalences", f"in {reg['counts']['equivalent']}"),
        ("map uncertain", f"{reg['counts']['uncertain']} stay uncertain"),
        # CP3: abstract is arithmetically complete (14 + 23 + 3 = 40) and the
        # "no cluster win" sentence is guarded — if a win_y cell ever appears in
        # the data, the rebuilt needle becomes unfindable and the audit fails.
        ("abstract map counts",
         f"{reg['counts']['equivalent']} saturated or starved cells equivalent"),
        ("abstract map uncertain", f"{reg['counts']['uncertain']} uncertain"),
        ("no cluster win band",
         (f"no cluster win of ${{\\ge}}{reg['band_pp']:.0f}$\\,pp"
          if reg["counts"].get("win_y", 0) == 0
          else "INVALID — cluster wins exist; manuscript sentence must change")),
        ("largest cluster edge",
         f"largest cluster edge, ${r1(abs(edge['delta_pp']))}$\\,pp"),
        ("map win range", f"+{r1(reg['win_delta_min_pp'])}$ to $+{r1(reg['win_delta_max_pp'])}"),
        ("map headline cell CI", f"[{r1(reg['headline_cell']['ci_pp'][0])},"),
        ("meso random seeded", f"{ph['meso']['random']['seeded_teams_mean']:.0f}$ of {ph['n_line_teams']}"),
        ("meso random ignited", f"{ph['meso']['random']['ignited50_mean']:.0f}$ end at majority"),
        ("meso cluster", f"{ph['meso']['cluster']['seeded_teams_mean']:.0f}$ (${{\\sim}}{ph['meso']['cluster']['ignited50_mean']:.0f}$)"),
        ("broadcast", f"{ind['broadcast']['mean_pct']:.1f}\\pm{ind['broadcast']['sd_pct']:.1f}"),
        ("pinnov ablation n", f"all {ind['broadcast_at_pinnov0']['n']} runs"),
        ("decay r1 rho.10", f"+{r1(dec['r=1.0,rho=0.1']['delta_pp'])}$\\,pp $[{r1(dec['r=1.0,rho=0.1']['ci_pp'][0])}, {r1(dec['r=1.0,rho=0.1']['ci_pp'][1])}]"),
        ("decay r1 rho.25", f"{r1(dec['r=1.0,rho=0.25']['delta_pp'])}}}$\\,pp $[{r1(dec['r=1.0,rho=0.25']['ci_pp'][0])}, {r1(dec['r=1.0,rho=0.25']['ci_pp'][1])}]"),
        ("decay r1 rho.40", f"{r1(dec['r=1.0,rho=0.4']['delta_pp'])}$\\,pp $[{r1(dec['r=1.0,rho=0.4']['ci_pp'][0])}, {r1(dec['r=1.0,rho=0.4']['ci_pp'][1])}]"),
        ("decay r05 rho.10", f"+{r1(dec['r=0.5,rho=0.1']['delta_pp'])}$\\,pp $[{r1(dec['r=0.5,rho=0.1']['ci_pp'][0])}, {r1(dec['r=0.5,rho=0.1']['ci_pp'][1])}]"),
        ("decay r05 rho.25", f"{r1(dec['r=0.5,rho=0.25']['delta_pp'])}$\\,pp $[{r1(dec['r=0.5,rho=0.25']['ci_pp'][0])}, +{r1(dec['r=0.5,rho=0.25']['ci_pp'][1])}]"),
        ("decay r05 rho.40", f"{r1(dec['r=0.5,rho=0.4']['delta_pp'])}$\\,pp $[{r1(dec['r=0.5,rho=0.4']['ci_pp'][0])}, {r1(dec['r=0.5,rho=0.4']['ci_pp'][1])}]"),
        ("asym cluster", f"{r1(dec['r=0.5,rho=0.0']['cluster_pct'])}\\%$ at $\\rho{{=}}0$ to ${r1(dec['r=1.0,rho=0.4']['cluster_pct'])}\\%"),
        ("asym random collapse", f"{r1(dec['r=0.5,rho=0.0']['random_pct'])}\\%$ to ${r1(dec['r=1.0,rho=0.4']['random_pct'])}\\%"),
        ("cumulative random", r1(sec["random"]["cumulative_pct"])),
        ("retention pair", f"{sec['cluster']['retention_mean']:.2f}$ (cluster) vs.\\ ${sec['random']['retention_mean']:.2f}$ (random)"),
        # CP3: endpoint-dependence — cumulative-reach contrasts (descriptive).
        ("cumulative contrast rho.25",
         f"{r1(cum25['delta_pp'])}$\\,pp $[{r1(cum25['ci_pp'][0])}, +{r1(cum25['ci_pp'][1])}]"),
        ("cumulative contrast rho.40",
         f"{r1(cum40['delta_pp'])}$\\,pp $[{r1(cum40['ci_pp'][0])}, {r1(cum40['ci_pp'][1])}]"),
        ("robustness range", f"+{r1(rob['min_pp'])}$ to $+{r1(rob['max_pp'])}"),
        ("eucore contrast", f"+{r1(euc['contrast_random_cluster']['delta_pp'])}"),
        ("eucore CI", f"[{r1(euc['contrast_random_cluster']['ci_pp'][0])}, {r1(euc['contrast_random_cluster']['ci_pp'][1])}]"),
        ("eucore graph", f"{euc['graph']['n_nodes_compiled']} nodes, {euc['graph']['n_departments']} ground-truth"),
        # CP3 (D22(a)): the >=10% "ignition share" claim is retracted; the
        # manuscript now cites the bimodal shape (largest-gap split, descriptive).
        ("eucore mode medians",
         f"low (median ${modes['low_median_pct']:.0f}$\\%) or high "
         f"(median ${modes['high_median_pct']:.0f}$\\%)"),
        ("eucore mode gap",
         f"none between ${modes['gap_open_interval_pct'][0]}$\\% and "
         f"${modes['gap_open_interval_pct'][1]}$\\%"),
        ("predictor gate", f"AUC ${pred['v1_auc']:.2f}$, below even the "
                           f"${pred['gate_partial']:.2f}$ partial threshold"),
        ("scenario N", f"N{{=}}{N['scenario']['n_agents']}"),
        ("line teams", f"{ph['n_line_teams']} line teams"),
    ]
    return out


def main() -> int:
    failures = []
    for name, needle in claims():
        if needle not in TEX:
            failures.append((name, needle))
    if failures:
        print(f"AUDIT FAILED — {len(failures)} claim(s) not found in main.tex:")
        for name, needle in failures:
            print(f"  [{name}] expected substring: {needle!r}")
        return 1
    print(f"audit OK — {len(claims())} claims verified against numbers.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
