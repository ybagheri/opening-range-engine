"""Trade record schema (spec section 17: minimum trade record)."""

from dataclasses import dataclass

TRADE_COLUMNS: tuple = (
    "date", "signal_time_utc", "direction", "session",
    "or_high", "or_low", "or_size", "atr_m5",
    "entry", "stop", "take_profit", "risk_distance", "r_multiple",
    "spread_at_signal", "commission", "slippage_points",
    "fill_price", "exit", "exit_time_utc", "result", "r_result",
    "mae_r", "mfe_r", "bars_held",
)


@dataclass(frozen=True)
class TradeRecord:
    date: str
    signal_time_utc: str
    direction: str
    session: str
    or_high: float
    or_low: float
    or_size: float
    atr_m5: float
    entry: float
    stop: float
    take_profit: float
    risk_distance: float
    r_multiple: float
    spread_at_signal: float
    commission: float
    slippage_points: int
    fill_price: float
    exit: float | None
    exit_time_utc: str | None
    result: str
    r_result: float
    mae_r: float
    mfe_r: float
    bars_held: int

    def to_row(self) -> list:
        return [getattr(self, c) for c in TRADE_COLUMNS]


def trade_from_signal_and_result(signal, res) -> TradeRecord:
    return TradeRecord(
        date=signal.date, signal_time_utc=signal.signal_time_utc,
        direction=signal.direction, session=signal.session,
        or_high=signal.or_high, or_low=signal.or_low,
        or_size=signal.or_size, atr_m5=signal.atr_m5,
        entry=signal.entry, stop=signal.stop,
        take_profit=signal.take_profit,
        risk_distance=signal.risk_distance,
        r_multiple=signal.r_multiple,
        spread_at_signal=signal.spread_at_signal,
        commission=signal.commission,
        slippage_points=signal.slippage_points,
        fill_price=res.fill_price, exit=res.exit,
        exit_time_utc=res.exit_time_utc, result=res.result,
        r_result=res.r_result, mae_r=res.mae_r, mfe_r=res.mfe_r,
        bars_held=res.bars_held)
