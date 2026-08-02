"""Seeding strategies: budget exactness, composition, fairness (D9)."""

import numpy as np
import pytest

from core import defaults
from core.orggen import LEADERSHIP_TEAM, generate_org
from core.seeding import STRATEGIES, make_seeding


def compiled(n=600, seed=5, **kw):
    return generate_org(n_agents=n, seed=seed, **kw).compile()


def test_equal_budget_across_seeded_strategies():
    c = compiled()
    k_expected = int(np.floor(0.05 * c.n))
    for strategy in STRATEGIES:
        s = make_seeding(strategy, c, budget=0.05, rng=1)
        if strategy == "broadcast":
            assert s.initial_adopters.size == 0 and s.broadcast
        else:
            assert s.initial_adopters.size == k_expected
            assert not s.broadcast
            assert np.unique(s.initial_adopters).size == k_expected


def test_champions_are_top_degree():
    c = compiled()
    s = make_seeding("champions", c, budget=0.05, rng=2)
    deg = c.degrees()
    non_seeds = np.setdiff1d(np.arange(c.n), s.initial_adopters)
    assert deg[s.initial_adopters].min() >= deg[non_seeds].max() - 0  # ties at the cut allowed
    assert deg[s.initial_adopters].mean() > deg.mean()


def test_champions_custom_scores_override():
    c = compiled()
    scores = np.zeros(c.n)
    scores[[3, 4, 5]] = 1.0
    s = make_seeding("champions", c, budget=3 / c.n, rng=2, scores=scores)
    assert set(s.initial_adopters) == {3, 4, 5}


def test_cluster_fills_whole_teams():
    c = compiled()
    s = make_seeding("cluster", c, budget=0.05, rng=3)
    teams_used = s.meta["teams_seeded"]
    assert LEADERSHIP_TEAM not in teams_used
    # All used teams except possibly the last are fully seeded.
    seeded = set(s.initial_adopters.tolist())
    for t in teams_used[:-1]:
        members = set(np.flatnonzero(c.team == t).tolist())
        assert members <= seeded
    # Concentration: cluster touches far fewer teams than random seeding does.
    r = make_seeding("random", c, budget=0.05, rng=3)
    assert len(set(c.team[s.initial_adopters])) < len(set(c.team[r.initial_adopters]))


def test_line_manager_first_picks_managers():
    c = compiled()
    s = make_seeding("line_manager_first", c, budget=0.02, rng=4)
    assert (c.role[s.initial_adopters] == defaults.ROLE_MANAGER).all()
    assert s.meta["topped_up_with_random"] == 0


def test_line_manager_top_up_when_budget_exceeds_managers():
    c = compiled()
    n_managers = int((c.role == defaults.ROLE_MANAGER).sum())
    budget = (n_managers + 10) / c.n
    s = make_seeding("line_manager_first", c, budget=budget, rng=4)
    assert s.meta["topped_up_with_random"] == 10
    seeded_roles = c.role[s.initial_adopters]
    assert (seeded_roles == defaults.ROLE_MANAGER).sum() == n_managers


def test_one_per_team_covers_distinct_teams():
    c = compiled()
    s = make_seeding("one_per_team", c, budget=0.05, rng=6)
    k = int(np.floor(0.05 * c.n))
    seed_teams = c.team[s.initial_adopters]
    assert LEADERSHIP_TEAM not in seed_teams
    # One pass: k < n_line_teams -> k distinct teams, exactly one seed each.
    assert np.unique(seed_teams).size == k
    assert s.meta["teams_covered"] == k
    assert s.meta["passes"] == 1


def test_one_per_team_second_pass_when_budget_exceeds_teams():
    c = compiled()
    n_line_teams = c.n_teams - 1
    k = n_line_teams + 5
    s = make_seeding("one_per_team", c, budget=(k + 0.5) / c.n, rng=6)  # floor-proof
    assert s.initial_adopters.size == k
    seed_teams = c.team[s.initial_adopters]
    counts = np.bincount(seed_teams, minlength=c.n_teams)
    assert counts[LEADERSHIP_TEAM] == 0
    line = np.array([t for t in range(c.n_teams) if t != LEADERSHIP_TEAM])
    assert (counts[line] >= 1).all()          # every line team covered
    assert (counts[line] <= 2).all()          # second pass only just started
    assert (counts[line] == 2).sum() == 5
    assert s.meta["teams_covered"] == n_line_teams
    assert s.meta["passes"] == 2


def test_validation_errors():
    c = compiled()
    with pytest.raises(ValueError):
        make_seeding("viral", c)
    with pytest.raises(ValueError):
        make_seeding("random", c, budget=0.9)
    with pytest.raises(ValueError):
        make_seeding("random", c, budget=0.0001)  # 0 seeds


def test_seeding_determinism():
    c = compiled()
    for strategy in ("random", "cluster", "champions", "line_manager_first", "one_per_team"):
        a = make_seeding(strategy, c, 0.05, rng=9).initial_adopters
        b = make_seeding(strategy, c, 0.05, rng=9).initial_adopters
        np.testing.assert_array_equal(a, b)
