"""Phase 3 tests (part 1): costs + simulator edge cases."""

from datetime import datetime, timezone

import pytest

from engine.backtest.costs import CostModel
from engine.backtest.simulator import simulate_signal
from engine.bars import Bar
from engine.config import StrategyConfig
from engine.data.schema import SignalRecord

UTC = timezone.utc
CFG = StrategyConfig()


def _bar(h, mi, o=100.0, hi=101.0, lo=99.0, c=100.0):
    return Bar(time_utc=datetime(2024, 1, 9, h, mi, tzinfo=UTC),
               open=o, high=hi, low=lo, close=c)


def _sig(entry=105.0, stop=100.0, tp=112.5, direction="BULLISH",
         sig_time="2024-01-09T14:50:00+00:00"):
    return SignalRecord(
        date="2024-01-09", signal_time_utc=sig_time, symbol="US30",
        direction=direction, session="NY_CASH_OPEN",
        or_high=104.0, or_low=100.0, or_size=4.0, atr_m5=8.0,
        m15_ema_fast=102.0, m15_ema_slow=100.0,
        entry=entry, stop=stop, take_profit=tp,
        risk_distance=abs(entry - stop), r_multiple=1.5,
        spread_at_signal=2.0, commission=0.0, slippage_points=0)

def test_entry_fill_bullish_no_slippage():
    costs = CostModel().validate()
    assert costs.entry_fill(105.0, "BULLISH") == 105.0
    assert costs.entry_fill(105.0, "BEARISH") == 105.0


def test_entry_fill_applies_slippage_adversely():
    costs = CostModel(slippage_points=2, point=1.0).validate()
    assert costs.entry_fill(105.0, "BULLISH") == 107.0
    assert costs.entry_fill(105.0, "BEARISH") == 103.0


def test_win_when_tp_hit_first():
    sig = _sig()
    bars = [_bar(14, 51, hi=106.0, lo=104.0, c=105.0),
            _bar(14, 52, hi=113.0, lo=106.0, c=112.0)]
    res = simulate_signal(sig, bars, CFG)
    assert res.result == "WIN"
    assert res.r_result == pytest.approx(1.5)
    assert res.fill_price == pytest.approx(105.0)


def test_loss_when_sl_hit_first():
    sig = _sig()
    bars = [_bar(14, 51, hi=106.0, lo=104.0, c=105.0),
            _bar(14, 52, hi=106.0, lo=99.0, c=100.0)]
    res = simulate_signal(sig, bars, CFG)
    assert res.result == "LOSS"
    assert res.r_result == pytest.approx(-1.0)


def test_same_bar_sl_tp_resolves_sl_first():
    sig = _sig()
    bars = [_bar(14, 51, hi=106.0, lo=104.0, c=105.0),
            _bar(14, 52, hi=115.0, lo=98.0, c=100.0)]
    res = simulate_signal(sig, bars, CFG)
    assert res.result == "LOSS"
    assert res.r_result == pytest.approx(-1.0)


def test_expired_when_entry_never_touched():
    sig = _sig(entry=120.0, stop=115.0, tp=122.5)
    bars = [_bar(14, 51, hi=106.0, lo=104.0, c=105.0),
            _bar(16, 35, hi=106.0, lo=104.0, c=105.0)]
    res = simulate_signal(sig, bars, CFG)
    assert res.result == "EXPIRED"
    assert res.r_result == pytest.approx(0.0)


def test_unfilled_order_expires_at_1130():
    sig = _sig(entry=106.0, stop=101.0, tp=113.5)
    bars = [_bar(14, 51, hi=105.0, lo=104.0, c=104.5),
            _bar(16, 29, hi=105.0, lo=104.0, c=104.5),
            _bar(16, 30, hi=110.0, lo=104.0, c=109.0)]
    res = simulate_signal(sig, bars, CFG)
    assert res.result == "EXPIRED"


def test_mae_mfe_tracked_in_r():
    sig = _sig()
    bars = [_bar(14, 51, hi=106.0, lo=104.0, c=105.0),
            _bar(14, 52, hi=108.0, lo=103.0, c=107.0),
            _bar(14, 53, hi=113.0, lo=107.0, c=112.0)]
    res = simulate_signal(sig, bars, CFG)
    assert res.mae_r == pytest.approx((103.0 - 105.0) / 5.0)
    assert res.mfe_r == pytest.approx((113.0 - 105.0) / 5.0)
    assert res.result == "WIN"

