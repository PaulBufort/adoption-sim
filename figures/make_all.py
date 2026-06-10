"""Regenerate every final figure with one command, deterministically.

    python figures/make_all.py            # full regeneration (~3-5 min)
    python figures/make_all.py --list     # show the expected figure set and exit

The experiment notebooks are the single source of truth for figure code (no
duplicated plotting paths that could drift). This script executes them headlessly
in order — every figure is a pure function of the master seeds in the scenario
files — then verifies the expected files exist and prints their SHA-256 hashes.

Determinism contract: identical bytes on the same machine/library versions
(constraints.txt); across platforms the *numbers* (CSVs) are bit-stable while PNG
bytes may differ via font rendering (see .github/workflows/ci.yml).

ALL FIGURES DEPICT SYNTHETIC DATA (docs/limitations.md).
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
FIGDIR = REPO / "figures"

NOTEBOOKS = [
    "experiments/01_broadcast_vs_cluster.ipynb",
    "experiments/02_sanity_checks.ipynb",
    "experiments/03_observability.ipynb",
]

EXPECTED = [
    "headline.png",        # exp1: dual-regime headline (also embedded in README)
    "exp1_pinnov.png",     # exp1: innovator-share sweep (D2)
    "exp1_tb.png",         # exp1: broadcast duration sweep (D8)
    "exp1_silo.png",       # exp1: silo gradient
    "exp1_decay.png",      # exp1: decay reversal
    "exp2_tornado.png",    # exp2: sensitivity tornado
    "exp3_equivalence.png",  # exp3: theta/v equivalence witness (D17)
    "exp3_globalv.png",    # exp3: global visibility sweep
    "exp3_pilots.png",     # exp3: observable-pilots intervention
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list expected figures and exit")
    args = parser.parse_args()
    if args.list:
        for name in EXPECTED:
            print(FIGDIR / name)
        return 0

    t0 = time.time()
    for nb in NOTEBOOKS:
        print(f"[make_all] executing {nb} …", flush=True)
        t1 = time.time()
        subprocess.run(
            [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook",
             "--execute", "--inplace", nb],
            cwd=REPO, check=True,
        )
        print(f"[make_all]   done in {time.time() - t1:.0f}s")

    missing = [n for n in EXPECTED if not (FIGDIR / n).exists()]
    if missing:
        print(f"[make_all] FAILED — missing figures: {missing}")
        return 1
    print(f"[make_all] all {len(EXPECTED)} figures regenerated in {time.time() - t0:.0f}s:")
    for name in EXPECTED:
        digest = hashlib.sha256((FIGDIR / name).read_bytes()).hexdigest()[:16]
        print(f"  {name:<22} sha256:{digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
