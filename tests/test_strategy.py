"""Phase 1 strategy tests (part 1): session, bias."""

from datetime import date, datetime, timezone

import pytest

from engine.bars import Bar, resample
from engine.bias import bias_from_m1, compute_bias
from engine.config import Bias, StrategyConfig
from engine.session import build_opening_range, check_or_size

UTC = timezone.utc
CFG = StrategyConfig()


def utc(y, mo, d, h, mi):
    return datetime(y, mo, d, h, mi, tzinfo=UTC)


def m1_at(h, mi, o=100.0, hi=101.0, lo=99.0, c=100.0):
    return Bar(time_utc=utc(2024, 1, 15, h, mi), open=o, high=hi, low=lo, close=c)


def or_bars(n=15):
    # 09:30-09:44 NY == 14:30-14:44 UTC on 2024-01-15 (EST).
    return [Bar(time_utc=datetime(2024, 1, 15, 14, 30 + i, tzinfo=UTC),
                open=100, high=100 + (i % 3), low=99, close=100)
            for i in range(n)]


def test_or_valid_all_15_present():
    or_ = build_opening_range(or_bars(), date(2024, 1, 15), CFG)
    assert or_.valid and or_.bar_count == 15
    assert or_.high == 102 and or_.low == 99


def test_or_invalid_missing_bar():
    or_ = build_opening_range(or_bars(n=14), date(2024, 1, 15), CFG)
    assert not or_.valid
    assert or_.reason == "Opening Range incomplete (missing bars)"


def test_or_size_filters():
    or_ = build_opening_range(or_bars(), date(2024, 1, 15), CFG)
    assert or_.size == 3.0
    ok, _ = check_or_size(or_, 8.0, CFG)
    assert ok
    ok, reason = check_or_size(or_, 20.0, CFG)
    assert not ok and reason == "Opening Range too small"
    ok, reason = check_or_size(or_, 2.0, CFG)
    assert not ok and reason == "Opening Range too large"


def test_or_size_no_atr():
    or_ = build_opening_range(or_bars(), date(2024, 1, 15), CFG)
    ok, reason = check_or_size(or_, None, CFG)
    assert not ok and reason == "Insufficient data"


def test_bias_bullish():
    closes = [100 + i * 0.5 for i in range(60)]
    bias, _ = compute_bias(closes, 20, 50)
    assert bias == Bias.BULLISH


def test_bias_bearish():
    closes = [200 - i * 0.5 for i in range(60)]
    bias, _ = compute_bias(closes, 20, 50)
    assert bias == Bias.BEARISH


def test_bias_neutral_flat():
    bias, _ = compute_bias([100.0] * 60, 20, 50)
    assert bias == Bias.NEUTRAL


def test_bias_insufficient_history():
    bias, _ = compute_bias([100.0] * 10, 20, 50)
    assert bias == Bias.NEUTRAL


def test_bias_prefix_consistency():
    bars = [Bar(time_utc=datetime(2024, 1, 8, 0, 0, tzinfo=UTC),
                open=100 + i * 0.01, high=100 + i * 0.01 + 0.5,
                low=100 + i * 0.01 - 0.5, close=100 + i * 0.01)
            for i in range(1200)]
    cut = len(bars) // 2
    a, _ = bias_from_m1(bars, cut, CFG)
    b, _ = bias_from_m1(bars[: cut + 1], cut, CFG)
    assert a == b
