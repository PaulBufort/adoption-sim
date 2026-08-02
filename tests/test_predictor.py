"""D21 level-1 ignition predictor: cascade fidelity, dilution, folding, gates.

The load-bearing test is test_cascade_matches_the_engine: the predictor's
cascade must reproduce core.dynamics.run_simulation exactly on an isolated
team, or nothing downstream means anything."""

import math

import numpy as np
import pytest

from core.dynamics import SimParams, run_simulation
from core.seeding import Seeding
from experiments.predictor import (
    TeamSpec,
    cascade,
    hypergeom_pmf,
    measure_external_mass,
    p_ignite,
    predict_strategy,
    predict_team,
    roc_auc,
    sample_team,
    seeds_per_team_pmf,
    team_specs_from_org,
    v1_local_ignition,
    v2_sign_agreement,
    verdict,
)
from tests.helpers import fixed_agents, tiny_org


def clique_spec(m, theta, w=1.0, w_ext=0.0, willing=None, able=None):
    """m-member team, all-to-all at weight w, plus a fixed external mass."""
    w_in = np.full((m, m), float(w))
    np.fill_diagonal(w_in, 0.0)
    theta = np.full(m, theta, dtype=float) if np.isscalar(theta) else np.asarray(theta, float)
    return TeamSpec(
        theta=theta,
        willing=np.ones(m, bool) if willing is None else np.asarray(willing, bool),
        able=np.ones(m, bool) if able is None else np.asarray(able, bool),
        w_in=w_in,
        w_total=w_in.sum(axis=1) + w_ext,
    )


# --- Cascade mechanics ----------------------------------------------------------

def test_one_seed_ignites_a_small_isolated_team():
    # 4 members, all-to-all weight 1 -> each has w_total 3; one seed gives the
    # others share 1/3 > 0.3, so the whole team cascades.
    spec = clique_spec(4, theta=0.3)
    r = predict_team(spec, [0])
    assert r["adopted"].all() and r["fraction"] == 1.0 and r["ignited"]


def test_external_dilution_stalls_the_same_team():
    # Same team, same seed, but 7.0 of out-of-team credible mass: share drops to
    # 1/10 < 0.3 and nothing spreads. This is D21's external-mass dilution.
    spec = clique_spec(4, theta=0.3, w_ext=7.0)
    r = predict_team(spec, [0])
    assert r["fraction"] == 0.25 and not r["ignited"]
    assert r["adopted"].sum() == 1  # the seed only


def test_partial_cascade_stops_at_the_threshold_boundary():
    # 5-clique, w_total = 4 each. Seed 0 -> the two theta=0.2 members see 1/4 and
    # join; the two theta=0.9 members then see 3/4 < 0.9 and stay out forever.
    # Majority reached without unanimity — the case an "ignited" flag must keep.
    spec = clique_spec(5, theta=[0.2, 0.2, 0.2, 0.9, 0.9])
    r = predict_team(spec, [0])
    assert r["fraction"] == 0.6 and r["ignited"]
    assert not r["adopted"][3] and not r["adopted"][4]


def test_seeds_adopt_unconditionally_but_gates_bind_everyone_else():
    # D9: a non-willing seed still counts as adopted; non-willing non-seeds never do.
    spec = clique_spec(4, theta=0.3, willing=[False, False, True, True])
    r = predict_team(spec, [0])
    assert r["adopted"][0]            # seed, despite not being willing
    assert not r["adopted"][1]        # not willing -> never adopts
    assert r["adopted"][2] and r["adopted"][3]


def test_ignition_is_monotone_in_the_seed_count():
    fracs = []
    for s in range(0, 7):
        stats = p_ignite(s, 6, np.random.default_rng(11), n_draws=250, w_ext=4.0)
        fracs.append(stats["p_ignite"])
    assert fracs == sorted(fracs), f"P_ig must not decrease with more seeds: {fracs}"
    assert fracs[0] < fracs[-1]
    assert fracs[-1] == 1.0            # a fully seeded team is ignited by definition


