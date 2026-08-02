"""Test statistics for experiment analysis — numpy + stdlib only (stack policy).

Implements exactly what the paired protocol (D19) and the regime map (D18) need:
Student-t tail probabilities via the regularized incomplete beta function
(Lentz continued fraction), critical values by bisection, paired and Welch t
summaries, TOST equivalence tests against a practical-significance band, Holm
step-down correction, and the three-way cell classification
victory / equivalence / uncertainty used by the regime map.

Unit-pinned (tests/test_stats.py) against the hardcoded critical values already
used elsewhere in the repo: t(0.975, df=11) = 2.201 (notebook 01 Welch cell) and
t(0.975, df=49) = 2.0096.

Conventions:
- All p-values are two-sided unless the name says otherwise.
- ``paired_stats(x, y)`` analyzes d = x - y, so positive means "x above y".
- Degenerate inputs (zero variance) are handled explicitly and documented on
  each function rather than raising: paired CSV columns can legitimately be
  constant (e.g. broadcast at p_innovator = 0 is exactly 0.0 in every run).
"""

from __future__ import annotations

import math

import numpy as np

__all__ = [
    "t_sf",
    "t_crit",
    "paired_stats",
    "welch_stats",
    "tost_paired",
    "holm",
    "classify_cells",
]


# --- Student-t distribution (no scipy) -----------------------------------------

def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta (Lentz; Numerical Recipes 6.4)."""
    MAXIT, EPS, FPMIN = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            return h
    raise RuntimeError("incomplete-beta continued fraction did not converge")


def _betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_front = (
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log1p(-x)
    )
    front = math.exp(ln_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_sf(t: float, df: float) -> float:
    """Survival function P(T_df > t). Two-sided p-value = 2 * t_sf(|t|, df)."""
    if df <= 0:
        raise ValueError("df must be positive")
    if math.isnan(t):
        return math.nan
    if math.isinf(t):
        return 0.0 if t > 0 else 1.0
    # P(|T| > |t|) = I_{df/(df+t^2)}(df/2, 1/2)
    tail_both = _betainc(df / 2.0, 0.5, df / (df + t * t))
    return 0.5 * tail_both if t >= 0 else 1.0 - 0.5 * tail_both


def t_crit(df: float, q: float = 0.975) -> float:
    """Quantile t with P(T_df <= t) = q, by bisection on t_sf. q must be >= 0.5."""
    if not 0.5 <= q < 1.0:
        raise ValueError("q must be in [0.5, 1)")
    target = 1.0 - q
    lo, hi = 0.0, 1000.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_sf(mid, df) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# --- Summaries -----------------------------------------------------------------

def paired_stats(x, y, alpha: float = 0.05) -> dict:
    """Paired t summary of d = x - y (one entry per pair, e.g. per organization).

    Returns {n, mean_d, sd_d, se, t, df, p, ci: (lo, hi), dz}. Degenerate case
    sd_d = 0: t/dz are +-inf (or 0 when mean_d = 0), p is 0.0 (or 1.0), and the
    CI collapses to the point estimate.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("x and y must be 1-D arrays of equal length (pairs)")
    n = x.size
    if n < 2:
        raise ValueError("need at least 2 pairs")
    d = x - y
    mean_d = float(d.mean())
    sd_d = float(d.std(ddof=1))
    se = sd_d / math.sqrt(n)
    df = n - 1
    if se == 0.0:
        t = 0.0 if mean_d == 0.0 else math.copysign(math.inf, mean_d)
        p = 1.0 if mean_d == 0.0 else 0.0
        ci = (mean_d, mean_d)
        dz = t
    else:
        t = mean_d / se
        p = 2.0 * t_sf(abs(t), df)
        tc = t_crit(df, 1.0 - alpha / 2.0)
        ci = (mean_d - tc * se, mean_d + tc * se)
        dz = mean_d / sd_d
    return {"n": n, "mean_d": mean_d, "sd_d": sd_d, "se": se, "t": t,
            "df": df, "p": p, "ci": ci, "dz": dz}


