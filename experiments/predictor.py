"""D21 level-1 ignition predictor: does a team light up on its own?

The mesoscopic diagnostic in the paper *measures* which teams ignited; this
module *predicts* it, from team-local quantities only, without running the
network simulation. Level 1 answers exactly one question:

    given s seeds inside a team of m members, with thresholds drawn as in D1-D2
    and the team's own wiring, does the team reach majority adoption on its own?

The prediction is the exact synchronous Granovetter cascade restricted to the
team, with the members' out-of-team credible mass kept in the denominator of
the exposure share but contributing no adopted mass (the "external-mass
dilution" of D21). It is therefore a statement about *local* ignition, and
deliberately ignores inter-team spillover — which the published diagnostic
shows is the dominant channel for dispersed seeding (random: 125 of 197
ignited teams were never seeded). Level 2 (spillover on the team-quotient
graph) is out of scope here; see D21.

Two modes:

- **measured** — build TeamSpec objects from a compiled organization and the
  actual theta/willing/able draws of a run, then predict each team's outcome.
  This is what validation gate V1 scores.
- **analytic** — sample synthetic teams from the generator's own recipe
  (manager-IC ties at ``manager_report``, IC-IC ties w.p. ``p_team`` at
  ``peer_close``, external mass calibrated with ``measure_external_mass``) and
  tabulate the ignition probability P_ig(s, m) by Monte Carlo, off-network.
  Folding P_ig through each strategy's seeds-per-team distribution gives the
  headline explanatory statement: how many near-certain local ignitions cluster
  seeding buys, versus how many low-probability tickets dispersed seeding buys.

The cascade mirrors ``core.dynamics.run_simulation`` exactly for an isolated
team with no broadcast and no relapse (pinned by a test that runs the engine
itself on a hand-built org). Validation gates V1/V2 and the go/partial/no-go
verdict are pre-declared in docs/decisions.md D21 and implemented verbatim in
``verdict`` — this module scores them, it does not choose them.

Stack policy: numpy + stdlib only. ALL DATA SYNTHETIC.
"""

from __future__ import annotations

import dataclasses
import math

import numpy as np

from core import defaults
from core.orggen import LEADERSHIP_TEAM

IGNITE_FRAC = 0.5          # "ignited" = majority adoption, as in the paper's diagnostic
READY_TOL = 1e-12          # same tolerance as core.dynamics (D4 boundary is inclusive)

__all__ = [
    "TeamSpec",
    "cascade",
    "predict_team",
    "team_specs_from_org",
    "measure_external_mass",
    "sample_team",
    "p_ignite",
    "hypergeom_pmf",
    "seeds_per_team_pmf",
    "predict_strategy",
    "roc_auc",
    "v1_local_ignition",
    "v2_sign_agreement",
    "verdict",
]


# --- Team representation and the exact local cascade ----------------------------

@dataclasses.dataclass(frozen=True)
class TeamSpec:
    """One team's local state: draws, internal wiring, and total credible mass.

    ``w_in`` is the symmetric (m, m) matrix of within-team credibility weights
    (zero diagonal). ``w_total`` is each member's FULL denominator from
    Eq. (1) — within-team plus out-of-team credible weight — so out-of-team
    contacts dilute the share exactly as they do in the engine.
    """

    theta: np.ndarray
    willing: np.ndarray
    able: np.ndarray
    w_in: np.ndarray
    w_total: np.ndarray

    def __post_init__(self) -> None:
        m = self.theta.size
        if self.w_in.shape != (m, m):
            raise ValueError(f"w_in must be ({m}, {m}), got {self.w_in.shape}")
        for name in ("willing", "able", "w_total"):
            if getattr(self, name).shape != (m,):
                raise ValueError(f"{name} must have shape ({m},)")
        if (self.w_total < self.w_in.sum(axis=1) - 1e-9).any():
            raise ValueError("w_total must include the within-team mass")

    @property
    def size(self) -> int:
        return int(self.theta.size)


