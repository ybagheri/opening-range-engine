"""Opening Range reconstruction + validity (spec sections 4-5).

The OR window is 09:30:00-09:44:59 America/New_York, all M1 bars.
The OR is valid ONLY if all 15 M1 bars are present; missing data is
never filled and yields NO TRADE for that day (assumption A7).
"""

from dataclasses import dataclass
from datetime import date, time

from .bars import Bar
from .config import StrategyConfig
from .ny_time import OR_START_NY, to_ny

# No-trade reason strings (must match spec section 14 verbatim).
REASON_OR_INCOMPLETE = "Opening Range incomplete (missing bars)"
REASON_OR_TOO_SMALL = "Opening Range too small"
REASON_OR_TOO_LARGE = "Opening Range too large"
REASON_INSUFFICIENT_DATA = "Insufficient data"


@dataclass(frozen=True)
class OpeningRange:
    """Reconstructed Opening Range for one New York trading day."""

    ny_day: date
    high: float
    low: float
    bar_count: int
    valid: bool
    reason: str | None = None

    @property
    def size(self) -> float:
        return self.high - self.low


def m1_bars_for_or_window(m1_bars: list[Bar], ny_day: date) -> list[Bar]:
    """M1 bars whose New York date == ny_day and time in [09:30, 09:45)."""
    out: list[Bar] = []
    start = time(9, 30)
    end = time(9, 45)
    for bar in m1_bars:
        ny = to_ny(bar.time_utc)
        if ny.date() != ny_day:
            continue
        if start <= ny.time().replace(second=0, microsecond=0) < end:
            out.append(bar)
    return sorted(out, key=lambda b: b.time_utc)


def build_opening_range(
    m1_bars: list[Bar], ny_day: date, config: StrategyConfig | None = None
) -> OpeningRange:
    """Reconstruct the OR for ``ny_day`` from M1 bars (completed only).

    Requires exactly ``opening_range_minutes`` (default 15) distinct
    minute slots 09:30..09:44 NY. Any missing slot -> invalid with
    REASON_OR_INCOMPLETE. Never synthesises bars.
    """
    expected = (config.opening_range_minutes if config else 15)
    window = m1_bars_for_or_window(m1_bars, ny_day)
    # Distinct NY minute slots present.
    slots = sorted(
        {to_ny(b.time_utc).time().replace(second=0, microsecond=0) for b in window}
    )
    if len(window) != expected or len(slots) != expected:
        return OpeningRange(
            ny_day=ny_day,
            high=max((b.high for b in window), default=0.0),
            low=min((b.low for b in window), default=0.0),
            bar_count=len(window),
            valid=False,
            reason=REASON_OR_INCOMPLETE,
        )
    return OpeningRange(
        ny_day=ny_day,
        high=max(b.high for b in window),
        low=min(b.low for b in window),
        bar_count=len(window),
        valid=True,
        reason=None,
    )


def check_or_size(
    or_: OpeningRange, atr_m5: float | None, config: StrategyConfig
) -> tuple[bool, str | None]:
    """Apply the OR size filter (spec section 5).

    Returns (ok, reason). ``atr_m5`` of None -> (False, Insufficient data).
    """
    if not or_.valid:
        return False, or_.reason
    if atr_m5 is None or atr_m5 <= 0:
        return False, REASON_INSUFFICIENT_DATA
    size = or_.size
    if size < config.min_or_atr * atr_m5:
        return False, REASON_OR_TOO_SMALL
    if size > config.max_or_atr * atr_m5:
        return False, REASON_OR_TOO_LARGE
    return True, None
