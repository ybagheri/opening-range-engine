"""Phase 3 tests (part 2): metrics + cost sensitivity + reports."""

import pytest

from engine.backtest.costs import CostModel
from engine.backtest.metrics import compute_metrics
from engine.backtest.records import trade_from_signal_and_result
from engine.backtest.report import export_equity, export_summary, export_trades
from engine.backtest.simulator import simulate_signal
from engine.config import StrategyConfig
from tests.test_backtest import _bar, _sig

CFG = StrategyConfig()


def test_metrics_hand_computed():
    m = compute_metrics([1.5, -1.0, 1.5, -1.0])
    assert m.n_trades == 4
    assert m.win_rate == pytest.approx(0.5)
    assert m.avg_win_r == pytest.approx(1.5)
    assert m.avg_loss_r == pytest.approx(-1.0)
    assert m.expectancy_r == pytest.approx(0.25)
    assert m.net_r == pytest.approx(1.0)
    assert m.profit_factor == pytest.approx(1.5)
    assert m.max_drawdown_r == pytest.approx(1.0)
    assert m.median_r == pytest.approx(0.25)


def test_metrics_empty():
    m = compute_metrics([])
    assert m.n_trades == 0 and m.net_r == 0.0


def test_slippage_reduces_win_r():
    sig = _sig()
    bars = [_bar(14, 51, hi=106.0, lo=104.0, c=105.0),
            _bar(14, 52, hi=113.0, lo=106.0, c=112.0)]
    free = simulate_signal(sig, bars, CFG, CostModel())
    slip = simulate_signal(sig, bars, CFG,
                           CostModel(slippage_points=2, point=1.0))
    assert slip.fill_price == pytest.approx(107.0)
    assert slip.r_result < free.r_result


def test_cost_sensitivity_monotonic(tmp_path=None):
    sig = _sig()
    bars = [_bar(14, 51, hi=106.0, lo=104.0, c=105.0),
            _bar(14, 52, hi=113.0, lo=106.0, c=112.0)]
    rs = [simulate_signal(sig, bars, CFG,
                          CostModel(slippage_points=p, point=1.0)).r_result
          for p in (0, 1, 2, 5, 10)]
    assert rs == sorted(rs, reverse=True)


def test_trade_record_and_exports(tmp_path):
    sig = _sig()
    bars = [_bar(14, 51, hi=106.0, lo=104.0, c=105.0),
            _bar(14, 52, hi=113.0, lo=106.0, c=112.0)]
    res = simulate_signal(sig, bars, CFG)
    tr = trade_from_signal_and_result(sig, res)
    assert tr.result == "WIN"
    p1 = str(tmp_path / "trades.csv")
    export_trades([tr], p1)
    header = open(p1).readline().strip().split(",")
    assert "r_result" in header and "mae_r" in header
    m = compute_metrics([res.r_result])
    p2 = str(tmp_path / "summary.txt")
    export_summary(m, CostModel(), p2)
    assert "expectancy_r" in open(p2).read()
    p3 = str(tmp_path / "equity.csv")
    export_equity([res.r_result], p3)
    assert "equity_r" in open(p3).readline()
