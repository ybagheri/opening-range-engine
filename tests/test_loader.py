"""Loader tests: broker/MT5 export format handling."""

import csv

import pytest

from engine.data.loader import load_m1_csv


def _write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    return str(path)


def test_loads_lowercase_headers(tmp_path):
    p = _write(tmp_path / "a.csv",
               ["time", "open", "high", "low", "close", "volume", "spread"],
               [["2024-01-15 14:30", "100.0", "101.0", "99.0",
                 "100.5", "12", "3"]])
    (bar,) = load_m1_csv(p)
    assert bar.volume == 12.0
    assert bar.spread == 3.0


def test_loads_mt5_export_format(tmp_path):
    # MT5 native export: capitalized headers, dot date format,
    # TickVolume/RealVolume instead of volume.
    p = _write(tmp_path / "mt5.csv",
               ["Time", "Open", "High", "Low", "Close",
                "TickVolume", "RealVolume", "Spread"],
               [["2026.08.14 01:02:00", "53909.40000", "53909.40000",
                 "53884.60000", "53897.00000", "37", "0", "38"]])
    (bar,) = load_m1_csv(p)
    assert bar.volume == 37.0
    assert bar.spread == 38.0
    assert bar.time_utc.year == 2026
    assert bar.time_utc.month == 8
    assert bar.time_utc.day == 14
    assert bar.time_utc.hour == 1
    assert bar.time_utc.minute == 2


def test_loads_slash_date_with_seconds(tmp_path):
    p = _write(tmp_path / "b.csv",
               ["time", "open", "high", "low", "close"],
               [["2024/01/15 14:30:45", "100.0", "101.0",
                 "99.0", "100.5"]])
    (bar,) = load_m1_csv(p)
    assert bar.time_utc.second == 45


def test_missing_columns_still_rejected(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("Time,Open,High,Low\n2026.08.14 01:02:00,1,2,1\n",
                 encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        load_m1_csv(str(p))


def test_header_whitespace_tolerated(tmp_path):
    p = _write(tmp_path / "ws.csv",
               [" time ", " open", "high", "low", "close"],
               [["2024-01-15 14:30", "100.0", "101.0",
                 "99.0", "100.5"]])
    assert len(load_m1_csv(p)) == 1


def test_mt5_volume_absent_defaults_zero(tmp_path):
    p = _write(tmp_path / "c.csv",
               ["Time", "Open", "High", "Low", "Close"],
               [["2026.08.14 01:02:00", "53909.4", "53910.0",
                 "53900.0", "53905.0"]])
    (bar,) = load_m1_csv(p)
    assert bar.volume == 0.0
    assert bar.spread == 0.0