def cascade(spec: TeamSpec, seeds, ext_mass=None, visibility: float = 1.0) -> np.ndarray:
    """Exact synchronous within-team cascade to its fixed point.

    ``seeds`` is a boolean mask or an index array; seeds adopt unconditionally
    (D9), willing/able gate everyone else. ``ext_mass`` optionally adds a frozen
    adopted mass from outside the team to each member's numerator (default 0 —
    the isolated-team question level 1 asks). Monotone, so it converges in at
    most m rounds.
    """
    m = spec.size
    adopted = np.zeros(m, dtype=bool)
    seeds = np.asarray(seeds)
    if seeds.dtype == bool:
        if seeds.shape != (m,):
            raise ValueError(f"seed mask must have shape ({m},)")
        adopted |= seeds
    else:
        adopted[seeds.astype(int)] = True
    ext = np.zeros(m) if ext_mass is None else np.asarray(ext_mass, dtype=np.float64)
    if ext.shape != (m,):
        raise ValueError(f"ext_mass must have shape ({m},)")
    gate = spec.willing & spec.able
    with np.errstate(invalid="ignore", divide="ignore"):
        for _ in range(m + 1):
            numer = spec.w_in @ (adopted * visibility) + ext
            share = np.where(spec.w_total > 0, numer / spec.w_total, 0.0)
            ready = (share > 0.0) & (share >= spec.theta - READY_TOL)
            new = ready & gate & ~adopted
            if not new.any():
                break
            adopted |= new
    return adopted


def predict_team(spec: TeamSpec, seeds, ext_mass=None, visibility: float = 1.0,
                 ignite_frac: float = IGNITE_FRAC) -> dict:
    """Cascade + the two summary quantities: adopted fraction and ignition."""
    adopted = cascade(spec, seeds, ext_mass=ext_mass, visibility=visibility)
    frac = float(adopted.mean())
    return {"adopted": adopted, "fraction": frac, "ignited": bool(frac >= ignite_frac)}


# --- Measured mode: read teams off a compiled organization -----------------------

def team_specs_from_org(compiled, theta, willing, able,
                        skip_leadership: bool = True) -> dict[int, TeamSpec]:
    """One TeamSpec per team, built from a CompiledOrg and one run's draws.

    Only *active* members are represented, matching the engine's team rates
    (which average over active members). Teams with no active member are
    omitted.
    """
    theta = np.asarray(theta, dtype=np.float64)
    willing = np.asarray(willing, dtype=bool)
    able = np.asarray(able, dtype=bool)
    indptr, indices, weights = compiled.indptr, compiled.indices, compiled.weights
    out: dict[int, TeamSpec] = {}
    for t in range(compiled.n_teams):
        if skip_leadership and t == LEADERSHIP_TEAM and compiled.meta.get("kind") != "real":
            continue
        members = np.flatnonzero((compiled.team == t) & compiled.active)
        if members.size == 0:
            continue
        pos = {int(g): i for i, g in enumerate(members)}
        w_in = np.zeros((members.size, members.size))
        for i, g in enumerate(members):
            lo, hi = indptr[g], indptr[g + 1]
            for nb, w in zip(indices[lo:hi], weights[lo:hi]):
                j = pos.get(int(nb))
                if j is not None:
                    w_in[i, j] = w
        out[t] = TeamSpec(
            theta=theta[members], willing=willing[members], able=able[members],
            w_in=w_in, w_total=compiled.total_weight[members],
        )
    return out


def measure_external_mass(compiled, skip_leadership: bool = True) -> dict:
    """Mean out-of-team credible mass per role — calibrates the analytic mode.

    Returns {"manager": float, "ic": float, "overall": float}. Keeping this
    measured rather than derived keeps the analytic teams honest about the
    generator's actual cross-team wiring (D10, D15).
    """
    indptr, indices, weights = compiled.indptr, compiled.indices, compiled.weights
    acc = {"manager": [], "ic": []}
    for g in range(compiled.n):
        t = int(compiled.team[g])
        if not compiled.active[g]:
            continue
        if skip_leadership and t == LEADERSHIP_TEAM and compiled.meta.get("kind") != "real":
            continue
        lo, hi = indptr[g], indptr[g + 1]
        same = compiled.team[indices[lo:hi]] == t
        ext = float(weights[lo:hi][~same].sum())
        key = "manager" if compiled.role[g] == defaults.ROLE_MANAGER else "ic"
        acc[key].append(ext)
    both = acc["manager"] + acc["ic"]
    return {
        "manager": float(np.mean(acc["manager"])) if acc["manager"] else 0.0,
        "ic": float(np.mean(acc["ic"])) if acc["ic"] else 0.0,
        "overall": float(np.mean(both)) if both else 0.0,
    }


# --- Analytic mode: sample teams from the generator's recipe ---------------------

