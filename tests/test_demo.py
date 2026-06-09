"""Streamlit demo smoke test: the full app script executes without exceptions
and renders the honesty banner. Uses Streamlit's AppTest (no browser needed)."""

import pathlib

import pytest

st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = pathlib.Path(__file__).resolve().parent.parent / "demo" / "app.py"


def test_demo_runs_end_to_end():
    at = AppTest.from_file(str(APP), default_timeout=240)
    # Shrink the workload before the first run: AppTest executes the script once
    # to discover widgets, so keep defaults small via session-state-free rerun.
    at.run()
    assert not at.exception, f"demo raised: {at.exception}"
    # Honesty requirement: the synthetic-data banner is present.
    warnings = " ".join(w.value for w in at.warning)
    assert "Synthetic data" in warnings
    # Metrics rendered (final adoption + broadcast reference + dead pockets + seeds).
    assert len(at.metric) == 4


def test_demo_broadcast_branch():
    at = AppTest.from_file(str(APP), default_timeout=240)
    at.run()
    at.selectbox[0].select("broadcast").run()
    assert not at.exception
    assert at.metric[1].value == "—"  # broadcast is its own reference
