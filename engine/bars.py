"""Bar model and timeframe resampling.

The base resolution is the M1 bar. M5 and M15 bars are derived by
exact aggregation of consecutive M1 bars. Because New York is always
a whole number of hours from UTC (UTC-5 EST / UTC-4 EDT),
UTC-aligned M5/M15 bucket boundaries coincide exactly with the New
York session boundaries (09:30 / 09:45 / 11:30 NY).
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Sequence

from .ny_time import UTC


@dataclass(frozen=True)
class Bar:
    """One completed candle.

    ``time_utc`` is the bar OPEN time in UTC. ``spread`` is recorded
    in points at bar close (spec: record, never filter, in v1.0).
    """

    time_utc: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    spread: float = 0.0

    def validate(self) -> "Bar":
        if self.high < self.low:
            raise ValueError(f"high < low at {self.time_utc}")
        if self.open <= 0 or self.high <= 0 or self.low <= 0 or self.close <= 0:
            raise ValueError(f"non-positive price at {self.time_utc}")
        if not (self.low <= self.open <= self.high):
            raise ValueError(f"open outside [low, high] at {self.time_utc}")
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"close outside [low, high] at {self.time_utc}")
        return self


def bucket_start_utc(time_utc: datetime, minutes: int) -> datetime:
    """Start of the UTC-aligned aggregation bucket of width ``minutes``."""
    minute_of_day = time_utc.hour * 60 + time_utc.minute
    bucket_index = minute_of_day // minutes
    return time_utc.replace(
        hour=bucket_index * minutes // 60,
        minute=bucket_index * minutes % 60,
        second=0,
        microsecond=0,
    )


def resample(bars: Sequence[Bar], minutes: int) -> list[Bar]:
    """Aggregate M1 bars into ``minutes``-minute bars (UTC-aligned).

    Only fully-contained buckets are emitted: a bucket is emitted
    once a bar from the following bucket is seen, guaranteeing that
    every emitted bar is completed. Trailing partial buckets are
    dropped (never forward-filled).
    """
    if minutes <= 0:
        raise ValueError("minutes must be positive")
    out: list[Bar] = []
    current_start: datetime | None = None
    o = h = l = c = 0.0
    v = s = 0.0
    count = 0
    for bar in bars:
        start = bucket_start_utc(bar.time_utc, minutes)
        if current_start is None:
            current_start = start
        if start != current_start:
            # Previous bucket is now known to be complete.
            out.append(
                Bar(
                    time_utc=current_start,
                    open=o,
                    high=h,
                    low=l,
                    close=c,
                    volume=v,
                    spread=s,
                )
            )
            current_start = start
            o = h = l = c = 0.0
            v = s = 0.0
            count = 0
        if count == 0:
            o = bar.open
            h = bar.high
            l = bar.low
        else:
            h = max(h, bar.high)
            l = min(l, bar.low)
        c = bar.close
        v += bar.volume
        s = bar.spread  # spread of the bucket's last M1 bar
        count += 1
    # Trailing bucket: dropped intentionally (not known complete).
    return out


def bars_within(
    bars: Sequence[Bar], start_utc: datetime, end_utc: datetime
) -> list[Bar]:
    """Bars whose open time is in [start_utc, end_utc)."""
    return [b for b in bars if start_utc <= b.time_utc < end_utc]


def ensure_sorted_unique(bars: list[Bar]) -> list[Bar]:
    """Sort by time and drop exact-duplicate timestamps (keep first).

    Raises if duplicate timestamps carry different OHLC (corrupt data).
    """
    bars = sorted(bars, key=lambda b: b.time_utc)
    out: list[Bar] = []
    for bar in bars:
        if out and out[-1].time_utc == bar.time_utc:
            if out[-1] != bar:
                raise ValueError(
                    f"conflicting duplicate bar at {bar.time_utc}"
                )
            continue
        out.append(bar)
    return out


def check_contiguous(bars: Sequence[Bar], step_minutes: int = 1) -> list[str]:
    """Return human-readable descriptions of gaps in an M1 series."""
    gaps: list[str] = []
    step = timedelta(minutes=step_minutes)
    for prev, cur in zip(bars, bars[1:]):
        expected = prev.time_utc + step
        if cur.time_utc > expected:
            missing = int((cur.time_utc - expected).total_seconds() // 60)
            gaps.append(
                f"gap: {missing} bar(s) missing between "
                f"{prev.time_utc.isoformat()} and {cur.time_utc.isoformat()}"
            )
    return gaps
