"""CSV bar loader with validation (UTC timestamps, OHLC sanity)."""

import csv
from datetime import datetime, timezone

from ..bars import Bar, ensure_sorted_unique

UTC = timezone.utc


def _parse_time(value: str) -> datetime:
    text = value.strip()
    fmts = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S",
            "%Y/%m/%d %H:%M", "%Y/%m/%d %H:%M:%S",
            "%Y.%m.%d %H:%M", "%Y.%m.%d %H:%M:%S")
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


# MT5's native CSV export uses capitalized headers (Time,Open,...)
# and TickVolume/RealVolume instead of volume. Headers are matched
# case-insensitively; tick/real volume both feed Bar.volume.
_HEADER_ALIASES = {
    "tickvolume": "volume",
    "realvolume": "volume",
}


def _normalise_fieldnames(fieldnames) -> dict:
    """Map lowercase header -> actual header (first wins)."""
    mapping: dict = {}
    for name in fieldnames or []:
        key = name.strip().lower()
        key = _HEADER_ALIASES.get(key, key)
        if key not in mapping:
            mapping[key] = name
    return mapping


def load_m1_csv(path: str) -> list:
    """Load M1 bars from CSV. Required columns: time,open,high,low,close.

    Header case is ignored; ``TickVolume``/``RealVolume`` are accepted
    as ``volume`` (MT5 export format).
    """
    bars: list = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = _normalise_fieldnames(reader.fieldnames)
        needed = {"time", "open", "high", "low", "close"}
        missing = needed - set(cols)
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        for lineno, row in enumerate(reader, start=2):
            try:
                bar = Bar(
                    time_utc=_parse_time(row[cols["time"]]),
                    open=float(row[cols["open"]]),
                    high=float(row[cols["high"]]),
                    low=float(row[cols["low"]]),
                    close=float(row[cols["close"]]),
                    volume=float(row.get(cols.get("volume"), 0.0) or 0.0),
                    spread=float(row.get(cols.get("spread"), 0.0) or 0.0),
                ).validate()
            except ValueError as exc:
                raise ValueError(f"{path}:{lineno}: {exc}")
            bars.append(bar)
    return ensure_sorted_unique(bars)
