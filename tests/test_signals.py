"""Phase 1 strategy tests (part 2): breakout, pullback, trigger, limits."""

from datetime import datetime, timezone

import pytest

from engine.bars import Bar, resample
from engine.config import Bias, SignalState, StrategyConfig
from engine.signals import (
    NO_TRADE_REASONS,
    build_trade_params,
    check_daily_limits,
    is_breakout_bar,
    is_signal_bar,
    pullback_state,
    signal_bar_in_window,
)

UTC = timezone.utc
CFG = StrategyConfig()


def utc(h, mi):
    return datetime(2024, 1, 15, h, mi, tzinfo=UTC)


def m1_at(h, mi, o=100.0, hi=101.0, lo=99.0, c=100.0):
    return Bar(time_utc=utc(h, mi), open=o, high=hi, low=lo, close=c)


def m5(h, mi, o=101.0, hi=106.0, lo=101.0, c=105.0):
    return Bar(time_utc=utc(h, mi), open=o, high=hi, low=lo, close=c)


def test_breakout_bullish_close_beyond():
    bo, reason = is_breakout_bar(m5(14, 50), 102, 98, Bias.BULLISH, 10.0, CFG)
    assert bo is not None and bo.direction == "BULLISH" and reason is None


def test_breakout_wick_only_is_waiting():
    bar = m5(14, 50, c=101.0, hi=110.0)
    bo, reason = is_breakout_bar(bar, 102, 98, Bias.BULLISH, 10.0, CFG)
    assert bo is None and reason is None


def test_breakout_wrong_bias_is_waiting():
    bo, reason = is_breakout_bar(m5(14, 50), 102, 98, Bias.BEARISH, 10.0, CFG)
    assert bo is None and reason is None


def test_breakout_extension_limit():
    bo, reason = is_breakout_bar(m5(14, 50, c=110.0, hi=111.0), 102, 98,
                                 Bias.BULLISH, 10.0, CFG)
    assert bo is None and reason == "Breakout extension too large"


def test_breakout_after_window():
    bo, reason = is_breakout_bar(m5(16, 35), 102, 98, Bias.BULLISH, 10.0, CFG)
    assert bo is None and reason == "Breakout occurred after trading window"


def test_pullback_bullish_confirmed():
    after = [Bar(time_utc=utc(14, 55 + i), open=102, high=102.5,
                 low=101.5, close=102.0) for i in range(2)]
    state, extreme = pullback_state(after, "BULLISH", 102.0, 10.0, CFG)
    assert state == "CONFIRMED" and extreme == pytest.approx(101.5)


def test_pullback_bullish_invalidated():
    bad = [Bar(time_utc=utc(14, 55), open=100, high=101, low=98, close=98.0)]
    state, _ = pullback_state(bad, "BULLISH", 102.0, 10.0, CFG)
    assert state == "INVALIDATED"


def test_pullback_bearish_mirror():
    after = [Bar(time_utc=utc(14, 55), open=98, high=98.5, low=97.5, close=98.0)]
    state, extreme = pullback_state(after, "BEARISH", 98.0, 10.0, CFG)
    assert state == "CONFIRMED" and extreme == pytest.approx(98.5)


def test_signal_bar_bullish():
    prev = m1_at(14, 55, hi=103.0)
    sig = m1_at(14, 56, o=103.0, hi=104.0, lo=103.0, c=103.5)
    assert is_signal_bar(sig, prev, "BULLISH", 102.0, 98.0)
    assert not is_signal_bar(sig, prev, "BEARISH", 102.0, 98.0)


def test_trade_params_entry_stop_tp():
    sig = m1_at(14, 56, hi=104.0, lo=103.0)
    tp, reason = build_trade_params("BULLISH", sig, 101.5, 10.0, CFG)
    assert reason is None
    assert tp.entry == pytest.approx(105.0)
    assert tp.stop == pytest.approx(100.5)
    assert tp.risk_distance == pytest.approx(4.5)
    assert tp.take_profit == pytest.approx(105.0 + 1.5 * 4.5)


def test_trade_params_stop_filter():
    sig = m1_at(14, 56, hi=104.0, lo=103.0)
    tp, reason = build_trade_params("BULLISH", sig, 105.5, 10.0, CFG)
    assert tp is None and reason == "Stop distance too small"


def test_signal_bar_window_edges():
    assert signal_bar_in_window(m1_at(14, 45))
    assert signal_bar_in_window(m1_at(16, 29))
    assert not signal_bar_in_window(m1_at(16, 30))


def test_daily_limits_order():
    assert check_daily_limits(0, 0.0, False, CFG) == (True, None)
    assert check_daily_limits(0, -2.0, False, CFG)[1] == "Daily loss limit reached"
    assert check_daily_limits(2, 0.0, False, CFG)[1] == "Daily trade limit reached"
    assert check_daily_limits(0, 0.0, True, CFG)[1] == "Same-direction setup already active"


def test_registry_counts():
    assert len(NO_TRADE_REASONS) == 14
    assert len(list(SignalState)) == 12


def test_m15_resample_never_uses_future_bar():
    bars = [m1_at(14, 30 + i) for i in range(6)]
    assert len(resample(bars, 5)) == 1
    assert len(resample(bars + [m1_at(14, 36)], 5)) == 1
