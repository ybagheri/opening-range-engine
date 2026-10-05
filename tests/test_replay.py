"""Phase 2 tests: loader, synthetic determinism, export, replay."""

import csv
from datetime import datetime, timezone

import pytest

from engine.config import StrategyConfig
from engine.data.loader import load_m1_csv
from engine.data.schema import SIGNAL_COLUMNS, SignalRecord
from engine.data.synthetic import generate_m1
from engine.export import export_day_reports, export_signals
from engine.ny_time import ny_date
from engine.replay import replay_all, replay_day

UTC = timezone.utc
CFG = StrategyConfig()


def test_synthetic_deterministic():
    a = generate_m1(seed=42, days=5)
    b = generate_m1(seed=42, days=5)
    assert [(x.time_utc, x.open, x.high, x.low, x.close)
            for x in a] == [(x.time_utc, x.open, x.high, x.low, x.close)
                            for x in b]


def test_synthetic_seed_changes_output():
    a = generate_m1(seed=42, days=2)
    b = generate_m1(seed=7, days=2)
    assert a[100].close != b[100].close


def test_replay_emits_signals_on_synthetic():
    bars = generate_m1(seed=42, days=5)
    _, signals = replay_all(bars, CFG)
    assert len(signals) >= 1
    for sig in signals:
        assert sig.direction in ("BULLISH", "BEARISH")
        assert sig.risk_distance > 0

def test_export_byte_identical(tmp_path):
    bars = generate_m1(seed=42, days=5)
    _, signals = replay_all(bars, CFG)
    p1 = str(tmp_path / "s1.csv")
    p2 = str(tmp_path / "s2.csv")
    export_signals(signals, p1)
    export_signals(signals, p2)
    assert open(p1, "rb").read() == open(p2, "rb").read()
    with open(p1, newline="") as fh:
        header = next(csv.reader(fh))
    assert header == list(SIGNAL_COLUMNS)


def test_prefix_consistency(tmp_path):
    bars = generate_m1(seed=42, days=5)
    reports_full, _ = replay_all(bars, CFG)
    days = sorted({ny_date(b.time_utc) for b in bars})
    keep = [b for b in bars if ny_date(b.time_utc) <= days[2]]
    reports_cut, _ = replay_all(keep, CFG)
    full_map = {str(r.ny_day): (r.state, r.reason) for r in reports_full}
    for rep in reports_cut:
        # Days fully contained in the prefix keep identical outcomes.
        if str(rep.ny_day) < str(days[2]):
            assert (rep.state, rep.reason) == full_map[str(rep.ny_day)]


def test_missing_or_bar_gives_no_trade():
    bars = generate_m1(seed=42, days=5)
    days = sorted({ny_date(b.time_utc) for b in bars})
    target = days[2]
    day_bars = [b for b in bars if ny_date(b.time_utc) == target]
    doomed = [b for b in bars if b.time_utc != day_bars[572].time_utc]
    rep = replay_day(doomed, target, CFG)
    assert rep.state == "NO_TRADE"
    assert rep.reason == "Opening Range incomplete (missing bars)"
    assert rep.signals == []


def test_loader_roundtrip_and_rejects(tmp_path):
    bars = generate_m1(seed=42, days=2)
    p = tmp_path / "m1.csv"
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["time", "open", "high", "low", "close",
                    "volume", "spread"])
        for b in bars[:60]:
            w.writerow([b.time_utc.isoformat(), b.open, b.high,
                        b.low, b.close, b.volume, b.spread])
    loaded = load_m1_csv(str(p))
    assert len(loaded) == 60
    assert loaded[0].time_utc == bars[0].time_utc
    bad = tmp_path / "bad.csv"
    bad.write_text("time,open,high,low\n2024-01-08 05:00,1,2,1\n")
    with pytest.raises(ValueError):
        load_m1_csv(str(bad))


def test_day_reports_export(tmp_path):
    bars = generate_m1(seed=42, days=5)
    reports, _ = replay_all(bars, CFG)
    p = str(tmp_path / "days.csv")
    export_day_reports(reports, p)
    with open(p, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == len(reports)
    assert set(rows[0].keys()) == {"date", "state", "reason", "n_signals"}


def test_signal_record_schema_roundtrip():
    bars = generate_m1(seed=42, days=5)
    _, signals = replay_all(bars, CFG)
    row = dict(zip(SIGNAL_COLUMNS,
                   [str(v) if v is not None else ""
                    for v in signals[0].to_row()]))
    back = SignalRecord.from_row(row)
    assert back.entry == signals[0].entry
    assert back.direction == signals[0].direction

