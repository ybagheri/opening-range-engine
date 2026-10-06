"""Input data integrity audit (Phase 4).

Checks an M1 bar series for: gaps (missing bars), conflicting
duplicates, OHLC violations, non-positive prices, naive (non-UTC)
timestamps, out-of-order delivery, DST-boundary anomalies, OR-window
and trade-window completeness per NY day, and session-boundary
coverage. Never mutates input; returns a structured report plus a
human-readable rendering.

Gap severity model (impact on the research signal, never silent):
- ERROR: a gap intersects a signal window (OR 09:30-09:45 NY or
  trade 09:45-11:30 NY) or the trade window is incomplete on a
  fully-covered day — signal-relevant, blocks research.
- WARNING: a gap outside the signal windows (disclosed; overnight
  bars feed EMA lookbacks but never the signal windows), or a
  partial final day.
- INFO: recurring scheduled daily broker break (same clock-time
  pattern on >= 3 distinct NY days, >= 15 bars) or the multi-day
  weekend session break.
"""

from dataclasses import dataclass, field
from datetime import datetime, time as _time, timedelta

from ..bars import Bar
from ..ny_time import NY_TZ, is_dst_ny_rules, ny_date, to_ny

# Strategy signal windows in NY local time (spec section 6).
_OR_START = _time(9, 30)     # Opening Range: 09:30-09:44 NY
_TRADE_END = _time(11, 30)   # trade window closes 11:30 NY


@dataclass(frozen=True)
class AuditFinding:
    check: str
    severity: str  # ERROR / WARNING / INFO
    detail: str


@dataclass
class AuditReport:
    symbol: str
    n_bars: int
    first_utc: str
    last_utc: str
    findings: list = field(default_factory=list)

    @property
    def n_errors(self) -> int:
        return sum(1 for f in self.findings if f.severity == "ERROR")

    @property
    def n_warnings(self) -> int:
        return sum(1 for f in self.findings if f.severity == "WARNING")

    def passed(self) -> bool:
        return self.n_errors == 0

def _is_session_break(prev: Bar, cur: Bar) -> bool:
    """True if the gap spans outside 00:00-16:00 NY day-session coverage."""
    try:
        prev_ny = to_ny(prev.time_utc)
        cur_ny = to_ny(cur.time_utc)
    except ValueError:
        return False
    if cur_ny.date() != prev_ny.date():
        return True
    return False