def welch_stats(x, y, alpha: float = 0.05) -> dict:
    """Welch (unpooled, unpaired) t summary of mean(x) - mean(y).

    Returns {n_x, n_y, mean_x, mean_y, diff, se, t, df, p, ci}. Degenerate case
    se = 0 handled as in paired_stats.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.ndim != 1 or y.ndim != 1 or x.size < 2 or y.size < 2:
        raise ValueError("x and y must be 1-D with at least 2 values each")
    nx, ny = x.size, y.size
    vx, vy = float(x.var(ddof=1)), float(y.var(ddof=1))
    diff = float(x.mean() - y.mean())
    se2 = vx / nx + vy / ny
    se = math.sqrt(se2)
    if se == 0.0:
        t = 0.0 if diff == 0.0 else math.copysign(math.inf, diff)
        p = 1.0 if diff == 0.0 else 0.0
        return {"n_x": nx, "n_y": ny, "mean_x": float(x.mean()), "mean_y": float(y.mean()),
                "diff": diff, "se": 0.0, "t": t, "df": float(nx + ny - 2), "p": p,
                "ci": (diff, diff)}
    df = se2 * se2 / ((vx / nx) ** 2 / (nx - 1) + (vy / ny) ** 2 / (ny - 1))
    t = diff / se
    p = 2.0 * t_sf(abs(t), df)
    tc = t_crit(df, 1.0 - alpha / 2.0)
    return {"n_x": nx, "n_y": ny, "mean_x": float(x.mean()), "mean_y": float(y.mean()),
            "diff": diff, "se": se, "t": t, "df": df, "p": p,
            "ci": (diff - tc * se, diff + tc * se)}


def tost_paired(x, y, band: float, alpha: float = 0.05) -> dict:
    """Paired TOST equivalence test: H1 is -band < mean(x - y) < +band.

    p = max of the two one-sided p-values; equivalence is claimed when p < alpha
    (after any family correction applied by the caller). Degenerate case se = 0:
    p = 0.0 when |mean_d| < band, else 1.0.
    """
    if band <= 0:
        raise ValueError("band must be positive")
    ps = paired_stats(x, y, alpha=alpha)
    mean_d, se, df = ps["mean_d"], ps["se"], ps["df"]
    if se == 0.0:
        p = 0.0 if abs(mean_d) < band else 1.0
        return {**ps, "band": band, "p_lower": p, "p_upper": p, "p_tost": p}
    p_lower = t_sf((mean_d + band) / se, df)   # H0: mean_d <= -band
    p_upper = t_sf((band - mean_d) / se, df)   # H0: mean_d >= +band
    return {**ps, "band": band, "p_lower": p_lower, "p_upper": p_upper,
            "p_tost": max(p_lower, p_upper)}


# --- Multiple comparisons --------------------------------------------------------

def holm(pvals, alpha: float = 0.05) -> np.ndarray:
    """Holm step-down adjusted p-values (same order as input).

    Reject H0_i at family level alpha iff adjusted[i] < alpha. ``alpha`` is
    accepted for symmetry with callers but adjusted p-values do not depend on it.
    """
    p = np.asarray(pvals, dtype=np.float64)
    if p.ndim != 1 or p.size == 0:
        raise ValueError("pvals must be a non-empty 1-D sequence")
    if np.isnan(p).any() or (p < 0).any() or (p > 1).any():
        raise ValueError("pvals must be in [0, 1]")
    m = p.size
    order = np.argsort(p, kind="stable")
    adjusted = np.empty(m, dtype=np.float64)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adjusted[idx] = min(1.0, running)
    return adjusted


def classify_cells(pairs: list[tuple], band: float = 0.02, alpha: float = 0.05) -> list[dict]:
    """Three-way classification for a FAMILY of paired comparisons (regime map).

    ``pairs`` is a list of (x, y) tuples — one per cell, each analyzed as
    d = x - y. Two families are Holm-corrected SEPARATELY across all cells:
    the difference tests (paired t) and the equivalence tests (paired TOST
    against +-band). Per cell:

    - "win_x"      : Holm-corrected difference p < alpha AND mean_d >= +band
    - "win_y"      : Holm-corrected difference p < alpha AND mean_d <= -band
    - "equivalent" : Holm-corrected TOST p < alpha
    - "uncertain"  : none of the above

    Victory and equivalence are mutually exclusive by construction: a rejected
    TOST (even pre-correction) forces |mean_d| < band, while victory requires
    |mean_d| >= band.

    Returns one dict per cell with the paired_stats fields plus band, p_tost,
    p_diff_holm, p_tost_holm, cls.
    """
    cells = [tost_paired(x, y, band=band, alpha=alpha) for x, y in pairs]
    p_diff_holm = holm([c["p"] for c in cells], alpha=alpha)
    p_tost_holm = holm([c["p_tost"] for c in cells], alpha=alpha)
    out = []
    for c, pd, pt in zip(cells, p_diff_holm, p_tost_holm):
        if pd < alpha and abs(c["mean_d"]) >= band:
            cls = "win_x" if c["mean_d"] > 0 else "win_y"
        elif pt < alpha:
            cls = "equivalent"
        else:
            cls = "uncertain"
        out.append({**c, "p_diff_holm": float(pd), "p_tost_holm": float(pt), "cls": cls})
    return out
