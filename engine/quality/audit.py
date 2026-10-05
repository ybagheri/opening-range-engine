"""Input data integrity audit (Phase 4).

Checks an M1 bar series for: gaps (missing bars), conflicting
duplicates, OHLC violations, non-positive prices, naive (non-UTC)
timestamps, out-of-order delivery, DST-boundary anomalies, OR-window
completeness per NY day, and session-boundary coverage. Never mutates
input; returns a structured report plus a human-readable rendering.
Real broker-data audit stays blocked until data arrives; this module is
validated on synthetic data with injected defects.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ..bars import Bar
from ..ny_time import NY_TZ, is_dst_ny_rules, ny_date, to_ny


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
    # 3. Gaps on the sorted unique timeline.
    ordered = sorted(bars, key=lambda b: (b.time_utc.isoformat(),
                                          b.open, b.high, b.low, b.close))
    step = timedelta(minutes=step_minutes)
    for prev, cur in zip(ordered, ordered[1:]):
        if cur.time_utc == prev.time_utc:
            continue
        if cur.time_utc > prev.time_utc + step:
            # Overnight/weekend session breaks are expected in day-
            # session data (synthetic covers 00:00-16:00 NY only).
            if allow_overnight_gaps and _is_session_break(prev, cur):
                findings.append(AuditFinding(
                    "gaps", "INFO",
                    f"session break between "
                    f"{prev.time_utc.isoformat()} and "
                    f"{cur.time_utc.isoformat()} (expected)"))
                continue
            missing = int((cur.time_utc - prev.time_utc
                           - step).total_seconds() // 60) + 1
            if missing < 1:
                missing = 1
            findings.append(AuditFinding(
                "gaps", "ERROR",
                f"gap: {missing} bar(s) missing between "
                f"{prev.time_utc.isoformat()} and "
                f"{cur.time_utc.isoformat()}"))
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
    # 7. Session coverage summary.
    days = sorted(by_day)
    if days:
        findings.append(AuditFinding(
            "coverage", "INFO",
            f"{n} bars across {len(days)} NY day(s), "
            f"{days[0]}..{days[-1]}"))
    return report


def render_report(report: AuditReport) -> str:
    """Human-readable rendering (also written to the report file)."""
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
    lines += [
        "",
        "Real broker-data audit: BLOCKED (no MT5 data available).",
        "Synthetic audit validates the checker only `[SYNTHETIC]`.",
    ]
    return "\n".join(lines) + "\n"