def test_visibility_scales_exposure():
    # v = 0.5 halves the numerator: 1/3 -> 1/6 < 0.3, so the cascade dies.
    spec = clique_spec(4, theta=0.3)
    assert predict_team(spec, [0], visibility=1.0)["fraction"] == 1.0
    assert predict_team(spec, [0], visibility=0.5)["fraction"] == 0.25


def test_cascade_validation_errors():
    spec = clique_spec(4, theta=0.3)
    with pytest.raises(ValueError):
        cascade(spec, np.zeros(3, dtype=bool))
    with pytest.raises(ValueError):
        cascade(spec, [0], ext_mass=np.zeros(3))
    with pytest.raises(ValueError):
        TeamSpec(theta=np.zeros(3), willing=np.ones(3, bool), able=np.ones(3, bool),
                 w_in=np.zeros((3, 3)), w_total=np.full(3, -1.0))


# --- Fidelity to the engine (the load-bearing test) -----------------------------

def test_cascade_matches_the_engine_on_an_isolated_team():
    """Engine vs predictor on the same team, with out-of-team contacts that can
    never adopt (not willing) — exactly the isolated-team question of level 1."""
    m, w_ext = 5, 2.0
    edges = [(i, j, 1.0) for i in range(m) for j in range(i + 1, m)]
    edges += [(i, m + i, w_ext) for i in range(m)]      # one pendant contact each
    n = 2 * m
    org = tiny_org(edges, n=n, team=[0] * m + [1] * m)
    theta = np.array([0.0, 0.25, 0.45, 0.55, 0.95] + [0.5] * m)
    willing = np.array([True] * m + [False] * m)        # pendants can never adopt
    theta, willing, able = fixed_agents(n, theta, willing=willing)

    for seed_set in ([0], [1], [1, 2], [0, 4]):
        seeding = Seeding("test", np.array(seed_set, dtype=np.int64), False, {})
        res = run_simulation(org, SimParams(max_steps=50), seeding,
                             agents=(theta, willing, able))
        spec = team_specs_from_org(org, theta, willing, able, skip_leadership=False)[0]
        pred = cascade(spec, seed_set)
        np.testing.assert_array_equal(pred, res.adopted[:m])
        assert math.isclose(pred.mean(), res.team_final[0])


def test_team_specs_from_org_carry_the_full_denominator():
    m, w_ext = 4, 3.0
    edges = [(i, j, 1.0) for i in range(m) for j in range(i + 1, m)]
    edges += [(i, m + i, w_ext) for i in range(m)]
    n = 2 * m
    org = tiny_org(edges, n=n, team=[0] * m + [1] * m)
    theta, willing, able = fixed_agents(n, 0.3)
    spec = team_specs_from_org(org, theta, willing, able, skip_leadership=False)[0]
    assert spec.size == m
    np.testing.assert_allclose(spec.w_in.sum(axis=1), m - 1)     # within-team only
    np.testing.assert_allclose(spec.w_total, (m - 1) + w_ext)    # incl. external


def test_sample_team_follows_the_generator_recipe():
    rng = np.random.default_rng(0)
    spec = sample_team(9, rng, w_ext=(6.0, 4.0), p_team=1.0)
    assert spec.size == 9
    # Manager (member 0) wired to every IC at manager_report.
    assert np.allclose(spec.w_in[0, 1:], 0.7) and np.allclose(spec.w_in[1:, 0], 0.7)
    # p_team = 1 -> IC-IC clique at peer_close.
    ic = spec.w_in[1:, 1:]
    assert np.allclose(ic[~np.eye(8, dtype=bool)], 1.0)
    assert np.allclose(np.diag(spec.w_in), 0.0)
    # External mass is role-dependent and lands in w_total only.
    assert math.isclose(spec.w_total[0] - spec.w_in[0].sum(), 6.0)
    assert math.isclose(spec.w_total[1] - spec.w_in[1].sum(), 4.0)
    with pytest.raises(ValueError):
        sample_team(1, rng)


