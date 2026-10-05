"""Deterministic synthetic M1 generator (pipeline validation only).

Tagged [SYNTHETIC]: never market evidence. Pure function of
(seed, days, start): same inputs -> byte-identical bars. Shaped like a
textbook trend day: quiet premarket drift (builds M15 history), tight
OR window, then a steady uptrend.
"""

import random
from datetime import datetime, timedelta, timezone

from ..bars import Bar

UTC = timezone.utc


def generate_m1(seed=42, days=5, start="2024-01-08",
                base=40000.0) -> list:
    """Generate ``days`` weekday sessions (EST January days).

    Shape: quiet premarket drift (builds M15 EMA history), tight OR
    window, steady trade-window uptrend so the pipeline emits signals
    deterministically. Each day covers 00:00-16:00 NY.
    """
    rng = random.Random(seed)
    y, m, d = (int(x) for x in start.split("-"))
    day0 = datetime(y, m, d, tzinfo=UTC)
    out: list = []
    price = base
    made = 0
    cursor = day0
    while made < days:
        if cursor.weekday() < 5:
            for i in range(960):
                if i < 570:            # 00:00-09:29 NY premarket
                    drift, wave = 0.05, 3.4
                elif i < 585:          # 09:30-09:44 NY OR window
                    drift, wave = 0.0, 0.35
                elif i < 690:          # 09:45-11:29 NY trade window
                    drift, wave = 0.06, 0.45
                else:                  # rest of day
                    drift, wave = 0.02, 0.6
                t = cursor + timedelta(hours=5) + timedelta(minutes=i)
                o = price
                c = o + drift + rng.uniform(-0.5, 0.5) * wave
                h = max(o, c) + rng.uniform(0.0, 0.3) * wave
                lo = min(o, c) - rng.uniform(0.0, 0.3) * wave
                out.append(Bar(time_utc=t, open=o, high=h, low=lo,
                               close=c, volume=1.0, spread=2.0))
                price = c
            made += 1
        cursor += timedelta(days=1)
    return out