def sample_team(m: int, rng: np.random.Generator, *,
                w_ext: float | tuple[float, float] = 0.0,
                theta_mean: float = defaults.AGENTS["theta_mean"],
                theta_concentration: float = defaults.AGENTS["theta_concentration"],
                p_innovator: float = defaults.AGENTS["p_innovator"],
                p_willing: float = defaults.AGENTS["p_willing"][0],
                p_team: float = defaults.ORG["p_team"],
                weights: dict | None = None,
                role_offsets=tuple(defaults.AGENTS["theta_role_offsets"])) -> TeamSpec:
    """Draw one synthetic team the way core.orggen wires a line team.

    Member 0 is the manager (edges to every IC at ``manager_report``); IC-IC
    ties appear with probability ``p_team`` at ``peer_close`` (D3, D10).
    ``w_ext`` is the out-of-team credible mass, scalar or (manager, ic).
    Draw order mirrors core.dynamics.draw_agents: theta, innovator atom, willing.
    """
    if m < 2:
        raise ValueError("a team needs at least 2 members")
    w = dict(defaults.WEIGHTS, **(weights or {}))
    roles = np.zeros(m, dtype=np.int8)
    roles[0] = defaults.ROLE_MANAGER
    offsets = np.asarray(role_offsets, dtype=np.float64)
    mu = np.clip(theta_mean + offsets[roles], 0.01, 0.99)
    theta = rng.beta(mu * theta_concentration, (1.0 - mu) * theta_concentration, size=m)
    theta[rng.random(m) < p_innovator] = 0.0
    willing = rng.random(m) < p_willing
    able = np.ones(m, dtype=bool)

    w_in = np.zeros((m, m))
    w_in[0, 1:] = w_in[1:, 0] = w["manager_report"]
    if m > 2:
        iu = np.triu_indices(m - 1, k=1)
        present = rng.random(iu[0].size) < p_team
        rows, cols = iu[0][present] + 1, iu[1][present] + 1
        w_in[rows, cols] = w_in[cols, rows] = w["peer_close"]

    ext_m, ext_ic = (w_ext, w_ext) if np.isscalar(w_ext) else w_ext
    ext = np.full(m, float(ext_ic))
    ext[0] = float(ext_m)
    return TeamSpec(theta=theta, willing=willing, able=able, w_in=w_in,
                    w_total=w_in.sum(axis=1) + ext)


def p_ignite(s: int, m: int, rng: np.random.Generator, n_draws: int = 4000,
             ignite_frac: float = IGNITE_FRAC, **team_kwargs) -> dict:
    """Monte-Carlo P(team of size m ignites | s seeds), plus the mean adopted
    fraction. Seeds are placed uniformly at random among members, matching how
    dispersed strategies land inside a team."""
    if not 0 <= s <= m:
        raise ValueError("need 0 <= s <= m")
    hits = 0
    frac_sum = 0.0
    for _ in range(n_draws):
        spec = sample_team(m, rng, **team_kwargs)
        seeds = rng.permutation(m)[:s]
        r = predict_team(spec, seeds, ignite_frac=ignite_frac)
        hits += r["ignited"]
        frac_sum += r["fraction"]
    return {"s": s, "m": m, "n_draws": n_draws,
            "p_ignite": hits / n_draws, "mean_fraction": frac_sum / n_draws}


# --- Folding through each strategy's seeds-per-team distribution -----------------

def hypergeom_pmf(s: int, n_pop: int, n_seeds: int, m: int) -> float:
    """P(exactly s of a team's m members are among n_seeds seeds drawn without
    replacement from n_pop agents). Log-space, so N=2000 poses no problem."""
    if s < 0 or s > min(m, n_seeds) or m > n_pop or n_seeds > n_pop:
        return 0.0
    lg = math.lgamma
    def logc(a, b):
        if b < 0 or b > a:
            return -math.inf
        return lg(a + 1) - lg(b + 1) - lg(a - b + 1)
    val = logc(n_seeds, s) + logc(n_pop - n_seeds, m - s) - logc(n_pop, m)
    return math.exp(val) if val > -700 else 0.0


