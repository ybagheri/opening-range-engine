"""Phase 1 core tests: config, NY time/DST, bars, indicators."""

from datetime import date, datetime, time, timezone

import pytest

from engine import config as cfg_mod
from engine.bars import Bar, bucket_start_utc, check_contiguous, ensure_sorted_unique, resample
from engine.indicators import atr_series, ema
from engine.ny_time import (
    NY_TZ,
    is_dst_ny,
    is_dst_ny_rules,
    ny_date,
    to_ny,
    us_dst_end_utc,
    us_dst_start_utc,
)

UTC = timezone.utc


def utc(y, mo, d, h, mi):
    return datetime(y, mo, d, h, mi, tzinfo=UTC)


# --- config ---

def test_config_defaults_validate():
    c = cfg_mod.StrategyConfig().validate()
    assert c.tp_multiplier == 1.5
    assert c.opening_range_minutes == 15


def test_config_rejects_bad_ema():
    with pytest.raises(ValueError):
        cfg_mod.StrategyConfig(ema_fast=50, ema_slow=20).validate()


def test_config_rejects_bad_or_band():
    with pytest.raises(ValueError):
        cfg_mod.StrategyConfig(min_or_atr=1.0, max_or_atr=0.25).validate()


def test_tp_mode_from_string():
    assert cfg_mod.TPMode.from_string("R1.5") == cfg_mod.TPMode.R1_5
    assert cfg_mod.TPMode.from_string("R2") == cfg_mod.TPMode.R2
    with pytest.raises(ValueError):
        cfg_mod.TPMode.from_string("R9")


def test_signal_states_count():
    assert len(list(cfg_mod.SignalState)) == 12


# --- NY time ---

def test_ny_conversion_est():
    # 2024-01-15 14:30 UTC == 09:30 EST (UTC-5).
    assert to_ny(utc(2024, 1, 15, 14, 30)).hour == 9
    assert to_ny(utc(2024, 1, 15, 14, 30)).utcoffset().total_seconds() == -5 * 3600


def test_ny_conversion_edt():
    # 2024-07-15 13:30 UTC == 09:30 EDT (UTC-4).
    assert to_ny(utc(2024, 7, 15, 13, 30)).hour == 9
    assert to_ny(utc(2024, 7, 15, 13, 30)).utcoffset().total_seconds() == -4 * 3600


def test_dst_rules_match_zoneinfo():
    probes = [utc(2024, m, 15, 12, 0) for m in range(1, 13)]
    probes += [utc(2025, m, 15, 12, 0) for m in range(1, 13)]
    for p in probes:
        assert is_dst_ny(p) == is_dst_ny_rules(p), p


def test_dst_transitions_known_instants():
    # 2024: spring forward Mar 10 07:00 UTC; fall back Nov 3 06:00 UTC.
    assert us_dst_start_utc(2024) == utc(2024, 3, 10, 7, 0)
    assert us_dst_end_utc(2024) == utc(2024, 11, 3, 6, 0)
    assert not is_dst_ny_rules(utc(2024, 3, 10, 6, 59))
    assert is_dst_ny_rules(utc(2024, 3, 10, 7, 0))
    assert is_dst_ny_rules(utc(2024, 11, 3, 5, 59))
    assert not is_dst_ny_rules(utc(2024, 11, 3, 6, 0))


def test_ny_date_session_day():
    assert ny_date(utc(2024, 1, 15, 14, 30)) == date(2024, 1, 15)


def test_to_ny_rejects_naive():
    with pytest.raises(ValueError):
        to_ny(datetime(2024, 1, 15, 14, 30))


# --- bars ---

def _m1(h, mi, **kw):
    base = dict(open=100.0, high=101.0, low=99.0, close=100.5)
    base.update(kw)
    return Bar(time_utc=utc(2024, 1, 15, h, mi), **base)


def test_bar_validate_ok():
    _m1(14, 30).validate()


def test_bar_validate_rejects_bad():
    with pytest.raises(ValueError):
        Bar(time_utc=utc(2024, 1, 15, 14, 30), open=100, high=90,
            low=99, close=100).validate()


def test_bucket_start():
    assert bucket_start_utc(utc(2024, 1, 15, 14, 37), 5) == utc(2024, 1, 15, 14, 35)
    assert bucket_start_utc(utc(2024, 1, 15, 14, 37), 15) == utc(2024, 1, 15, 14, 30)


def test_resample_completed_only():
    bars = [_m1(14, 30 + i) for i in range(12)]
    m5 = resample(bars, 5)
    # Buckets 14:30, 14:35 complete once 14:40 seen; 14:40 trailing dropped.
    assert [b.time_utc for b in m5] == [utc(2024, 1, 15, 14, 30),
                                       utc(2024, 1, 15, 14, 35)]
    assert m5[0].open == 100.0 and m5[0].close == 100.5


def test_resample_ohlc_aggregation():
    bars = [_m1(14, 30 + i, high=100 + i, low=100 - i) for i in range(5)]
    (m5,) = [b for b in resample(bars + [_m1(14, 35)], 5)]
    assert m5.high == 104 and m5.low == 96


def test_sorted_unique_dedupes_identical():
    b = _m1(14, 30)
    assert ensure_sorted_unique([b, b]) == [b]


def test_sorted_unique_rejects_conflict():
    with pytest.raises(ValueError):
        ensure_sorted_unique([_m1(14, 30), _m1(14, 30, close=101.0)])


def test_check_contiguous_finds_gap():
    bars = [_m1(14, 30), _m1(14, 33)]
    gaps = check_contiguous(bars)
    assert len(gaps) == 1 and "2 bar(s) missing" in gaps[0]


# --- indicators ---

def test_ema_mt5_convention():
    # SMA(1,2,3)=2.0 seeds; alpha=0.5 for period 3.
    assert ema([1.0, 2.0, 3.0, 4.0], 3) == [None, None, 2.0, 3.0]


def test_ema_insufficient_history():
    assert ema([1.0, 2.0], 5) == [None, None]


def test_atr_wilder_convention():
    out = atr_series([10, 11, 12, 13], [9, 10, 11, 12],
                     [10, 10.5, 11, 12], 3)
    assert out[0] is None and out[1] is None
    assert out[2] == pytest.approx((1 + 1 + 1.5) / 3)
