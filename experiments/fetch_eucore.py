"""Download the SNAP email-Eu-core graph + department labels into data/raw/.

Usage: python experiments/fetch_eucore.py

Two small files (~200 KB total) from https://snap.stanford.edu/data/email-Eu-core.html:
- email-Eu-core.txt.gz              directed email edges (u v per line)
- email-Eu-core-department-labels.txt.gz   ground-truth department per node (42 depts)

Design pre-declared in docs/decisions.md D22 BEFORE any run: the directed graph
is symmetrized by UNION (an undirected edge iff at least one email in either
direction — exactly what core/ingest.load_edgelist's nx.Graph construction does),
self-loops and isolates dropped, departments are the SNAP ground-truth labels
(never inferred communities), and ALL agent attributes remain synthetic
(docs/limitations.md #11). The result is reported whichever way it comes out.
"""

from __future__ import annotations

import pathlib
import sys
import urllib.request

RAW = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"
FILES = {
    "email-Eu-core.txt.gz":
        "https://snap.stanford.edu/data/email-Eu-core.txt.gz",
    "email-Eu-core-department-labels.txt.gz":
        "https://snap.stanford.edu/data/email-Eu-core-department-labels.txt.gz",
}


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        dest = RAW / name
        if dest.exists():
            print(f"already present: {dest}")
            continue
        print(f"downloading {url} ...")
        urllib.request.urlretrieve(url, dest)  # noqa: S310 — fixed https URL
        print(f"saved {dest} ({dest.stat().st_size/1e3:.0f} kB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