def test_measure_external_mass_separates_roles():
    from core import defaults
    edges = [(0, 1, 0.7), (0, 2, 0.7), (1, 2, 1.0), (0, 3, 0.6), (1, 3, 0.6)]
    org = tiny_org(edges, n=4, team=[0, 0, 0, 1], role=[defaults.ROLE_MANAGER, 0, 0, 0])
    ext = measure_external_mass(org, skip_leadership=False)
    # Node 0 (manager, team 0) reaches out only to node 3: 0.6.
    assert math.isclose(ext["manager"], 0.6)
    # ICs are nodes 1 (0.6 to node 3), 2 (nothing outside), and 3 — which sits in
    # team 1, so BOTH its ties (0.6 + 0.6) are out-of-team.
    assert math.isclose(ext["ic"], (0.6 + 0.0 + 1.2) / 3)
    assert math.isclose(ext["overall"], (0.6 + 0.6 + 0.0 + 1.2) / 4)


# --- Seed-count folding ---------------------------------------------------------

def test_hypergeom_pmf_is_a_distribution():
    n_pop, k, m = 2000, 100, 8
    ps = [hypergeom_pmf(s, n_pop, k, m) for s in range(m + 1)]
    assert math.isclose(sum(ps), 1.0, abs_tol=1e-12)
    mean = sum(s * p for s, p in enumerate(ps))
    assert math.isclose(mean, m * k / n_pop, rel_tol=1e-9)   # = 0.4 seeds/team
    assert hypergeom_pmf(-1, n_pop, k, m) == 0.0
    assert hypergeom_pmf(9, n_pop, k, m) == 0.0


def test_seeds_per_team_pmf_per_strategy():
    n_pop, k, m, n_teams = 2000, 100, 8, 249
    rnd = seeds_per_team_pmf("random", n_pop, k, m, n_teams)
    assert math.isclose(rnd.sum(), 1.0)
    assert rnd[0] > 0.6                       # most teams get nothing at 5%
    # cluster: 100 seeds fill 12 whole teams of 8, plus one team with 4.
    clu = seeds_per_team_pmf("cluster", n_pop, k, m, n_teams)
    assert math.isclose(clu[m], 12 / n_teams)
    assert math.isclose(clu[4], 1 / n_teams)
    assert math.isclose(clu.sum(), 1.0)
    # one_per_team: 100 seeds over 249 teams -> 100 teams with exactly 1.
    opt = seeds_per_team_pmf("one_per_team", n_pop, k, m, n_teams)
    assert math.isclose(opt[1], 100 / n_teams) and math.isclose(opt[0], 149 / n_teams)
    with pytest.raises(ValueError):
        seeds_per_team_pmf("champions", n_pop, k, m, n_teams)


def test_predict_strategy_orders_local_ignition_as_folklore_expects():
    """Level 1 alone must reproduce the LOCAL truth behind the folklore:
    concentration buys near-certain team ignitions, dispersion buys few."""
    common = dict(n_pop=2000, n_seeds=100, m=8, n_teams=249, n_draws=120, w_ext=6.0)
    clu = predict_strategy("cluster", np.random.default_rng(1), **common)
    rnd = predict_strategy("random", np.random.default_rng(1), **common)
    assert clu["p_team_ignites"] > rnd["p_team_ignites"]
    assert clu["expected_ignited_teams"] >= 12      # the filled teams, at least
    assert 0.0 <= rnd["reach_local"] <= 1.0


# --- Validation gates -----------------------------------------------------------

def test_roc_auc_known_values():
    assert roc_auc([0.1, 0.2, 0.3, 0.4], [False, False, True, True]) == 1.0
    assert roc_auc([0.4, 0.3, 0.2, 0.1], [False, False, True, True]) == 0.0
    assert roc_auc([1.0, 1.0, 1.0, 1.0], [False, True, False, True]) == 0.5  # all ties
    assert roc_auc([0.1, 0.5, 0.4, 0.9], [False, True, False, True]) == 1.0
    assert math.isnan(roc_auc([0.1, 0.2], [True, True]))      # one class only
    with pytest.raises(ValueError):
        roc_auc([0.1, 0.2], [True])


