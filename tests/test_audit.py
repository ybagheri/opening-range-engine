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


def test_gap_detected():
    bars = _clean()
    doomed = [b for i, b in enumerate(bars) if i not in (100, 101, 102)]
    report = audit_bars(doomed)
    assert not report.passed()
    assert any(f.check == "gaps" and f.severity == "ERROR"
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
