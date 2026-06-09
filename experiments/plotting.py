"""Matplotlib helpers for experiment notebooks.

Honesty requirement (spec §6): every figure produced through this module is
stamped "SYNTHETIC DATA" — use fig_with_stamp()/stamp() for all figures, no
exceptions. Matplotlib is a notebook/toolchain dependency; core/ never imports it.
"""

from __future__ import annotations

import pathlib
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

STRATEGY_COLORS = {
    "broadcast": "#d62728",
    "random": "#7f7f7f",
    "champions": "#9467bd",
    "cluster": "#1f77b4",
    "line_manager_first": "#2ca02c",
}
STRATEGY_LABELS = {
    "broadcast": "broadcast (0 seeds, comms blast)",
    "random": "random seeding",
    "champions": "champions (top degree)",
    "cluster": "cluster (whole teams)",
    "line_manager_first": "line managers first",
}

matplotlib.rcParams.update({
    "figure.dpi": 110,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "font.size": 10,
})


def stamp(fig: plt.Figure, note: str = "") -> None:
    """Mandatory synthetic-data stamp on every figure (spec §6)."""
    text = "SYNTHETIC DATA — generated organization, uncalibrated model"
    if note:
        text += f" · {note}"
    fig.text(0.5, 0.005, text, ha="center", va="bottom",
             fontsize=8, color="#888888", style="italic")


def fig_with_stamp(nrows=1, ncols=1, figsize=(9, 4.5), note: str = ""):
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, constrained_layout=True)
    # constrained_layout reserves no room for fig.text: pad the bottom slightly.
    fig.get_layout_engine().set(rect=(0, 0.03, 1, 0.97))
    stamp(fig, note)
    return fig, axes


def plot_curve_band(ax, mean, lo, hi, label, color):
    steps = np.arange(len(mean))
    ax.plot(steps, 100 * mean, color=color, label=label, linewidth=2)
    ax.fill_between(steps, 100 * lo, 100 * hi, color=color, alpha=0.15, linewidth=0)


def save_fig(fig: plt.Figure, path: str | pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    return path
