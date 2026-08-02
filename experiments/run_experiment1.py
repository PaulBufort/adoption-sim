"""CLI front end for experiment 1 (same code path as the notebook).

Usage:
    python experiments/run_experiment1.py            # full run (~10-60 s, multi-core)
    python experiments/run_experiment1.py --smoke    # CI-sized, ~1-5 s, 1 core

Writes versioned CSVs + JSON metadata into experiments/results/.
ALL DATA IS SYNTHETIC.
"""

from __future__ import annotations

import argparse
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="tiny CI-sized run")
    parser.add_argument("--n-jobs", type=int, default=None)
    args = parser.parse_args()

    import exp1  # local sibling import; exp1 fixes sys.path for core

    t0 = time.time()
    sc = exp1.headline_scenario()
    if args.smoke:
        sc = exp1.smoke_variant(sc)
        sc["meta"]["name"] = "smoke"
        n_jobs = 1
    else:
        n_jobs = args.n_jobs

    rows = exp1.run_strategy_comparison(sc, n_jobs)
    print(f"[exp1] strategy comparison (κ=20 main regime): {len(rows)} runs")
    for line in exp1.summary_table(rows):
        print("   ", line)

    kappa12 = exp1.run_kappa_companion(sc, n_jobs)
    print(f"[exp1] κ=12 lottery companion (D1): {len(kappa12)} runs")
    pinnov = exp1.run_pinnov_sweep(sc, n_jobs, replicates=2 if args.smoke else 12)
    print(f"[exp1] p_innov sweep (D2): {len(pinnov)} runs")
    tb = exp1.run_broadcast_duration_sweep(sc, n_jobs)
    print(f"[exp1] broadcast duration T_b sweep (D8): {len(tb)} runs")
    silo = exp1.run_silo_panel(sc, n_jobs, replicates=2 if args.smoke else 12)
    print(f"[exp1] silo panel: {len(silo)} runs")
    decay = exp1.run_decay_demo(sc, n_jobs, replicates=2 if args.smoke else 12)
    print(f"[exp1] decay demo: {len(decay)} runs")
    paired = exp1.run_paired_headline(sc, n_jobs, replicates=2 if args.smoke else None)
    print(f"[exp1] paired strategy contrasts (D19): {len(paired)} runs")
    paired_decay = exp1.run_paired_decay(sc, n_jobs, replicates=2 if args.smoke else None)
    print(f"[exp1] paired decay grid (D7×D19): {len(paired_decay)} runs")
    print(f"[exp1] done in {time.time() - t0:.0f}s — results in experiments/results/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
