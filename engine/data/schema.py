"""Record schemas: CSV column contracts for signals."""

from dataclasses import dataclass

SIGNAL_COLUMNS: tuple = (
    "date", "signal_time_utc", "symbol", "direction", "session",
    "or_high", "or_low", "or_size", "atr_m5",
    "m15_ema_fast", "m15_ema_slow",
    "entry", "stop", "take_profit",
    "risk_distance", "r_multiple",
    "spread_at_signal", "commission", "slippage_points",
)


@dataclass(frozen=True)
class SignalRecord:
    date: str
    signal_time_utc: str
    symbol: str
    direction: str
    session: str
    or_high: float
    or_low: float
    or_size: float
    atr_m5: float
    m15_ema_fast: float | None
    m15_ema_slow: float | None
    entry: float
    stop: float
    take_profit: float
    risk_distance: float
    r_multiple: float
    spread_at_signal: float
    commission: float
    slippage_points: int

    def to_row(self) -> list:
        return [getattr(self, c) for c in SIGNAL_COLUMNS]

    @classmethod
    def from_row(cls, row: dict) -> "SignalRecord":
        num = ("or_high", "or_low", "or_size", "atr_m5", "entry",
               "stop", "take_profit", "risk_distance", "r_multiple",
               "spread_at_signal", "commission")
        conv = dict(row)
        for k in num:
            conv[k] = float(conv[k])
        for k in ("m15_ema_fast", "m15_ema_slow"):
            conv[k] = None if conv[k] in (None, "") else float(conv[k])
        conv["slippage_points"] = int(float(conv["slippage_points"]))
        for k in ("date", "signal_time_utc", "symbol", "direction", "session"):
            conv[k] = str(conv[k])
        return cls(**{c: conv[c] for c in SIGNAL_COLUMNS})
