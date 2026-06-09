"""Download the SNAP email-Enron graph into data/raw/ (demonstration use only).

Usage: python experiments/fetch_enron.py

~1.8 MB download from https://snap.stanford.edu/data/email-Enron.html.
The edges are a real intra-organizational e-mail topology; every agent attribute
the simulator puts on top of them is synthetic (docs/limitations.md #11).
Notebook 02 skips its real-topology section gracefully when this file is absent.
"""

from __future__ import annotations

import pathlib
import sys
import urllib.request

URL = "https://snap.stanford.edu/data/email-Enron.txt.gz"
DEST = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw" / "email-Enron.txt.gz"


def main() -> int:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        print(f"already present: {DEST}")
        return 0
    print(f"downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)  # noqa: S310 — fixed https URL
    print(f"saved {DEST} ({DEST.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
