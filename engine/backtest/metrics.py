"""Performance metrics (spec section 19: basic, risk, distribution)."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Metrics:
    n_trades: int
    n_wins: int
    n_losses: int
    win_rate: float
    avg_win_r: float
    avg_loss_r: float
    expectancy_r: float
    net_r: float
    profit_factor: float
    max_drawdown_r: float
    max_losing_streak: int
    max_winning_streak: int
    median_r: float
    stdev_r: float


def _median(xs: list) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0


def _stdev(xs: list) -> float:
    if len(xs) < 2:
        return 0.0
    mean = sum(xs) / len(xs)
    return math.sqrt(sum((x - mean) ** 2 for x in xs) / (len(xs) - 1))


def compute_metrics(r_values: list) -> Metrics:
    """Compute metrics over per-trade R results (expired = 0R included)."""
    n = len(r_values)
    wins = [r for r in r_values if r > 0]
    losses = [r for r in r_values if r < 0]
    win_rate = len(wins) / n if n else 0.0
    loss_rate = len(losses) / n if n else 0.0
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    expectancy = win_rate * avg_win + loss_rate * avg_loss
    net = sum(r_values)
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = (gross_win / gross_loss) if gross_loss > 0 else (
        float("inf") if gross_win > 0 else 0.0)
    peak = 0.0
    running = 0.0
    max_dd = 0.0
    for r in r_values:
        running += r
        peak = max(peak, running)
        max_dd = max(max_dd, peak - running)
    max_lose = max_win = 0
    cur_lose = cur_win = 0
    for r in r_values:
        if r <= 0:
            cur_lose += 1
            cur_win = 0
        else:
            cur_win += 1
            cur_lose = 0
        max_lose = max(max_lose, cur_lose)
        max_win = max(max_win, cur_win)
    return Metrics(n, len(wins), len(losses), win_rate, avg_win,
                   avg_loss, expectancy, net, pf, max_dd,
                   max_lose, max_win, _median(r_values),
                   _stdev(r_values))
