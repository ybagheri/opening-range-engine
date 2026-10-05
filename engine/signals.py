"""Signal state machine (spec sections 7-11, 13-14)."""

from dataclasses import dataclass

from .bars import Bar
from .config import Bias, SignalState, StrategyConfig
from .ny_time import TRADE_END_NY, TRADE_START_NY, to_ny

REASON_NEUTRAL_BIAS = "Neutral M15 bias"
REASON_OR_TOO_LARGE = "Opening Range too large"
REASON_OR_TOO_SMALL = "Opening Range too small"
REASON_OR_INCOMPLETE = "Opening Range incomplete (missing bars)"
REASON_BREAKOUT_AFTER_WINDOW = "Breakout occurred after trading window"
REASON_BREAKOUT_EXTENSION = "Breakout extension too large"
REASON_PULLBACK_INVALIDATED = "Pullback invalidated"
REASON_STOP_TOO_LARGE = "Stop distance too large"
REASON_STOP_TOO_SMALL = "Stop distance too small"
REASON_DAILY_TRADE_LIMIT = "Daily trade limit reached"
REASON_SIGNAL_AFTER_CLOSE = "Signal not confirmed before window close"
REASON_SETUP_ACTIVE = "Same-direction setup already active"
REASON_DAILY_LOSS_LIMIT = "Daily loss limit reached"
REASON_INSUFFICIENT_DATA = "Insufficient data"

NO_TRADE_REASONS: tuple[str, ...] = (
    REASON_NEUTRAL_BIAS, REASON_OR_TOO_LARGE, REASON_OR_TOO_SMALL,
    REASON_OR_INCOMPLETE, REASON_BREAKOUT_AFTER_WINDOW,
    REASON_BREAKOUT_EXTENSION, REASON_PULLBACK_INVALIDATED,
    REASON_STOP_TOO_LARGE, REASON_STOP_TOO_SMALL,
    REASON_DAILY_TRADE_LIMIT, REASON_SIGNAL_AFTER_CLOSE,
    REASON_SETUP_ACTIVE, REASON_DAILY_LOSS_LIMIT,
    REASON_INSUFFICIENT_DATA,
)

BULLISH = "BULLISH"
BEARISH = "BEARISH"


@dataclass(frozen=True)
class Breakout:
    direction: str
    bar_time_utc: object
    close: float
    level: float
    extension: float


def _ny_open(bar: Bar):
    return to_ny(bar.time_utc)


def is_breakout_bar(m5_bar, or_high, or_low, bias, atr_m5, config):
    """One completed M5 bar -> (Breakout|None, reason|None).

    Wick-through without close beyond OR, or a bar before 09:45 NY,
    is waiting (None, None), not a rejection.
    """
    ny_open = _ny_open(m5_bar).time().replace(second=0, microsecond=0)
    if ny_open >= TRADE_END_NY:
        return None, REASON_BREAKOUT_AFTER_WINDOW
    if ny_open < TRADE_START_NY:
        return None, None
    if atr_m5 is None or atr_m5 <= 0:
        return None, REASON_INSUFFICIENT_DATA
    direction = None
    level = 0.0
    if m5_bar.close > or_high and bias == Bias.BULLISH:
        direction, level = BULLISH, or_high
    elif m5_bar.close < or_low and bias == Bias.BEARISH:
        direction, level = BEARISH, or_low
    else:
        return None, None
    extension = abs(m5_bar.close - level)
    if extension > config.max_breakout_extension_atr * atr_m5:
        return None, REASON_BREAKOUT_EXTENSION
    return (Breakout(direction=direction, bar_time_utc=m5_bar.time_utc,
                     close=m5_bar.close, level=level, extension=extension),
            None)

def pullback_state(m5_bars, direction, or_level, atr_m5, config):
    """Fold post-breakout M5 bars -> (CONFIRMED|INVALIDATED|WAITING, extreme)."""
    if direction == BULLISH:
        lower = or_level - config.pullback_lower_atr * atr_m5
        upper = or_level + config.pullback_upper_atr * atr_m5
        touched = False
        extreme = float("inf")
        for bar in m5_bars:
            if bar.close < lower:
                return "INVALIDATED", None
            if bar.low <= upper:
                touched = True
                extreme = min(extreme, bar.low)
        return ("CONFIRMED", extreme) if touched else ("WAITING", None)
    if direction == BEARISH:
        lower = or_level - config.pullback_upper_atr * atr_m5
        upper = or_level + config.pullback_lower_atr * atr_m5
        touched = False
        extreme = float("-inf")
        for bar in m5_bars:
            if bar.close > upper:
                return "INVALIDATED", None
            if bar.high >= lower:
                touched = True
                extreme = max(extreme, bar.high)
        return ("CONFIRMED", extreme) if touched else ("WAITING", None)
    raise ValueError(f"unknown direction: {direction!r}")


def is_signal_bar(m1_bar, prev_m1_bar, direction, or_high, or_low):
    """M1 entry trigger (spec section 9) on completed candles only."""
    if direction == BULLISH:
        return (m1_bar.close > m1_bar.open
                and m1_bar.close > prev_m1_bar.high
                and m1_bar.close > or_high)
    if direction == BEARISH:
        return (m1_bar.close < m1_bar.open
                and m1_bar.close < prev_m1_bar.low
                and m1_bar.close < or_low)
    raise ValueError(f"unknown direction: {direction!r}")


from dataclasses import dataclass as _dc


@_dc(frozen=True)
class TradeParams:
    direction: str
    entry: float
    stop: float
    take_profit: float
    risk_distance: float
    r_multiple: float


def build_trade_params(direction, signal_bar, pullback_extreme, atr_m5, config):
    """Entry/SL/TP from signal bar + pullback extreme (spec section 10)."""
    point = config.point
    if direction == BULLISH:
        entry = signal_bar.high + config.entry_buffer_points * point
        stop = pullback_extreme - config.stop_buffer_points * point
        sign = 1.0
    elif direction == BEARISH:
        entry = signal_bar.low - config.entry_buffer_points * point
        stop = pullback_extreme + config.stop_buffer_points * point
        sign = -1.0
    else:
        raise ValueError(f"unknown direction: {direction!r}")
    risk = abs(entry - stop)
    if risk < config.min_stop_atr * atr_m5:
        return None, REASON_STOP_TOO_SMALL
    if risk > config.max_stop_atr * atr_m5:
        return None, REASON_STOP_TOO_LARGE
    tp = entry + sign * config.tp_multiplier * risk
    return (TradeParams(direction=direction, entry=entry, stop=stop,
                        take_profit=tp, risk_distance=risk,
                        r_multiple=config.tp_multiplier), None)


def signal_bar_in_window(m1_bar):
    """True if the M1 signal bar opened inside [09:45, 11:30) NY."""
    t = _ny_open(m1_bar).time().replace(second=0, microsecond=0)
    return TRADE_START_NY <= t < TRADE_END_NY


def check_daily_limits(trades_today, day_r, setup_active_same_direction, config):
    """Daily guards (spec section 11): loss limit, trade limit, setup."""
    if day_r <= -abs(config.daily_loss_limit_r):
        return False, REASON_DAILY_LOSS_LIMIT
    if trades_today >= config.max_trades_per_day:
        return False, REASON_DAILY_TRADE_LIMIT
    if setup_active_same_direction:
        return False, REASON_SETUP_ACTIVE
    return True, None


ALL_STATES: tuple[str, ...] = tuple(s.value for s in SignalState)

