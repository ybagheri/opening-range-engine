"""CSV bar loader with validation (UTC timestamps, OHLC sanity)."""

import csv
from datetime import datetime, timezone

from ..bars import Bar, ensure_sorted_unique

UTC = timezone.utc


def _parse_time(value: str) -> datetime:
    text = value.strip()
    fmts = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S",
            "%Y/%m/%d %H:%M", "%Y.%m.%d %H:%M")
    for fmt in fmts:
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=UTC)
        except ValueError:
            continue
    iso = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        raise ValueError(f"unparseable timestamp: {value!r}")
    if dt.tzinfo is None:
        raise ValueError(f"naive timestamp (UTC required): {value!r}")
    return dt.astimezone(UTC)


def load_m1_csv(path: str) -> list:
    """Load M1 bars from CSV. Required columns: time,open,high,low,close."""
    bars: list = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        needed = {"time", "open", "high", "low", "close"}
        missing = needed - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        for lineno, row in enumerate(reader, start=2):
            try:
                bar = Bar(
                    time_utc=_parse_time(row["time"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row.get("volume", 0.0) or 0.0),
                    spread=float(row.get("spread", 0.0) or 0.0),
                ).validate()
            except ValueError as exc:
                raise ValueError(f"{path}:{lineno}: {exc}")
            bars.append(bar)
    return ensure_sorted_unique(bars)
