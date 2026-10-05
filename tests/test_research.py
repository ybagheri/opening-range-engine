"""Research machinery tests (Phases 6/7/8/11): splits, WF, MC, assess."""

import pytest

from engine.config import StrategyConfig
from engine.data.synthetic import generate_m1
from engine.research.assessment import assess
from engine.research.montecarlo import run_monte_carlo
from engine.research.sensitivity import run_grid
from engine.research.splits import make_splits, walk_forward_windows

CFG = StrategyConfig()


def test_make_splits_chronological():
    days = [f"2024-01-{d:02d}" for d in range(1, 11)]
    split = make_splits(days)
    assert list(split.train) == days[:6]
    assert list(split.validation) == days[6:8]
    assert list(split.oos) == days[8:]
    assert split.oos == tuple(days[8:])


def test_make_splits_rejects_tiny():
    with pytest.raises(ValueError):
        make_splits(["a", "b"])


def test_walk_forward_no_overlap():
    days = list(range(10))
    wins = list(walk_forward_windows(days, 4, 2, step=2))
    assert wins[0] == ([0, 1, 2, 3], [4, 5])
    assert wins[1] == ([2, 3, 4, 5], [6, 7])
    for train, test in wins:
        assert max(train) < min(test)


def test_monte_carlo_seeded_deterministic():
    rs = [1.5, -1.0, 1.5, 0.0, -1.0, 1.5]
    a = run_monte_carlo(rs, n_sims=500, seed=7)
    b = run_monte_carlo(rs, n_sims=500, seed=7)
    assert a == b
    assert 0.0 <= a.prob_profit <= 1.0
    assert a.p5_net_r <= a.p50_net_r <= a.p95_net_r


def test_monte_carlo_modes_differ():
    rs = [1.5, -1.0, 1.5, 0.0, -1.0, 1.5]
    p = run_monte_carlo(rs, n_sims=500, seed=7, mode="permute")
    b = run_monte_carlo(rs, n_sims=500, seed=7, mode="bootstrap")
    assert p.mean_net_r == pytest.approx(sum(rs))
    assert b.mean_net_r == pytest.approx(sum(rs), abs=1.5)


def test_assess_inconclusive_on_tiny_sample():
    v = assess(4, 1.5, float("inf"), 0.0, "ROBUST REGION", 0.9)
    assert v.label == "INCONCLUSIVE"


def test_assess_overfit_on_instability():
    v = assess(100, 0.5, 2.0, 3.0, "POSSIBLE OVERFITTING", 0.9)
    assert v.label == "OVERFIT"


def test_assess_robust_needs_everything():
    v = assess(100, 0.4, 1.8, 4.0, "ROBUST REGION", 0.9)
    assert v.label == "ROBUST"
    v2 = assess(100, 0.4, 1.8, 4.0, "ROBUST REGION", 0.5)
    assert v2.label == "PROMISING"


def test_sensitivity_grid_runs_on_synthetic():
    bars = generate_m1(seed=42, days=5)
    report = run_grid(bars, CFG)
    assert len(report.cells) == 5 + 4
    assert report.verdict() in ("ROBUST REGION", "POSSIBLE OVERFITTING")
    tp_cells = [c for c in report.cells if c.varied == "tp_multiplier"]
    assert [c.value for c in tp_cells] == [1.0, 1.25, 1.5, 1.75, 2.0]
