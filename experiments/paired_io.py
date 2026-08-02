"""Loaders for paired-run CSVs (D19): pairs are joined by pair_id, never by
row order. Shared by the CP1 analysis and the predictor validation harness.

Stack policy: numpy + stdlib only.
"""

from __future__ import annotations

import csv
import pathlib

import numpy as np


def read_rows(path: str | pathlib.Path) -> list[dict]:
    """CSV rows with numeric coercion for the columns analyses use."""
    numeric = {"final_rate", "peak_rate", "cumulative_rate", "plateau", "relapse"}
    rows = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            for k in numeric & row.keys():
                row[k] = float(row[k]) if row[k] != "" else float("nan")
            # retention_rate is legitimately blank (cumulative = 0, D19).
            if "retention_rate" in row:
                row["retention_rate"] = (float(row["retention_rate"])
                                         if row["retention_rate"] != "" else float("nan"))
            rows.append(row)
    return rows


def cell_finals(rows: list[dict], cell_keys: tuple[str, ...],
                value: str = "final_rate") -> dict:
    """Group {cell_tuple: {strategy: {pair_id: value}}}.

    cell_keys are the CSV label columns defining a cell (e.g.
    ("agents.theta_mean", "seeding.budget")); () yields the single-cell case.
    """
    out: dict = {}
    for r in rows:
        cell = tuple(r[k] for k in cell_keys)
        out.setdefault(cell, {}).setdefault(r["strategy"], {})[r["pair_id"]] = r[value]
    return out


def aligned_pair(cell: dict, s_x: str, s_y: str) -> tuple[np.ndarray, np.ndarray]:
    """Aligned (x, y) arrays for two strategies of one cell, joined on pair_id.

    Raises if the pair_id sets differ — a silent intersection could hide a
    broken pairing (the exact failure mode the pair_id audit found)."""
    px, py = cell[s_x], cell[s_y]
    if set(px) != set(py):
        raise ValueError(f"pair_id sets differ between {s_x} and {s_y}: "
                         f"{sorted(set(px) ^ set(py))[:5]}...")
    ids = sorted(px)
    return (np.array([px[i] for i in ids], dtype=np.float64),
            np.array([py[i] for i in ids], dtype=np.float64))
