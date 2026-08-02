"""experiments/stats.py: t distribution, paired/Welch/TOST summaries, Holm,
and the 3-way regime-map cell classification — pinned against known values."""

import math

import numpy as np
import pytest

from experiments.stats import (
    classify_cells,
    holm,
    paired_stats,
    t_crit,
    t_sf,
    tost_paired,
    welch_stats,
)


def test_t_sf_pins():
    # Pins against the critical values hardcoded elsewhere in the repo:
    # 2.201 (df=11, notebook 01 Welch cell) and 2.0096 (df=49, RESULTS_VERIFIED).
    assert 2 * t_sf(2.201, 11) == pytest.approx(0.050, abs=1e-3)
    assert 2 * t_sf(2.0096, 49) == pytest.approx(0.050, abs=1e-3)
    assert t_sf(0.0, 7) == pytest.approx(0.5, abs=1e-12)
    assert t_sf(-1.3, 9) + t_sf(1.3, 9) == pytest.approx(1.0, abs=1e-12)
    assert t_sf(13.5, 60) < 1e-12          # the decay drop's t-scale is "huge"
    assert t_sf(math.inf, 5) == 0.0
    # Large df converges to the normal tail.
    assert t_sf(1.959964, 1_000_000) == pytest.approx(0.025, abs=1e-4)
    with pytest.raises(ValueError):
        t_sf(1.0, 0)


def test_t_crit_pins():
    assert t_crit(11) == pytest.approx(2.201, abs=2e-3)
    assert t_crit(49) == pytest.approx(2.0096, abs=1e-3)
    assert t_crit(4) == pytest.approx(2.7764, abs=1e-3)
    with pytest.raises(ValueError):
        t_crit(10, q=0.4)


def test_paired_stats_hand_example():
    # d = [1, 1, 1, 1, 2]: mean 1.2, sd 0.44721, se 0.2, t = 6.0, df = 4.
    s = paired_stats([1, 2, 3, 4, 5], [0, 1, 2, 3, 3])
    assert s["n"] == 5 and s["df"] == 4
    assert s["mean_d"] == pytest.approx(1.2)
    assert s["sd_d"] == pytest.approx(0.4472136, abs=1e-6)
    assert s["t"] == pytest.approx(6.0, abs=1e-9)
    assert s["p"] == pytest.approx(0.003883, abs=2e-4)
    lo, hi = s["ci"]
    assert lo == pytest.approx(1.2 - 2.7764 * 0.2, abs=2e-3)
    assert hi == pytest.approx(1.2 + 2.7764 * 0.2, abs=2e-3)
    assert s["dz"] == pytest.approx(1.2 / 0.4472136, abs=1e-5)


def test_paired_stats_degenerate_and_validation():
    s = paired_stats([1.0, 1.0, 1.0], [1.0, 1.0, 1.0])
    assert s["t"] == 0.0 and s["p"] == 1.0 and s["ci"] == (0.0, 0.0)
    s2 = paired_stats([2.0, 2.0], [1.0, 1.0])
    assert s2["t"] == math.inf and s2["p"] == 0.0
    with pytest.raises(ValueError):
        paired_stats([1.0], [2.0])
    with pytest.raises(ValueError):
        paired_stats([1.0, 2.0], [1.0, 2.0, 3.0])


def test_welch_hand_example():
    # x: mean 2, var 1; y: mean 4, var 4 -> diff -2, se sqrt(5/3), Welch df 2.941.
    w = welch_stats([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
    assert w["diff"] == pytest.approx(-2.0)
    assert w["se"] == pytest.approx(math.sqrt(5 / 3), abs=1e-9)
    assert w["df"] == pytest.approx(2.9412, abs=1e-3)
    assert w["t"] == pytest.approx(-2.0 / math.sqrt(5 / 3), abs=1e-9)
    assert 0.17 < w["p"] < 0.27


def test_tost_paired():
    wiggle = np.tile([1.0, -1.0], 5)
    near = 0.001 * wiggle
    r = tost_paired(near, np.zeros(10), band=0.02)
    assert r["p_tost"] < 1e-6                     # clearly inside the band
    far = 0.05 + 0.001 * wiggle
    r2 = tost_paired(far, np.zeros(10), band=0.02)
    assert r2["p_tost"] > 0.5                     # clearly outside
    # Degenerate se = 0: decided by |mean_d| vs band.
    assert tost_paired([0.01] * 5, [0.0] * 5, band=0.02)["p_tost"] == 0.0
    assert tost_paired([0.05] * 5, [0.0] * 5, band=0.02)["p_tost"] == 1.0
    with pytest.raises(ValueError):
        tost_paired([1.0, 2.0], [1.0, 2.0], band=0.0)


def test_holm_textbook():
    adj = holm([0.01, 0.04, 0.03, 0.005])
    np.testing.assert_allclose(adj, [0.03, 0.06, 0.06, 0.02])
    assert [a < 0.05 for a in adj] == [True, False, False, True]
    # Step-down monotonicity (adjusted values never decrease along the sort).
    np.testing.assert_allclose(holm([0.01, 0.011, 0.012]), [0.03, 0.03, 0.03])
    with pytest.raises(ValueError):
        holm([])
    with pytest.raises(ValueError):
        holm([0.5, 1.5])


def test_classify_cells_three_way():
    wig50 = 0.001 * np.tile([1.0, -1.0], 25)
    wig10 = 0.05 * np.tile([1.0, -1.0], 5)
    z50, z10 = np.zeros(50), np.zeros(10)
    cells = [
        (0.10 + wig50, z50),   # x wins by 10 pp, tiny noise
        (-0.05 + wig50, z50),  # y wins by 5 pp
        (wig50, z50),          # provably inside the +-2 pp band
        (0.01 + wig10, z10),   # small n, wide CI: neither win nor equivalence
    ]
    res = classify_cells(cells, band=0.02, alpha=0.05)
    assert [c["cls"] for c in res] == ["win_x", "win_y", "equivalent", "uncertain"]
    # Corrected p-values are what the classes are built from.
    assert res[0]["p_diff_holm"] < 0.05 and abs(res[0]["mean_d"]) >= 0.02
    assert res[2]["p_tost_holm"] < 0.05 and abs(res[2]["mean_d"]) < 0.02
    assert res[3]["p_diff_holm"] >= 0.05 and res[3]["p_tost_holm"] >= 0.05
    # Victory and equivalence are mutually exclusive on every cell.
    for c in res:
        assert not (c["cls"].startswith("win") and c["p_tost_holm"] < 0.05
                    and abs(c["mean_d"]) < 0.02)