def seeds_per_team_pmf(strategy: str, n_pop: int, n_seeds: int, m: int,
                       n_teams: int) -> np.ndarray:
    """Distribution of seeds landing in one team, per strategy (D20 semantics).

    - ``random``       : hypergeometric — every agent equally likely.
    - ``one_per_team`` : deterministic round-robin, so a team holds
      floor(k/T) or ceil(k/T) seeds.
    - ``cluster``      : whole teams filled one at a time — a team is either
      saturated (s = m), the single partial team, or untouched.

    Returns an array over s = 0..m summing to 1 (the marginal for a team picked
    uniformly at random).
    """
    pmf = np.zeros(m + 1)
    if strategy == "random":
        for s in range(m + 1):
            pmf[s] = hypergeom_pmf(s, n_pop, n_seeds, m)
    elif strategy == "one_per_team":
        base, extra = divmod(n_seeds, n_teams)
        if base > m:
            raise ValueError("budget exceeds team capacity in one_per_team")
        pmf[min(base, m)] += (n_teams - extra) / n_teams
        pmf[min(base + 1, m)] += extra / n_teams
    elif strategy == "cluster":
        n_full, partial = divmod(n_seeds, m)
        n_full = min(n_full, n_teams)
        pmf[m] += n_full / n_teams
        if partial and n_full < n_teams:
            pmf[partial] += 1 / n_teams
            pmf[0] += (n_teams - n_full - 1) / n_teams
        else:
            pmf[0] += (n_teams - n_full) / n_teams
    else:
        raise ValueError(f"no analytic seed distribution for {strategy!r} "
                         "(champions has no closed form — D21 excludes it)")
    total = pmf.sum()
    if not math.isclose(total, 1.0, abs_tol=1e-9):
        raise AssertionError(f"seed pmf must sum to 1, got {total}")
    return pmf


def predict_strategy(strategy: str, rng: np.random.Generator, *, n_pop: int,
                     n_seeds: int, m: int, n_teams: int, n_draws: int = 2000,
                     **team_kwargs) -> dict:
    """Level-1 prediction for one strategy: expected locally-ignited teams and
    the reach that local ignition alone accounts for.

    ``reach_local`` is a LOWER BOUND on final reach: it counts only adoption
    inside teams that ignite on their own, and ignores every inter-team
    spillover. Comparing it against observed reach quantifies how much of the
    cascade is NOT EXPLAINED BY THE LOCAL PREDICTOR (see the module docstring;
    the residual is not automatically "non-local" — attributing it to spillover
    vs model error is level-2 territory).
    """
    pmf = seeds_per_team_pmf(strategy, n_pop, n_seeds, m, n_teams)
    per_s = {}
    p_ig = 0.0
    frac = 0.0
    for s, prob in enumerate(pmf):
        if prob <= 0:
            continue
        stats = p_ignite(s, m, rng, n_draws=n_draws, **team_kwargs)
        per_s[s] = {**stats, "weight": float(prob)}
        p_ig += prob * stats["p_ignite"]
        frac += prob * stats["mean_fraction"]
    return {
        "strategy": strategy,
        "seeds_pmf": pmf,
        "per_s": per_s,
        "p_team_ignites": float(p_ig),
        "expected_ignited_teams": float(p_ig * n_teams),
        "reach_local": float(frac * n_teams * m / n_pop),
    }


# --- Validation gates V1 / V2 (pre-declared in D21) ------------------------------

