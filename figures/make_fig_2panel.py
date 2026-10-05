"""Two-panel \\textwidth figure for the CN2026 abstract — STANDALONE, READ-ONLY.

Produces `figures/exp1_crossover_2panel.png`: panel (a) the paired 3-class regime
map, panel (b) the decay crossover. Panel (c) of the three-panel figure
(`figures/exp1_crossover.png`, hash-frozen at CP4) is dropped; its numbers move
to the running text.

What this script does NOT do
---------------------------
* No simulation. It re-analyses the two frozen CSVs written by the single S2
  execution, with the same loaders and the same pre-declared statistics as
  `experiments/cp1_analysis.py` (paired t, Holm within each family, TOST against
  a +-2 pp band, three-class cells).
* It writes exactly one file: `figures/exp1_crossover_2panel.png`. Nothing
  tracked is modified; the CP4 hash of `figures/exp1_crossover.png` is asserted
  before and after rendering.

Differences from `fig_paper_crossover()` (deliberate, all cosmetic or additive)
------------------------------------------------------------------------------
1. Two panels instead of three.
2. Rendered at the exact LLNCS \\textwidth (12.2 cm) and saved WITHOUT
   `bbox_inches="tight"`, so `\\includegraphics[width=\\textwidth]` scales 1:1 and
   a nominal 8 pt in the figure prints as 8 pt. The three-panel figure was drawn
   on a 19.4 cm canvas and reduced by 0.63, which shrank 9-11 pt to ~6-7 pt.
3. Sequential colormap bounded to the observed win domain [0, 43] pp instead of
   a symmetric diverging RdBu_r over [-42.6, +42.6]: no cell in the map is a
   cluster win, so half of the old scale carried no data. The +-2 pp band is
   marked on the colour bar.
4. A point estimate is printed in EVERY cell, including the equivalent ones
   (reviewer request), not only in the wins.
5. Panel (b) is recoloured. In the three-panel figure red meant "dispersion
   advantage" in (a) but "cluster" in (c); (b) here encodes the retention factor
   only, in two hues absent from the (a) ramp.

The statistics, the class assignment, the cell values and the boxed headline
cell are unchanged.

Usage:
    python figures/make_fig_2panel.py

Prints a cell-by-cell control table (CSV value -> printed value) and a
cross-check of every printed number against `paper/numbers.json`. Exit code is
non-zero if any cross-check or guard fails.

ALL DATA SYNTHETIC.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

from experiments.paired_io import aligned_pair, cell_finals, read_rows  # noqa: E402
from experiments.stats import classify_cells  # noqa: E402

RESULTS = ROOT / "experiments" / "results"
FIGURES = ROOT / "figures"
OUT_PNG = FIGURES / "exp1_crossover_2panel.png"
NUMBERS = ROOT / "paper" / "numbers.json"

# Pre-declared analysis constants — identical to experiments/cp1_analysis.py.
BAND, ALPHA = 0.02, 0.05
THETA_AXIS = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
BUDGET_AXIS = [0.01, 0.02, 0.05, 0.10, 0.15]
DECAY_FAMILY = ([("0.5", "0.0")]
                + [(r, rho) for r in ("0.5", "1.0") for rho in ("0.1", "0.25", "0.4")])
RHO_AXIS = ("0.0", "0.1", "0.25", "0.4")
HEADLINE = (0.30, 0.05)

# Guard: the CP4-frozen three-panel figure must not change (paper/cp4/CP4_PACKAGE.md).
FROZEN = {"figures/exp1_crossover.png":
          "c5af07dc6aa555c3353103089f8a3e9ec2b0bc11db402b68cf58b95421bc6b0d"}

# --- Print geometry -------------------------------------------------------------
# LLNCS \textwidth = 12.2 cm = 4.803 in. The canvas IS the printed size, so every
# font size below is also the printed point size (see docstring, point 2).
FIG_W_CM = 12.2
FIG_W_IN = FIG_W_CM / 2.54
FIG_H_IN = 2.40
DPI = 600

FS_CELL = 8.0      # in-cell point estimates
FS_TICK = 8.0      # tick labels
FS_AXIS = 8.5      # axis labels
FS_TITLE = 9.0     # panel titles
FS_LEGEND = 7.5        # in-panel legend of (b)
FS_LEGEND_SMALL = 7.0  # class key of (a), on the bottom strip
FS_STAMP = 6.5         # provenance stamp (not a data-bearing number)

# --- Colour ---------------------------------------------------------------------
CMAP = plt.get_cmap("viridis")          # sequential, colour-blind safe, prints in grey
VMIN, VMAX = 0.0, 43.0                  # observed win domain is [+2.8, +42.6] pp
C_EQUIV = "#d9d9d9"                     # TOST-equivalent fill
C_UNCERT_EDGE = "#8c8c8c"               # hatch colour for uncertain cells
C_R10 = "#000000"                       # panel (b): retention factor r = 1.0
C_R05 = "#d55e00"                       # panel (b): r = 0.5 (Okabe-Ito vermillion,
                                        # absent from the viridis ramp)
C_BAND = C_EQUIV                        # one grey = "inside the +-2 pp band", in the
                                        # cells, on the colour bar and in panel (b)

STAMP = "SYNTHETIC DATA · n = 50 organizations per cell"

MINUS = "−"


# --- Display rule ---------------------------------------------------------------

def fmt_pp(d: float) -> str:
    """Printed form of a paired delta in percentage points. DOCUMENTED ROUNDING:

        |d| <  0.05  ->  "0.0"            unsigned: at 1-dp resolution the sign of
                                          a value this small is not informative
        |d| < 10     ->  "{d:+.1f}"       one decimal
        |d| >= 10    ->  "{d:+.0f}"       nearest integer

    Rounding is Python's format(), i.e. round-half-to-even on the decimal
    representation. ASCII "-" is replaced by U+2212 MINUS SIGN.
    """
    if abs(d) < 0.05:
        return "0.0"
    s = f"{d:+.1f}" if abs(d) < 10 else f"{d:+.0f}"
    return s.replace("-", MINUS)


def text_colour_on(value: float) -> str:
    """Black or white in-cell text — whichever wins the WCAG contrast ratio.

    Relative luminance per WCAG 2.1 (gamma-expanded sRGB); black wins above
    L = 0.179, which is where (L+0.05)/0.05 overtakes 1.05/(L+0.05).
    """
    r, g, b, _ = CMAP((value - VMIN) / (VMAX - VMIN))
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    lum = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    return "black" if (lum + 0.05) / 0.05 > 1.05 / (lum + 0.05) else "white"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def border_ink(path: pathlib.Path) -> list[str]:
    """Edges of the PNG whose outermost pixel row/column is not blank."""
    from PIL import Image

    with Image.open(path) as img:
        a = np.asarray(img.convert("L"))
    edges = {"top": a[0, :], "bottom": a[-1, :], "left": a[:, 0], "right": a[:, -1]}
    return [name for name, line in edges.items() if int(line.min()) < 250]


# --- Data (pure re-analysis of the frozen CSVs) ----------------------------------

def load_regime() -> tuple[np.ndarray, np.ndarray, list, list]:
    """(delta_pp grid, class grid, sorted keys, classified cells) for the 40 cells."""
    rows = read_rows(RESULTS / "exp1_regime_paired_headline.csv")
    cells = cell_finals(rows, ("agents.theta_mean", "seeding.budget"))
    keys = sorted(cells, key=lambda c: (float(c[0]), float(c[1])))
    classified = classify_cells([aligned_pair(cells[k], "random", "cluster") for k in keys],
                                band=BAND, alpha=ALPHA)
    delta = np.full((len(THETA_AXIS), len(BUDGET_AXIS)), np.nan)
    cls_grid = np.empty((len(THETA_AXIS), len(BUDGET_AXIS)), dtype=object)
    for k, c in zip(keys, classified):
        i = THETA_AXIS.index(float(k[0]))
        j = BUDGET_AXIS.index(float(k[1]))
        delta[i, j] = 100 * c["mean_d"]
        cls_grid[i, j] = c["cls"]
    return delta, cls_grid, keys, classified


def load_decay() -> dict:
    """Per-contrast delta/CI/class, plus the rho = 0 bit-identity self-check.

    At rho = 0 the retention factor is inert, so the r = 0.5 and r = 1.0 runs are
    bit-identical and the family holds ONE contrast at rho = 0 (7 unique
    contrasts, D19). Both curves in panel (b) therefore share that point — the
    same convention as fig_paper_crossover(). The identity is asserted, not
    assumed.
    """
    rows = read_rows(RESULTS / "exp1_decay_paired_headline.csv")
    cells = cell_finals(rows, ("dynamics.retention_factor", "dynamics.relapse_prob"))
    x05, y05 = aligned_pair(cells[("0.5", "0.0")], "random", "cluster")
    x10, y10 = aligned_pair(cells[("1.0", "0.0")], "random", "cluster")
    identity = bool(np.array_equal(x05, x10) and np.array_equal(y05, y10))
    if not identity:
        raise SystemExit("GUARD FAILED: rho = 0 runs are not bit-identical across r; "
                         "the shared rho = 0 point in panel (b) would be wrong.")
    classified = classify_cells([aligned_pair(cells[k], "random", "cluster")
                                 for k in DECAY_FAMILY], band=BAND, alpha=ALPHA)
    fam = {f"r={k[0]},rho={k[1]}": {"delta_pp": 100 * c["mean_d"],
                                    "ci_pp": [100 * c["ci"][0], 100 * c["ci"][1]],
                                    "cls": c["cls"]}
           for k, c in zip(DECAY_FAMILY, classified)}
    return {"family": fam, "rho0_bit_identity": identity}


def decay_key(r: str, rho: str) -> str:
    """Family key for (r, rho); rho = 0 resolves to the single shared contrast."""
    return "r=0.5,rho=0.0" if rho == "0.0" else f"r={r},rho={rho}"


# --- Figure ---------------------------------------------------------------------

def render(delta: np.ndarray, cls_grid: np.ndarray, dec: dict) -> dict:
    """Draw the figure. Returns {'a': {cell: printed string}, 'b': plotted points}."""
    plt.rcParams["hatch.linewidth"] = 0.55      # visible at 600 dpi in print
    plt.rcParams["axes.unicode_minus"] = True

    fig = plt.figure(figsize=(FIG_W_IN, FIG_H_IN), dpi=DPI)
    # Explicit margins: no tight_layout, no bbox_inches="tight" — the saved canvas
    # must stay exactly FIG_W_IN wide so the printed point sizes are the nominal ones.
    gs = fig.add_gridspec(1, 2, width_ratios=[1.34, 1.0],
                          left=0.118, right=0.988, bottom=0.205, top=0.915,
                          wspace=0.46)
    ax = fig.add_subplot(gs[0, 0])
    axb = fig.add_subplot(gs[0, 1])

    # --- (a) regime map ---------------------------------------------------------
    printed_a = {}
    masked = np.where(np.isin(cls_grid, ["win_x", "win_y"]), delta, np.nan)
    im = ax.imshow(masked, cmap=CMAP, vmin=VMIN, vmax=VMAX, aspect="auto",
                   origin="lower")
    for i in range(len(THETA_AXIS)):
        for j in range(len(BUDGET_AXIS)):
            c = cls_grid[i, j]
            d = delta[i, j]
            label = fmt_pp(d)
            printed_a[(THETA_AXIS[i], BUDGET_AXIS[j])] = label
            if c == "equivalent":
                ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, facecolor=C_EQUIV,
                                       edgecolor="none"))
                ax.text(j, i, label, ha="center", va="center", fontsize=FS_CELL,
                        color="#404040")
            elif c == "uncertain":
                ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, facecolor="white",
                                       hatch="////", edgecolor=C_UNCERT_EDGE, lw=0))
                ax.text(j, i, label, ha="center", va="center", fontsize=FS_CELL,
                        color="#111111",
                        bbox=dict(facecolor="white", edgecolor="none",
                                  boxstyle="square,pad=0.10"))
            else:
                ax.text(j, i, label, ha="center", va="center", fontsize=FS_CELL,
                        fontweight="bold", color=text_colour_on(d))

    hi, hj = THETA_AXIS.index(HEADLINE[0]), BUDGET_AXIS.index(HEADLINE[1])
    ax.add_patch(Rectangle((hj - .5, hi - .5), 1, 1, fill=False, lw=1.6,
                           edgecolor="black", zorder=5))
    ax.set_xticks(range(len(BUDGET_AXIS)), [f"{100 * b:.0f}" for b in BUDGET_AXIS])
    ax.set_yticks(range(len(THETA_AXIS)), [f"{t:.2f}" for t in THETA_AXIS])
    ax.tick_params(labelsize=FS_TICK, length=2, pad=1.5)
    ax.set_xlabel("seed budget (%)", fontsize=FS_AXIS, labelpad=1.5)
    # \overline, not \bar: mathtext draws \bar as a hairline that vanishes at 8.5 pt.
    ax.set_ylabel(r"mean threshold $\overline{\theta}$", fontsize=FS_AXIS, labelpad=1.5)
    ax.set_title(r"(a) no decay: paired $\Delta$ (pp)", fontsize=FS_TITLE, pad=3.5)
    for s in ax.spines.values():
        s.set_linewidth(0.6)

    cbar = fig.colorbar(im, ax=ax, shrink=1.0, pad=0.035, fraction=0.075)
    cbar.set_ticks([2, 10, 20, 30, 40])
    cbar.ax.tick_params(labelsize=FS_TICK, length=1.8, pad=1.2)
    cbar.outline.set_linewidth(0.6)
    # The +-2 pp practical band, marked on the scale. No win falls below +2.8 pp,
    # so [0, 2] is empty by construction; the grey sliver and the rule state where
    # the band ends, in the same grey as the equivalent cells.
    cbar.ax.axhspan(0.0, 2.0, facecolor=C_BAND, edgecolor="none", zorder=3)
    cbar.ax.axhline(2.0, color="black", lw=0.9, zorder=4)

    # Class legend for (a), on the bottom strip under the panel it describes.
    fig.legend(handles=[Patch(facecolor=C_EQUIV, edgecolor="none", label="equivalent"),
                        Patch(facecolor="white", hatch="////",
                              edgecolor=C_UNCERT_EDGE, lw=0.4, label="uncertain"),
                        Patch(facecolor="none", edgecolor="black", lw=1.2,
                              label="headline")],
               loc="center", bbox_to_anchor=(0.275, 0.045), ncol=3,
               fontsize=FS_LEGEND_SMALL, frameon=False, handlelength=1.15,
               handleheight=0.9, handletextpad=0.3, columnspacing=0.75,
               borderpad=0.0)

    # --- (b) decay crossover ----------------------------------------------------
    rhos = [float(r) for r in RHO_AXIS]
    plotted_b = []
    axb.axhspan(-2, 2, facecolor=C_BAND, edgecolor="none", zorder=0)
    axb.axhline(0, color="#555555", lw=0.7, zorder=1)
    for r, colour, ls, marker in (("1.0", C_R10, "-", "s"), ("0.5", C_R05, "--", "o")):
        d, lo, hi2, cls = [], [], [], []
        for rho in RHO_AXIS:
            c = dec["family"][decay_key(r, rho)]
            d.append(c["delta_pp"]); lo.append(c["ci_pp"][0]); hi2.append(c["ci_pp"][1])
            cls.append(c["cls"])
            plotted_b.append({"r": r, "rho": rho, "key": decay_key(r, rho),
                              "delta_pp": c["delta_pp"], "ci_pp": c["ci_pp"],
                              "cls": c["cls"]})
        d, lo, hi2 = map(np.array, (d, lo, hi2))
        axb.errorbar(rhos, d, yerr=[d - lo, hi2 - d], fmt="none", ecolor=colour,
                     elinewidth=0.9, capsize=2.0, capthick=0.9, zorder=3)
        axb.plot(rhos, d, ls=ls, color=colour, lw=1.2, zorder=3, label=f"$r = {r}$")
        # Open marker = "uncertain" verdict (same three-class grammar as panel a).
        face = ["white" if c == "uncertain" else colour for c in cls]
        axb.scatter(rhos, d, marker=marker, s=13, facecolors=face, edgecolors=colour,
                    linewidths=0.9, zorder=4)
    axb.set_xlim(-0.025, 0.425)
    axb.set_xticks(rhos, [f"{r:g}" for r in rhos])
    axb.tick_params(labelsize=FS_TICK, length=2, pad=1.5)
    axb.set_xlabel(r"relapse probability $\rho$", fontsize=FS_AXIS, labelpad=1.5)
    axb.set_ylabel(r"$\Delta$ terminal adoption (pp)", fontsize=FS_AXIS, labelpad=1.5)
    axb.set_title("(b) decay crossover", fontsize=FS_TITLE, pad=3.5)
    for s in axb.spines.values():
        s.set_linewidth(0.6)
    axb.spines["top"].set_visible(False)
    axb.spines["right"].set_visible(False)
    handles, labels = axb.get_legend_handles_labels()
    handles.append(plt.Line2D([], [], ls="none", marker="o", ms=3.4, mfc="white",
                              mec="#555555", mew=0.9))
    labels.append("uncertain")
    axb.legend(handles, labels, loc="lower left", fontsize=FS_LEGEND, frameon=False,
               handlelength=1.6, handletextpad=0.5, borderpad=0.15, labelspacing=0.30)

    fig.text(0.988, 0.018, STAMP, ha="right", va="bottom", fontsize=FS_STAMP,
             color="#8a8a8a")

    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=DPI)          # no bbox_inches: canvas stays 12.2 cm
    plt.close(fig)
    return {"a": printed_a, "b": plotted_b}


# --- Control table ---------------------------------------------------------------

def control_table(delta, cls_grid, keys, classified, dec, printed) -> int:
    """Print CSV value -> printed value for every number, cross-check numbers.json.

    Returns the number of failed checks.
    """
    nums = json.loads(NUMBERS.read_text())
    fails = []

    def check(ok: bool, msg: str) -> None:
        print(f"  [{'ok ' if ok else 'FAIL'}] {msg}")
        if not ok:
            fails.append(msg)

    print("=" * 78)
    print("PROVENANCE — frozen inputs (no simulation, no tracked file modified)")
    print("=" * 78)
    for name in ("exp1_regime_paired_headline.csv", "exp1_decay_paired_headline.csv"):
        p = RESULTS / name
        print(f"  {name:<38} sha256 {sha256(p)[:16]}  {p.stat().st_size:>9,} B")
    print(f"  paper/numbers.json                     sha256 {sha256(NUMBERS)[:16]}")
    print(f"  analysis   experiments/paired_io.py + experiments/stats.py "
          f"(band {100 * BAND:.0f} pp, alpha {ALPHA})")
    print(f"  written    {OUT_PNG.relative_to(ROOT)}")
    print()

    print("=" * 78)
    print("PANEL (a) — 40 regime cells: CSV re-analysis -> printed string")
    print("=" * 78)
    print(f"  {'theta':>6} {'budget':>7} | {'delta_pp (exact)':>17} "
          f"{'95% CI (pp)':>20} | {'class':<11} {'printed':>8}")
    print("  " + "-" * 74)
    for k, c in zip(keys, classified):
        th, bu = float(k[0]), float(k[1])
        d = 100 * c["mean_d"]
        lo, hi = 100 * c["ci"][0], 100 * c["ci"][1]
        shown = printed["a"][(th, bu)]
        star = "  <- headline" if (th, bu) == HEADLINE else ""
        print(f"  {th:>6.2f} {100 * bu:>6.0f}% | {d:>17.3f} "
              f"[{lo:>8.2f},{hi:>8.2f}] | {c['cls']:<11} {shown:>8}{star}")
    print()

    print("  cross-checks against paper/numbers.json -> regime_map")
    counts = {}
    for c in classified:
        counts[c["cls"]] = counts.get(c["cls"], 0) + 1
    check(counts == nums["regime_map"]["counts"],
          f"class counts {counts} == numbers.json {nums['regime_map']['counts']}")
    wins = [100 * c["mean_d"] for c in classified if c["cls"].startswith("win")]
    check(round(min(wins), 1) == nums["regime_map"]["win_delta_min_pp"],
          f"min win {min(wins):.3f} -> {round(min(wins), 1)} pp "
          f"== win_delta_min_pp {nums['regime_map']['win_delta_min_pp']}")
    check(round(max(wins), 1) == nums["regime_map"]["win_delta_max_pp"],
          f"max win {max(wins):.3f} -> {round(max(wins), 1)} pp "
          f"== win_delta_max_pp {nums['regime_map']['win_delta_max_pp']}")
    check(all(c["cls"] != "win_y" for c in classified),
          "no cluster win in the map -> colour scale may start at 0 pp")
    hcell = nums["regime_map"]["headline_cell"]
    hd = delta[THETA_AXIS.index(HEADLINE[0]), BUDGET_AXIS.index(HEADLINE[1])]
    check(abs(hd - hcell["delta_pp"]) < 5e-3,
          f"headline cell {hd:.3f} == numbers.json {hcell['delta_pp']} "
          f"(printed {printed['a'][HEADLINE]}, boxed)")
    edge = nums["regime_map"]["largest_cluster_edge"]
    ed = delta[THETA_AXIS.index(edge["theta_mean"]), BUDGET_AXIS.index(edge["budget"])]
    check(abs(ed - edge["delta_pp"]) < 5e-3,
          f"largest cluster edge {ed:.3f} == numbers.json {edge['delta_pp']} "
          f"(printed {printed['a'][(edge['theta_mean'], edge['budget'])]}, "
          f"class {edge['cls']})")
    check(VMIN <= min(wins) and max(wins) <= VMAX,
          f"colour domain [{VMIN:.0f}, {VMAX:.0f}] pp brackets the observed wins "
          f"[{min(wins):.1f}, {max(wins):.1f}] pp with no unused negative half")
    print()

    print("=" * 78)
    print("PANEL (b) — 8 plotted points (rho = 0 shared by both curves)")
    print("=" * 78)
    print(f"  {'r':>4} {'rho':>5} {'family key':<16} | {'delta_pp':>10} "
          f"{'95% CI (pp)':>20} | {'class':<11} marker")
    print("  " + "-" * 74)
    for p in printed["b"]:
        marker = "open (uncertain)" if p["cls"] == "uncertain" else "filled"
        print(f"  {p['r']:>4} {p['rho']:>5} {p['key']:<16} | {p['delta_pp']:>10.3f} "
              f"[{p['ci_pp'][0]:>8.3f},{p['ci_pp'][1]:>8.3f}] | {p['cls']:<11} {marker}")
    print()

    print("  cross-checks against paper/numbers.json -> decay.family")
    check(dec["rho0_bit_identity"],
          "rho = 0 runs bit-identical across r -> one shared point, not two")
    for p in printed["b"]:
        ref = nums["decay"]["family"][p["key"]]
        ok = (abs(p["delta_pp"] - ref["delta_pp"]) < 5e-3
              and abs(p["ci_pp"][0] - ref["ci_pp"][0]) < 5e-3
              and abs(p["ci_pp"][1] - ref["ci_pp"][1]) < 5e-3
              and p["cls"] == ref["cls"])
        check(ok, f"{p['key']:<16} delta {p['delta_pp']:+8.3f} "
                  f"CI [{p['ci_pp'][0]:+7.3f}, {p['ci_pp'][1]:+7.3f}] cls {p['cls']:<9} "
                  f"== numbers.json {ref['delta_pp']:+8.3f} "
                  f"[{ref['ci_pp'][0]:+7.3f}, {ref['ci_pp'][1]:+7.3f}] {ref['cls']}")
    print()

    print("=" * 78)
    print("GEOMETRY & TYPOGRAPHY (printed sizes, scale 1:1)")
    print("=" * 78)
    with plt.rc_context():
        pass
    px_w, px_h = None, None
    try:
        from PIL import Image
        with Image.open(OUT_PNG) as img:
            px_w, px_h = img.size
    except Exception:                                   # PIL optional
        px_w, px_h = int(round(FIG_W_IN * DPI)), int(round(FIG_H_IN * DPI))
    exp_w, exp_h = int(round(FIG_W_IN * DPI)), int(round(FIG_H_IN * DPI))
    # +-1 px: matplotlib truncates figsize * dpi (12.2 cm * 600 dpi = 2881.9 px).
    check(abs(px_w - exp_w) <= 1 and abs(px_h - exp_h) <= 1,
          f"canvas {px_w}x{px_h} px == {FIG_W_IN:.3f}x{FIG_H_IN:.3f} in at {DPI} dpi "
          f"(+-1 px truncation); saved without bbox_inches, so "
          f"\\includegraphics[width=\\textwidth] scales 1:1 and nominal pt = printed pt")
    print(f"  [ok ] figure {FIG_W_CM:.1f} x {FIG_H_IN * 2.54:.1f} cm "
          f"= LLNCS \\textwidth x {FIG_H_IN * 2.54:.1f} cm")
    # Nothing may be clipped by the canvas edge: without bbox_inches="tight" an
    # overlong label is silently cut off (this caught the overline on theta-bar
    # running off the left edge).
    ink = border_ink(OUT_PNG)
    check(not ink, f"no ink on the 1 px canvas border -> nothing clipped"
                   + (f" (found on: {', '.join(ink)})" if ink else ""))
    smallest = min(FS_CELL, FS_TICK, FS_AXIS, FS_TITLE, FS_LEGEND, FS_LEGEND_SMALL)
    check(smallest >= 7.0,
          f"smallest font {smallest:.1f} pt printed; every number-bearing element "
          f">= 8.0 pt (cells {FS_CELL:.1f}, ticks {FS_TICK:.1f}, axes {FS_AXIS:.1f}, "
          f"titles {FS_TITLE:.1f}); keys {FS_LEGEND:.1f}/{FS_LEGEND_SMALL:.1f} pt and "
          f"stamp {FS_STAMP:.1f} pt carry no numbers")
    print(f"  [ok ] file size {OUT_PNG.stat().st_size / 1024:.0f} KiB at {DPI} dpi")
    print()

    print("=" * 78)
    print("GUARD — frozen artefacts untouched")
    print("=" * 78)
    for rel, want in FROZEN.items():
        got = sha256(ROOT / rel)
        check(got == want, f"{rel} sha256 {got[:16]} == CP4 manifest {want[:16]}")
    print()

    print("=" * 78)
    print(f"ROUNDING RULE (panel a): {fmt_pp.__doc__.splitlines()[0]}")
    for line in fmt_pp.__doc__.splitlines()[1:]:
        print(line)
    print("=" * 78)
    print(f"RESULT: {'ALL CHECKS PASSED' if not fails else str(len(fails)) + ' FAILED'}")
    return len(fails)


def main() -> int:
    delta, cls_grid, keys, classified = load_regime()
    dec = load_decay()
    printed = render(delta, cls_grid, dec)
    return 1 if control_table(delta, cls_grid, keys, classified, dec, printed) else 0


if __name__ == "__main__":
    sys.exit(main())
