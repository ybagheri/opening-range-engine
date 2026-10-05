"""Technical indicators computed on completed bars only.

EMA follows the MetaTrader 5 convention: the first value is the SMA
of the first ``period`` values, then
``EMA[i] = alpha * price[i] + (1 - alpha) * EMA[i-1]`` with
``alpha = 2 / (period + 1)``.

ATR follows the MetaTrader 5 (Wilder) convention:
``TR[i] = max(H-L, |H-C[i-1]|, |L-C[i-1]|)``, the first ATR is the
SMA of the first ``period`` TR values, then
``ATR[i] = (ATR[i-1] * (period - 1) + TR[i]) / period``.

Both functions return ``None`` until the indicator is defined, so
callers can never read a value computed from insufficient history.
"""

from typing import Sequence


def sma(values: Sequence[float], period: int) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    out: list[float | None] = []
    window: list[float] = []
    total = 0.0
    for value in values:
        window.append(value)
        total += value
        if len(window) > period:
            total -= window.pop(0)
        out.append(total / len(window) if len(window) == period else None)
    return out


def ema(values: Sequence[float], period: int) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    alpha = 2.0 / (period + 1)
    first = sum(values[:period]) / period
    out[period - 1] = first
    prev = first
    for i in range(period, len(values)):
        prev = alpha * values[i] + (1.0 - alpha) * prev
        out[i] = prev
    return out


def ema_last(values: Sequence[float], period: int) -> float | None:
    """Last defined EMA value (or None if undefined)."""
    series = ema(values, period)
    return series[-1] if series else None


def true_range(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float]
) -> list[float]:
    if not (len(highs) == len(lows) == len(closes)):
        raise ValueError("highs/lows/closes must have equal length")
    tr: list[float] = []
    for i in range(len(highs)):
        hl = highs[i] - lows[i]
        if i == 0:
            tr.append(hl)
        else:
            hc = abs(highs[i] - closes[i - 1])
            lc = abs(lows[i] - closes[i - 1])
            tr.append(max(hl, hc, lc))
    return tr


def atr_series(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
    period: int,
) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    tr = true_range(highs, lows, closes)
    out: list[float | None] = [None] * len(tr)
    if len(tr) < period:
        return out
    first = sum(tr[:period]) / period
    out[period - 1] = first
    prev = first
    for i in range(period, len(tr)):
        prev = (prev * (period - 1) + tr[i]) / period
        out[i] = prev
    return out


def atr_last(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
    period: int,
) -> float | None:
    """Last defined ATR value (or None if undefined)."""
    series = atr_series(highs, lows, closes, period)
    return series[-1] if series else None
