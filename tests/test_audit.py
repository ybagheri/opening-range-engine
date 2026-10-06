"""Phase 4 tests: audit detects every injected defect class."""

from datetime import datetime, timezone

import pytest

from engine.bars import Bar
from engine.data.synthetic import generate_m1
from engine.quality.audit import audit_bars, render_report

UTC = timezone.utc


def _clean():
    return generate_m1(seed=42, days=3)


def _checks(report):
    return {(f.check, f.severity) for f in report.findings}


def test_clean_synthetic_passes():
    report = audit_bars(_clean())
    assert report.passed() and report.n_errors == 0


def _bar_at_ny(bars, hhmm):
    from engine.ny_time import to_ny
    return next(b for b in bars
                if to_ny(b.time_utc).strftime("%H:%M") == hhmm)


def test_gap_detected():
    # A gap INSIDE the trade window is signal-relevant: ERROR.
    bars = _clean()
    doomed = [b for b in bars
              if b.time_utc not in
              (_bar_at_ny(bars, "10:00").time_utc,
               _bar_at_ny(bars, "10:01").time_utc,
               _bar_at_ny(bars, "10:02").time_utc)]
    report = audit_bars(doomed)
    assert not report.passed()
    assert any(f.check == "gaps" and f.severity == "ERROR"
               for f in report.findings)


def test_overnight_gap_is_warning():
    # A gap outside the signal windows is disclosed, never fatal.
    bars = _clean()
    doomed = [b for b in bars
              if b.time_utc != _bar_at_ny(bars, "02:00").time_utc]
    report = audit_bars(doomed)
    assert report.passed()
    assert any(f.check == "gaps" and f.severity == "WARNING"
               for f in report.findings)


def test_scheduled_daily_break_is_info():
    from datetime import timedelta
    from engine.bars import Bar
    bars = []
    for day in range(3):          # Mon-Wed, January (EST)
        base = datetime(2024, 1, 8 + day, tzinfo=UTC)
        for minute in range(9 * 60, 19 * 60 + 59):   # 09:00-19:58 NY
            t = base + timedelta(hours=5, minutes=minute)
            bars.append(Bar(time_utc=t, open=100.0, high=101.0,
                            low=99.0, close=100.0))
        for minute in range(21 * 60 + 1, 21 * 60 + 6):  # 21:01-21:05 NY
            t = base + timedelta(hours=5, minutes=minute)
            bars.append(Bar(time_utc=t, open=100.0, high=101.0,
                            low=99.0, close=100.0))
    report = audit_bars(bars)
    assert report.passed()
    scheduled = [f for f in report.findings
                 if f.check == "gaps" and f.severity == "INFO"
                 and "scheduled daily break" in f.detail]
    assert len(scheduled) == 3


def test_trade_window_gap_errors():
    bars = _clean()
    doomed = [b for b in bars
              if b.time_utc != _bar_at_ny(bars, "10:30").time_utc]
    report = audit_bars(doomed)
    assert not report.passed()
    assert any(f.check == "trade_coverage" and f.severity == "ERROR"
               for f in report.findings)


def test_partial_final_day_warns():
    bars = _clean()
    cutoff = _bar_at_ny(bars, "10:00").time_utc
    partial = [b for b in bars if b.time_utc <= cutoff]
    report = audit_bars(partial)
    assert report.passed()
    assert any(f.check == "trade_coverage" and f.severity == "WARNING"
               for f in report.findings)


def test_conflicting_duplicate_detected():
    bars = _clean()
    dup = Bar(time_utc=bars[50].time_utc, open=1.0, high=2.0,
              low=0.5, close=1.5)
    report = audit_bars(bars + [dup])
    assert any(f.check == "duplicates" and f.severity == "ERROR"
               for f in report.findings)


def test_ohlc_violation_detected():
    bars = _clean()
    bad = Bar(time_utc=bars[60].time_utc, open=100.0, high=90.0,
              low=80.0, close=85.0)
    doomed = [b for i, b in enumerate(bars) if i != 60] + [bad]
    report = audit_bars(doomed)
    assert any(f.check == "ohlc" and f.severity == "ERROR"
               for f in report.findings)


def test_out_of_order_detected():
    bars = _clean()
    doomed = list(bars)
    doomed[70], doomed[71] = doomed[71], doomed[70]
    report = audit_bars(doomed)
    assert any(f.check == "ordering" and f.severity == "ERROR"
               for f in report.findings)


def test_or_window_gap_warns():
    from engine.ny_time import ny_date, to_ny
    bars = _clean()
    or_bar = next(b for b in bars
                  if to_ny(b.time_utc).strftime("%H:%M") == "09:35")
    doomed = [b for b in bars if b.time_utc != or_bar.time_utc]
    report = audit_bars(doomed)
    assert any(f.check == "or_coverage" and f.severity == "WARNING"
               for f in report.findings)


def test_dst_agreement_logged():
    report = audit_bars(_clean())
    assert any(f.check == "dst" and f.severity == "INFO"
               for f in report.findings)


def test_render_marks_blocked_real_data():
    text = render_report(audit_bars(_clean()))
    assert "BLOCKED" in text and "PASS" in text


def test_render_real_source_executed():
    text = render_report(audit_bars(_clean()), source="real")
    assert "EXECUTED" in text and "PASS" in text
    assert "BLOCKED" not in text
