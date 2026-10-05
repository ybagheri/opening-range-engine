"""Historical signal reconstruction (no-look-ahead replay)."""

from dataclasses import dataclass, field

from .bars import resample
from .bias import bias_from_m1
from .config import Bias
from .data.schema import SignalRecord
from .indicators import atr_last, atr_series
from .ny_time import TRADE_END_NY, TRADE_START_NY, ny_date, to_ny
from .session import build_opening_range, check_or_size
from .signals import (
    build_trade_params,
    check_daily_limits,
    is_breakout_bar,
    is_signal_bar,
    pullback_state,
    signal_bar_in_window,
)

SESSION = "NY_CASH_OPEN"


@dataclass
class DayReport:
    ny_day: object
    state: str
    reason: str | None = None
    signals: list = field(default_factory=list)


def _m5_upto(m1_bars, end_time_utc, minutes):
    win = [b for b in m1_bars if b.time_utc <= end_time_utc]
    return resample(win, minutes)


def _atr_last(m5_completed, period):
    if len(m5_completed) < period:
        return None
    return atr_last([b.high for b in m5_completed],
                    [b.low for b in m5_completed],
                    [b.close for b in m5_completed], period)
def replay_day(m1_bars, ny_day, config) -> DayReport:
    """Replay one NY day using completed bars only (strictly causal).

    The OR-size gate uses the ATR at the OR completion (strategy control);
    breakout/pullback/trigger evaluate per-bar ATR causally.
    """
    cfg = config
    or_ = build_opening_range(m1_bars, ny_day, cfg)
    if not or_.valid:
        return DayReport(ny_day, "NO_TRADE", or_.reason)
    day_m1 = sorted([b for b in m1_bars if ny_date(b.time_utc) == ny_day],
                    key=lambda b: b.time_utc)
    if len(day_m1) < 15:
        return DayReport(ny_day, "NO_TRADE", "Insufficient data")
    m1_time_to_idx = {b.time_utc: i for i, b in enumerate(m1_bars)}
    atr_m5 = _atr_last(_m5_upto(m1_bars, day_m1[14].time_utc,
                               cfg.setup_timeframe_minutes), cfg.atr_period)
    ok, reason = check_or_size(or_, atr_m5, cfg)
    if not ok:
        return DayReport(ny_day, "NO_TRADE", reason)
    m5_hist = _m5_upto(m1_bars, day_m1[-1].time_utc,
                       cfg.setup_timeframe_minutes)
    atr_hist = atr_series([b.high for b in m5_hist],
                          [b.low for b in m5_hist],
                          [b.close for b in m5_hist], cfg.atr_period)
    m5_idx = [i for i, b in enumerate(m5_hist)
              if ny_date(b.time_utc) == ny_day and TRADE_START_NY
              <= to_ny(b.time_utc).time().replace(second=0, microsecond=0)
              < TRADE_END_NY]
    if not m5_idx:
        return DayReport(ny_day, "NO_TRADE",
                         "Signal not confirmed before window close")
    signals: list = []
    used: set = set()
    last_reason = "Signal not confirmed before window close"
    for bi in m5_idx:
        m5b = m5_hist[bi]
        atr_now = atr_hist[bi]
        if atr_now is None:
            last_reason = "Insufficient data"
            continue
        ok_s, r_s = (True, None)
        if False:  # per-bar OR re-gate removed: OR size is a session-level
            pass  # gate evaluated once at OR completion (strategy control).
        gi = m1_time_to_idx.get(m5b.time_utc)
        if gi is None:
            last_reason = "Insufficient data"
            continue
        bias, _ = bias_from_m1(m1_bars, gi, cfg)
        if bias == Bias.NEUTRAL:
            last_reason = "Neutral M15 bias"
            continue
        bo, r_bo = is_breakout_bar(m5b, or_.high, or_.low, bias,
                                   atr_now, cfg)
        if bo is None:
            if r_bo is not None:
                last_reason = r_bo
            continue
        # Causal pullback scan: grow the post-breakout window one
        # completed M5 bar at a time (same-day bars only).
        confirmed_at = None
        extreme = None
        for pi in range(bi + 1, len(m5_hist)):
            if ny_date(m5_hist[pi].time_utc) != ny_day:
                break
            window = m5_hist[bi + 1:pi + 1]
            state, ext = pullback_state(window, bo.direction, bo.level,
                                        atr_now, cfg)
            if state == "INVALIDATED":
                last_reason = "Pullback invalidated"
                break
            if state == "CONFIRMED":
                # Re-anchor the extreme to bars at/after the touch so a
                # stale breakout-bar extreme cannot inflate the stop.
                touch = None
                for b in window:
                    if bo.direction == "BULLISH":
                        band = bo.level + cfg.pullback_upper_atr * atr_now
                        if b.low <= band:
                            touch = b
                            break
                    else:
                        band = bo.level - cfg.pullback_upper_atr * atr_now
                        if b.high >= band:
                            touch = b
                            break
                if touch is not None:
                    tail = window[window.index(touch):]
                    if bo.direction == "BULLISH":
                        ext = min(b.low for b in tail)
                    else:
                        ext = max(b.high for b in tail)
                confirmed_at, extreme = pi, ext
                break
        if confirmed_at is None:
            if last_reason == "Signal not confirmed before window close":
                pass
            elif last_reason.startswith("Pullback"):
                pass
            else:
                last_reason = "Signal not confirmed before window close"
            continue
        # Causal M1 trigger scan after the confirming M5 bar.
        m1_after = [b for b in day_m1
                    if b.time_utc > m5_hist[confirmed_at].time_utc]
        for k in range(1, len(m1_after)):
            prev_b, sig_b = m1_after[k - 1], m1_after[k]
            if not signal_bar_in_window(sig_b):
                if (to_ny(sig_b.time_utc).time().replace(
                        second=0, microsecond=0) >= TRADE_END_NY):
                    break
                continue
            if not is_signal_bar(sig_b, prev_b, bo.direction,
                                 or_.high, or_.low):
                continue
            ok_d, r_d = check_daily_limits(len(signals), 0.0,
                                           bo.direction in used, cfg)
            if not ok_d:
                return DayReport(ny_day, "NO_TRADE", r_d, signals)
            tp, r_t = build_trade_params(bo.direction, sig_b, extreme,
                                         atr_now, cfg)
            if tp is None:
                last_reason = r_t
                continue
            gi2 = m1_time_to_idx.get(sig_b.time_utc)
            ef = es = None
            if gi2 is not None:
                _, info = bias_from_m1(m1_bars, gi2, cfg)
                ef, es = info.get("ema_fast"), info.get("ema_slow")
            signals.append(SignalRecord(
                date=str(ny_day), signal_time_utc=sig_b.time_utc.isoformat(),
                symbol=cfg.symbol, direction=bo.direction, session=SESSION,
                or_high=or_.high, or_low=or_.low, or_size=or_.size,
                atr_m5=atr_now, m15_ema_fast=ef, m15_ema_slow=es,
                entry=tp.entry, stop=tp.stop, take_profit=tp.take_profit,
                risk_distance=tp.risk_distance, r_multiple=tp.r_multiple,
                spread_at_signal=sig_b.spread,
                commission=cfg.commission_per_lot,
                slippage_points=cfg.slippage_points))
            used.add(bo.direction)
            return DayReport(ny_day, "SIGNAL_CONFIRMED", None, signals)
    if signals:
        return DayReport(ny_day, "SIGNAL_CONFIRMED", None, signals)
    return DayReport(ny_day, "NO_TRADE", last_reason)


def replay_all(m1_bars, config) -> tuple:
    """Replay every NY day present in the data, in time order."""
    days = sorted({ny_date(b.time_utc) for b in m1_bars})
    reports = [replay_day(m1_bars, d, config) for d in days]
    signals = [s for r in reports for s in r.signals]
    return reports, signals

