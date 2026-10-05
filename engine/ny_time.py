"""America/New_York time handling with explicit US daylight-saving rules.

The strategy is anchored to the New York cash session. No fixed UTC
offset is hardcoded anywhere: every timestamp is converted to
America/New_York, and US DST transitions are handled both by ``zoneinfo``
(primary) and by explicit rules (cross-checked in tests).

US DST rules (current law):
- DST begins: 2nd Sunday of March at 02:00 local standard time
  (= 07:00 UTC), clocks jump to 03:00 EDT (UTC-4).
- DST ends: 1st Sunday of November at 02:00 local daylight time
  (= 06:00 UTC), clocks fall back to 01:00 EST (UTC-5).
"""

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

NY_TZ = ZoneInfo("America/New_York")
UTC = timezone.utc

# Session windows, expressed in America/New_York local time.
OR_START_NY = time(9, 30)
TRADE_START_NY = time(9, 45)
TRADE_END_NY = time(11, 30)

EST_OFFSET = timedelta(hours=-5)
EDT_OFFSET = timedelta(hours=-4)


def to_ny(utc_dt: datetime) -> datetime:
    """Convert an aware UTC datetime to America/New_York local time."""
    if utc_dt.tzinfo is None:
        raise ValueError("utc_dt must be timezone-aware (UTC)")
    return utc_dt.astimezone(NY_TZ)


def utc_now() -> datetime:
    return datetime.now(UTC)


def ny_now() -> datetime:
    return to_ny(utc_now())


def is_dst_ny(utc_dt: datetime) -> bool:
    """True if the instant is inside US daylight saving time."""
    return to_ny(utc_dt).utcoffset() == EDT_OFFSET


def ny_date(utc_dt: datetime) -> date:
    return to_ny(utc_dt).date()


def ny_time_of_day(utc_dt: datetime) -> time:
    return to_ny(utc_dt).time()


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """n-th (1-based) occurrence of weekday (0=Monday) in the month."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def us_dst_start_utc(year: int) -> datetime:
    """2nd Sunday of March, 07:00 UTC (02:00 EST -> 03:00 EDT)."""
    second_sunday_march = _nth_weekday_of_month(year, 3, 6, 2)
    return datetime.combine(second_sunday_march, time(7, 0), UTC)


def us_dst_end_utc(year: int) -> datetime:
    """1st Sunday of November, 06:00 UTC (02:00 EDT -> 01:00 EST)."""
    first_sunday_november = _nth_weekday_of_month(year, 11, 6, 1)
    return datetime.combine(first_sunday_november, time(6, 0), UTC)


def is_dst_ny_rules(utc_dt: datetime) -> bool:
    """DST flag computed from the explicit US rules (independent of zoneinfo)."""
    year = utc_dt.year
    return us_dst_start_utc(year) <= utc_dt < us_dst_end_utc(year)


def ny_offset(utc_dt: datetime) -> timedelta:
    """New York UTC offset at an instant, from the explicit rules."""
    return EDT_OFFSET if is_dst_ny_rules(utc_dt) else EST_OFFSET


def in_ny_window(utc_dt: datetime, start: time, end: time) -> bool:
    """True if the instant's New York time-of-day is in [start, end)."""
    t = ny_time_of_day(utc_dt)
    return start <= t < end


def next_ny_day_start_utc(day: date) -> datetime:
    """UTC instant of 00:00 America/New_York at the start of ``day``."""
    # 00:00 NY is 05:00 UTC in EST or 04:00 UTC in EDT. Try both
    # candidates on the same calendar day and keep the one that maps
    # back to 00:00 NY of ``day``.
    for candidate_hour in (4, 5):
        guess = datetime.combine(day, time(candidate_hour, 0), UTC)
        if to_ny(guess).date() == day and to_ny(guess).time() == time(0, 0):
            return guess
    raise ValueError(f"cannot resolve NY midnight for {day}")