def roc_auc(scores, labels) -> float:
    """Rank-based AUC (Mann-Whitney U), mid-ranks for ties. No sklearn.

    Returns NaN when one class is absent — an AUC is undefined there, and a
    silent 0.5 would look like a real (chance-level) measurement.
    """
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels).astype(bool)
    if scores.shape != labels.shape or scores.ndim != 1:
        raise ValueError("scores and labels must be 1-D of equal length")
    n_pos, n_neg = int(labels.sum()), int((~labels).sum())
    if n_pos == 0 or n_neg == 0:
        return math.nan
    order = np.argsort(scores, kind="stable")
    ranks = np.empty(scores.size, dtype=np.float64)
    sorted_scores = scores[order]
    i = 0
    while i < scores.size:                      # mid-ranks within tie groups
        j = i
        while j + 1 < scores.size and sorted_scores[j + 1] == sorted_scores[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return float((ranks[labels].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def v1_local_ignition(specs: dict[int, TeamSpec], seeds_by_team: dict[int, np.ndarray],
                      observed_rates: dict[int, float],
                      ignite_frac: float = IGNITE_FRAC) -> dict:
    """Gate V1: per-team ignition on SEEDED teams (D21 — level 1 claims local
    ignition, so unseeded teams, which can only ignite by spillover, are out of
    scope for this gate).

    Score = predicted adopted fraction (continuous); label = observed ignition.
    Returns AUC plus accuracy at the 0.5 cut and the confusion counts, so a
    high-AUC / badly-calibrated predictor cannot hide behind the AUC alone.
    """
    rows = []
    for t, spec in specs.items():
        seeds = seeds_by_team.get(t)
        if seeds is None or len(seeds) == 0 or t not in observed_rates:
            continue
        pred = predict_team(spec, seeds, ignite_frac=ignite_frac)
        rows.append((t, pred["fraction"], pred["ignited"],
                     observed_rates[t] >= ignite_frac))
    if not rows:
        raise ValueError("no seeded teams with observed rates to score")
    frac = np.array([r[1] for r in rows])
    pred_ig = np.array([r[2] for r in rows], dtype=bool)
    obs_ig = np.array([r[3] for r in rows], dtype=bool)
    return {
        "n_teams": len(rows),
        "auc": roc_auc(frac, obs_ig),
        "accuracy": float((pred_ig == obs_ig).mean()),
        "base_rate_observed": float(obs_ig.mean()),
        "base_rate_predicted": float(pred_ig.mean()),
        "tp": int((pred_ig & obs_ig).sum()), "fp": int((pred_ig & ~obs_ig).sum()),
        "tn": int((~pred_ig & ~obs_ig).sum()), "fn": int((~pred_ig & obs_ig).sum()),
        "per_team": rows,
    }


def v2_sign_agreement(predicted_delta: dict, observed_cells: dict) -> dict:
    """Gate V2: does the predictor reproduce the SIGN structure of the paired
    regime map on its decisive cells?

    ``predicted_delta``: {cell_key: predicted (random - cluster) reach}.
    ``observed_cells``:  {cell_key: dict from stats.classify_cells} — only
    cells classified "win_x"/"win_y" are scored (D21: decisive cells).
    An opposite-sign error is a decisive cell where the predictor takes the
    other side; ties (predicted exactly 0) count as disagreements, never as
    free passes.
    """
    scored, agree, opposite, missing = [], 0, 0, []
    for key, cell in observed_cells.items():
        if cell.get("cls") not in ("win_x", "win_y"):
            continue
        if key not in predicted_delta:
            missing.append(key)
            continue
        obs = 1 if cell["cls"] == "win_x" else -1
        pred = predicted_delta[key]
        pred_sign = 0 if pred == 0 else (1 if pred > 0 else -1)
        ok = pred_sign == obs
        agree += ok
        opposite += (pred_sign == -obs)
        scored.append({"cell": key, "observed_sign": obs, "predicted": float(pred),
                       "predicted_sign": pred_sign, "agrees": bool(ok)})
    n = len(scored)
    return {
        "n_decisive_cells": n,
        "n_missing_predictions": len(missing),
        "missing": missing,
        "agreement": (agree / n) if n else math.nan,
        "opposite_sign_errors": opposite,
        "per_cell": scored,
    }


# Pre-declared thresholds (docs/decisions.md D21) — recorded here as data so the
# gate cannot drift silently between the decision log and the code.
V1_AUC_GO = 0.80
V1_AUC_PARTIAL = 0.70
V2_AGREEMENT_GO = 0.90


def verdict(v1_auc: float, v2_agreement: float, v2_opposite_errors: int) -> dict:
    """Apply D21's pre-declared gates. Returns {"verdict", "reasons"}.

    - **go**      : AUC >= 0.80 AND sign agreement >= 0.90 AND zero opposite-sign errors.
    - **partial** : AUC >= 0.70 but the go conditions are not all met.
    - **no_go**   : AUC < 0.70 (or undefined).

    D21 defines the partial band by AUC alone; the case "V1 passes but V2
    fails" is read here as *partial* — local ignition is validated, the map's
    sign structure is not — which is the honest wording D21 attaches to
    partial ("consistent with", no AUC claim). Flagged for arbitration rather
    than silently resolved.
    """
    reasons = []
    auc_ok = not math.isnan(v1_auc) and v1_auc >= V1_AUC_GO
    auc_partial = not math.isnan(v1_auc) and v1_auc >= V1_AUC_PARTIAL
    agree_ok = not math.isnan(v2_agreement) and v2_agreement >= V2_AGREEMENT_GO
    clean = v2_opposite_errors == 0
    reasons.append(f"V1 AUC {v1_auc:.3f} {'>=' if auc_ok else '<'} {V1_AUC_GO}")
    reasons.append(f"V2 agreement {v2_agreement:.3f} "
                   f"{'>=' if agree_ok else '<'} {V2_AGREEMENT_GO}")
    reasons.append(f"V2 opposite-sign errors {v2_opposite_errors} "
                   f"({'clean' if clean else 'DISQUALIFYING for go'})")
    if auc_ok and agree_ok and clean:
        out = "go"
    elif auc_partial:
        out = "partial"
    else:
        out = "no_go"
    return {"verdict": out, "reasons": reasons}