def test_v1_scores_only_seeded_teams():
    specs = {0: clique_spec(4, 0.3), 1: clique_spec(4, 0.3), 2: clique_spec(4, 0.9)}
    seeds = {0: np.array([0]), 1: np.array([]), 2: np.array([0])}   # team 1 unseeded
    observed = {0: 1.0, 1: 1.0, 2: 0.10}
    rep = v1_local_ignition(specs, seeds, observed)
    assert rep["n_teams"] == 2                     # unseeded team excluded (D21)
    assert rep["accuracy"] == 1.0 and rep["auc"] == 1.0
    assert rep["tp"] == 1 and rep["tn"] == 1
    with pytest.raises(ValueError):
        v1_local_ignition(specs, {0: np.array([])}, observed)


def test_v2_sign_agreement_counts_opposite_errors():
    observed = {
        "a": {"cls": "win_x", "mean_d": 0.44},
        "b": {"cls": "win_y", "mean_d": -0.03},
        "c": {"cls": "equivalent", "mean_d": 0.001},   # not decisive -> ignored
        "d": {"cls": "uncertain", "mean_d": 0.01},     # not decisive -> ignored
    }
    rep = v2_sign_agreement({"a": 0.30, "b": 0.02, "c": 0.0, "d": 0.0}, observed)
    assert rep["n_decisive_cells"] == 2
    assert rep["agreement"] == 0.5 and rep["opposite_sign_errors"] == 1
    # A predicted exact tie is a disagreement, never a free pass.
    rep0 = v2_sign_agreement({"a": 0.0, "b": -0.01}, observed)
    assert rep0["agreement"] == 0.5 and rep0["opposite_sign_errors"] == 0
    rep_missing = v2_sign_agreement({"a": 0.3}, observed)
    assert rep_missing["n_missing_predictions"] == 1 and rep_missing["missing"] == ["b"]


def test_calibration_is_deterministic_and_correctly_worded():
    """calibrate() must be bit-reproducible under a fixed seed, and its
    non-local shares must use the pre-declared denominators (teams vs reach)."""
    from experiments.calibrate_predictor import calibrate
    a = calibrate(seed=123, n_orgs=1, n_draws_curve=30, n_draws_fold=30)
    b = calibrate(seed=123, n_orgs=1, n_draws_curve=30, n_draws_fold=30)
    a.pop("comparison_vs_observed"); b.pop("comparison_vs_observed")
    assert a == b
    c = calibrate(seed=124, n_orgs=1, n_draws_curve=30, n_draws_fold=30)
    assert c["p_ignite_curve_m8"] != a["p_ignite_curve_m8"]
    # Structural sanity: P_ig curve monotone, fully-seeded team certain.
    ps = [a["p_ignite_curve_m8"][s]["p_ignite"] for s in range(9)]
    assert ps == sorted(ps) and ps[0] == 0.0 and ps[-1] == 1.0


def test_verdict_applies_the_predeclared_gates():
    assert verdict(0.85, 0.95, 0)["verdict"] == "go"
    assert verdict(0.80, 0.90, 0)["verdict"] == "go"          # boundaries inclusive
    assert verdict(0.85, 0.95, 1)["verdict"] == "partial"     # any opposite error blocks go
    assert verdict(0.85, 0.40, 0)["verdict"] == "partial"     # V1 passes, V2 fails
    assert verdict(0.75, 0.99, 0)["verdict"] == "partial"     # AUC in the partial band
    assert verdict(0.69, 0.99, 0)["verdict"] == "no_go"
    assert verdict(math.nan, 0.99, 0)["verdict"] == "no_go"   # undefined AUC is not a pass
    assert len(verdict(0.85, 0.95, 0)["reasons"]) == 3