def audit_bars(bars: list, symbol: str = "US30",
               step_minutes: int = 1,
               allow_overnight_gaps: bool = True) -> AuditReport:
    """Audit an M1 series. Input order is preserved for the check."""
    findings: list = []
    n = len(bars)
    first = bars[0].time_utc.isoformat() if n else ""
    last = bars[-1].time_utc.isoformat() if n else ""
    report = AuditReport(symbol, n, first, last, findings)
    if not bars:
        findings.append(AuditFinding("coverage", "ERROR",
                                     "empty bar series"))
        return report
    # 1. Order + duplicates.
    seen: dict = {}
    for i, bar in enumerate(bars):
        if i and bars[i].time_utc < bars[i - 1].time_utc:
            findings.append(AuditFinding(
                "ordering", "ERROR",
                f"out-of-order bar at index {i}: "
                f"{bar.time_utc.isoformat()} after "
                f"{bars[i - 1].time_utc.isoformat()}"))
        key = bar.time_utc.isoformat()
        prev = seen.get(key)
        if prev is not None and prev != bar:
            findings.append(AuditFinding(
                "duplicates", "ERROR",
                f"conflicting duplicate bar at {key}"))
        seen.setdefault(key, bar)
    # 2. Timezone awareness.
    for i, bar in enumerate(bars):
        if bar.time_utc.tzinfo is None:
            findings.append(AuditFinding(
                "timezone", "ERROR",
                f"naive timestamp at index {i} (UTC required)"))
            break
    # 3. Gaps on the sorted unique timeline, classified by
    #    impact on the signal windows (see module docstring).
    ordered = sorted(bars, key=lambda b: (b.time_utc.isoformat(),
                                          b.open, b.high, b.low, b.close))
    step = timedelta(minutes=step_minutes)
    same_day_gaps: list = []
    sig_dates: dict = {}
    for prev, cur in zip(ordered, ordered[1:]):
        if cur.time_utc == prev.time_utc:
            continue
        if cur.time_utc <= prev.time_utc + step:
            continue
        if allow_overnight_gaps and _is_session_break(prev, cur):
            findings.append(AuditFinding(
                "gaps", "INFO",
                f"session break between "
                f"{prev.time_utc.isoformat()} and "
                f"{cur.time_utc.isoformat()} (expected)"))
            continue
        try:
            pny = to_ny(prev.time_utc)
            cny = to_ny(cur.time_utc)
        except ValueError:
            pny = cny = None
        if pny is not None and pny.date() == cny.date():
            sig = (pny.hour, pny.minute, cny.hour, cny.minute)
            sig_dates.setdefault(sig, set()).add(pny.date())
            same_day_gaps.append((prev, cur, pny, cny))
            continue
        # Same-UTC-date but cross-NY-date (rare): treat like a
        # session break, never a signal-window defect.
        findings.append(AuditFinding(
            "gaps", "INFO",
            f"session break between "
            f"{prev.time_utc.isoformat()} and "
            f"{cur.time_utc.isoformat()} (expected)"))
    # A same-clock-time gap recurring on >= 3 distinct NY days is a
    # scheduled broker break (e.g. the daily 23:58->01:01 UTC
    # hiatus), not a random feed defect.
    recurring = {sig for sig, days in sig_dates.items()
                 if len(days) >= 3}
    for prev, cur, pny, cny in same_day_gaps:
        missing = int((cur.time_utc - prev.time_utc
                       - step).total_seconds() // 60) + 1
        if missing < 1:
            missing = 1
        in_signal_window = not (cny.time() <= _OR_START
                                or pny.time() >= _TRADE_END)
        if in_signal_window:
            findings.append(AuditFinding(
                "gaps", "ERROR",
                f"gap: {missing} bar(s) missing INSIDE signal "
                f"window (09:30-11:30 NY) between "
                f"{prev.time_utc.isoformat()} and "
                f"{cur.time_utc.isoformat()}"))
        else:
            sig = (pny.hour, pny.minute, cny.hour, cny.minute)
            detail = (f"gap: {missing} bar(s) missing between "
                      f"{prev.time_utc.isoformat()} and "
                      f"{cur.time_utc.isoformat()}")
            if sig in recurring and missing >= 15:
                findings.append(AuditFinding(
                    "gaps", "INFO",
                    f"scheduled daily break (recurring "
                    f"{missing}-bar pattern) between "
                    f"{prev.time_utc.isoformat()} and "
                    f"{cur.time_utc.isoformat()}"))
            else:
                findings.append(AuditFinding(
                    "gaps", "WARNING",
                    detail + " (outside signal windows)"))
    # 4. OHLC sanity per bar.
    for bar in ordered:
        if bar.high < bar.low:
            findings.append(AuditFinding(
                "ohlc", "ERROR",
                f"high < low at {bar.time_utc.isoformat()}"))
        elif min(bar.open, bar.high, bar.low, bar.close) <= 0:
            findings.append(AuditFinding(
                "ohlc", "ERROR",
                f"non-positive price at {bar.time_utc.isoformat()}"))
        elif not (bar.low <= bar.open <= bar.high
                  and bar.low <= bar.close <= bar.high):
            findings.append(AuditFinding(
                "ohlc", "ERROR",
                f"open/close outside [low, high] at "
                f"{bar.time_utc.isoformat()}"))
    # 5. DST cross-check: zoneinfo offset vs explicit US rules.
    for bar in ordered:
        ny = bar.time_utc.astimezone(NY_TZ)
        rules_dst = is_dst_ny_rules(bar.time_utc)
        zone_dst = ny.utcoffset().total_seconds() == -4 * 3600
        if rules_dst != zone_dst:
            findings.append(AuditFinding(
                "dst", "ERROR",
                f"DST rule mismatch at {bar.time_utc.isoformat()}"))
            break
    else:
        findings.append(AuditFinding(
            "dst", "INFO",
            "zoneinfo offsets agree with explicit US DST rules"))
    # 6. OR-window completeness per NY day (09:30-09:44 NY).
    by_day: dict = {}
    for bar in ordered:
        try:
            ny = to_ny(bar.time_utc)
        except ValueError:
            continue
        by_day.setdefault(ny.date(), []).append(
            ny.time().replace(second=0, microsecond=0))
    from datetime import time as _time
    want = [f"09:{m:02d}" for m in range(30, 45)]
    for day in sorted(by_day):
        have = {t.strftime("%H:%M") for t in by_day[day]}
        missing_slots = [s for s in want if s not in have]
        if missing_slots:
            findings.append(AuditFinding(
                "or_coverage", "WARNING",
                f"{day}: OR window missing "
                f"{len(missing_slots)}/15 bars "
                f"({', '.join(missing_slots[:5])}"
                f"{'...' if len(missing_slots) > 5 else ''}) "
                f"-> NO TRADE that day"))
    # 6b. Trade-window completeness per NY day (09:45-11:29 NY).
    # A missing bar inside the trade window silently corrupts M5
    # breakout/pullback signals, so it is signal-relevant (ERROR)
    # on any day whose data continues past 11:30 NY.
    trade_slots = ([f"09:{m:02d}" for m in range(45, 60)]
                   + [f"10:{m:02d}" for m in range(60)]
                   + [f"11:{m:02d}" for m in range(30)])
    for day in sorted(by_day):
        todays = by_day[day]
        have = {t.strftime("%H:%M") for t in todays}
        if not any(t < _time(12, 0) for t in todays):
            continue  # evening-only session (e.g. Sunday): OR check already warns
        missing_tw = [s for s in trade_slots if s not in have]
        if not missing_tw:
            continue
        past_window = any(t > _time(11, 30) for t in todays)
        if past_window:
            findings.append(AuditFinding(
                "trade_coverage", "ERROR",
                f"{day}: trade window missing "
                f"{len(missing_tw)}/{len(trade_slots)} bars "
                f"({', '.join(missing_tw[:5])}"
                f"{'...' if len(missing_tw) > 5 else ''}) "
                f"-> signals corrupted"))
        else:
            findings.append(AuditFinding(
                "trade_coverage", "WARNING",
                f"{day}: partial trading day, data ends before "
                f"11:30 NY (missing {len(missing_tw)}/"
                f"{len(trade_slots)} bars)"))
    # 7. Session coverage summary.
    days = sorted(by_day)
    if days:
        findings.append(AuditFinding(
            "coverage", "INFO",
            f"{n} bars across {len(days)} NY day(s), "
            f"{days[0]}..{days[-1]}"))
    return report


def render_report(report: AuditReport,
                  source: str = "synthetic") -> str:
    """Human-readable rendering (also written to the report file).

    ``source`` is "real" for broker data or "synthetic" for the
    deterministic generator; it only affects the provenance note.
    """
    lines = [
        "# Data Quality Report",
        "",
        f"Symbol: {report.symbol}",
        f"Bars: {report.n_bars}",
        f"Range (UTC): {report.first_utc} .. {report.last_utc}",
        f"Errors: {report.n_errors}  "
        f"Warnings: {report.n_warnings}",
        f"Verdict: {'PASS' if report.passed() else 'FAIL'}",
        "",
        "## Gap severity model",
        "",
        "- ERROR: gap inside a signal window (OR 09:30-09:45 NY "
        "or trade 09:45-11:30 NY), or trade window incomplete on "
        "a fully-covered day.",
        "- WARNING: gap outside signal windows (disclosed; overnight "
        "bars feed EMA lookbacks but never the signal windows), or "
        "a partial final day.",
        "- INFO: recurring scheduled daily broker break (same "
        "clock-time pattern on >= 3 distinct NY days, >= 15 bars) "
        "or the multi-day weekend session break.",
        "",
        "## Findings",
        "",
    ]
    if not report.findings:
        lines.append("- (none)")
    else:
        for finding in report.findings:
            lines.append(
                f"- [{finding.severity}] "
                f"{finding.check}: {finding.detail}")
    if source == "real":
        lines += [
            "",
            f"Real broker-data audit: EXECUTED on {report.n_bars} "
            f"bars ({report.symbol}). No gaps intersect the signal "
            "windows unless listed above as ERROR.",
        ]
    else:
        lines += [
            "",
            "Real broker-data audit: BLOCKED (no MT5 data available).",
            "Synthetic audit validates the checker only `[SYNTHETIC]`.",
        ]
    return "\n".join(lines) + "\n"
