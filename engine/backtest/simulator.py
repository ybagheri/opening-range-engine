"""Stop-order fill simulator (spec sections 10-12, 18)."""

from dataclasses import dataclass

from ..bars import Bar
from ..config import StrategyConfig
from ..ny_time import TRADE_END_NY, to_ny
from .costs import CostModel


@dataclass(frozen=True)
class TradeResult:
    signal_time_utc: str
    direction: str
    entry: float
    fill_price: float
    stop: float
    take_profit: float
    risk_distance: float
    exit: float | None
    exit_time_utc: str | None
    result: str
    r_result: float
    mae_r: float
    mfe_r: float
    bars_held: int


def _ny_t(bar: Bar):
    return to_ny(bar.time_utc).time().replace(second=0, microsecond=0)


def _touches(entry: float, direction: str, bar: Bar) -> bool:
    if direction == "BULLISH":
        return bar.high >= entry
    return bar.low <= entry


def _sl_hit(stop: float, direction: str, bar: Bar) -> bool:
    if direction == "BULLISH":
        return bar.low <= stop
    return bar.high >= stop


def _tp_hit(tp: float, direction: str, bar: Bar) -> bool:
    if direction == "BULLISH":
        return bar.high >= tp
    return bar.low <= tp


def _r_pnl(direction: str, fill: float, px: float, risk: float) -> float:
    if risk <= 0:
        raise ValueError("risk_distance must be positive")
    sign = 1.0 if direction == "BULLISH" else -1.0
    return sign * (px - fill) / risk

def simulate_signal(signal, m1_bars, config: StrategyConfig,
                    costs: CostModel | None = None) -> TradeResult:
    """Simulate one signal against M1 bars after its signal bar.

    ``signal`` is a SignalRecord; ``m1_bars`` is the full day-ordered M1
    list (only bars after the signal bar are examined). Entry fills at
    the stop price plus slippage (A15); expiry 11:30 NY (DEC-005);
    same-bar SL/TP resolves SL first (DEC-004). Because slippage moves
    the fill adversely while SL/TP stay fixed, both the R outcome and
    MAE/MFE are measured from the actual fill (not the ordered price).
    Commission in price units is converted to R against risk_distance.
    """
    costs = (costs or CostModel(
        slippage_points=config.slippage_points,
        commission_per_trade=config.commission_per_lot,
        point=config.point)).validate()
    direction = signal.direction
    entry = signal.entry
    stop = signal.stop
    take_profit = signal.take_profit
    risk = signal.risk_distance
    sig_time = signal.signal_time_utc
    after = [b for b in m1_bars
             if b.time_utc.isoformat() > sig_time]
    fill = None
    fill_idx = -1
    for i, bar in enumerate(after):
        if _ny_t(bar) >= TRADE_END_NY:
            break
        if _touches(entry, direction, bar):
            fill = costs.entry_fill(entry, direction)
            fill_idx = i
            break
    if fill is None:
        return TradeResult(sig_time, direction, entry, entry, stop,
                           take_profit, risk, None, None,
                           "EXPIRED", 0.0, 0.0, 0.0, 0)
    comm_r = costs.commission_per_trade / risk if risk > 0 else 0.0
    mae = 0.0
    mfe = 0.0
    held = 0
    for bar in after[fill_idx:]:
        held += 1
        if direction == "BULLISH":
            mae = min(mae, _r_pnl(direction, fill, bar.low, risk))
            mfe = max(mfe, _r_pnl(direction, fill, bar.high, risk))
        else:
            mae = min(mae, _r_pnl(direction, fill, bar.high, risk))
            mfe = max(mfe, _r_pnl(direction, fill, bar.low, risk))
        sl = _sl_hit(stop, direction, bar)
        tp = _tp_hit(take_profit, direction, bar)
        if sl and tp:
            sl = True
            tp = False  # SL first (DEC-004)
        if sl:
            return TradeResult(sig_time, direction, entry, fill, stop,
                               take_profit, risk, stop,
                               bar.time_utc.isoformat(), "LOSS",
                               _r_pnl(direction, fill, stop, risk) - comm_r,
                               mae, mfe, held)
        if tp:
            return TradeResult(sig_time, direction, entry, fill, stop,
                               take_profit, risk, take_profit,
                               bar.time_utc.isoformat(), "WIN",
                               _r_pnl(direction, fill, take_profit, risk)
                               - comm_r, mae, mfe, held)
    return TradeResult(sig_time, direction, entry, fill, stop,
                       take_profit, risk, None, None, "EXPIRED",
                       0.0 - comm_r if held else 0.0, mae, mfe, held)


def simulate_all(signals, m1_bars, config,
                 costs: CostModel | None = None) -> list:
    """Simulate every signal in time order."""
    ordered = sorted(signals, key=lambda s: s.signal_time_utc)
    return [simulate_signal(s, m1_bars, config, costs) for s in ordered]

