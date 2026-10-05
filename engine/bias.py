"""M15 market bias (spec section 6).

Uses EMA(20) and EMA(50) on M15, completed candles only.

- BULLISH: EMA20 > EMA50 AND Close(M15) > EMA20
  AND EMA20[current] > EMA20[previous].
- BEARISH: mirrored.
- Otherwise NEUTRAL -> NO TRADE (Neutral M15 bias).
"""

from .bars import Bar, resample
from .config import Bias, StrategyConfig
from .indicators import ema

REASON_NEUTRAL_BIAS = "Neutral M15 bias"
REASON_INSUFFICIENT_DATA = "Insufficient data"


def compute_bias(
    m15_closes: list[float],
    ema_fast_period: int,
    ema_slow_period: int,
) -> tuple[Bias, dict]:
    """Compute bias from a series of completed M15 closes.

    Returns (bias, debug_info). Insufficient history -> (NEUTRAL, ...).
    Needs at least ema_slow + 1 values so EMA20 slope can be evaluated.
    """
    info: dict = {"ema_fast": None, "ema_slow": None, "ema_fast_prev": None}
    if len(m15_closes) < ema_slow_period + 1:
        return Bias.NEUTRAL, info
    fast = ema(m15_closes, ema_fast_period)
    slow = ema(m15_closes, ema_slow_period)
    ef, ef_prev, es = fast[-1], fast[-2], slow[-1]
    info.update({"ema_fast": ef, "ema_slow": es, "ema_fast_prev": ef_prev})
    if ef is None or ef_prev is None or es is None:
        return Bias.NEUTRAL, info
    close = m15_closes[-1]
    if ef > es and close > ef and ef > ef_prev:
        return Bias.BULLISH, info
    if ef < es and close < ef and ef < ef_prev:
        return Bias.BEARISH, info
    return Bias.NEUTRAL, info


def bias_from_m1(m1_bars: list[Bar], upto_index: int, config: StrategyConfig) -> tuple[Bias, dict]:
    """Bias using only M1 bars with index <= upto_index (no look-ahead).

    Resamples M1[0..upto_index] into completed M15 buckets and evaluates
    compute_bias on the resulting closes. Trailing partial buckets are
    dropped by resample(), so only completed M15 candles are used.
    """
    window = m1_bars[: upto_index + 1] if upto_index >= 0 else []
    m15 = resample(window, config.context_timeframe_minutes)
    closes = [b.close for b in m15]
    bias, info = compute_bias(closes, config.ema_fast, config.ema_slow)
    info["m15_bars"] = len(m15)
    if len(m15) < config.ema_slow + 1:
        info["reason"] = REASON_INSUFFICIENT_DATA
    elif bias == Bias.NEUTRAL:
        info["reason"] = REASON_NEUTRAL_BIAS
    else:
        info["reason"] = None
    return bias, info
