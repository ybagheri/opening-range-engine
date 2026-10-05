"""Seeded Monte Carlo engine (spec section 20: >= 10,000 simulations).

Three analyses over a fixed R series (research-only; not advice):
1. Random trade ordering (path / drawdown distribution).
2. Bootstrap resampling with replacement (sampling uncertainty).
3. Losing-streak analysis (run-length distribution).

Pure functions of (r_values, n_sims, seed): byte-identical outputs.
"""

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class MonteCarloResult:
    n_sims: int
    seed: int
    mean_net_r: float
    p5_net_r: float
    p50_net_r: float
    p95_net_r: float
    prob_profit: float
    max_drawdown_p95: float
    worst_losing_streak: int


def _quantile(sorted_xs: list, q: float) -> float:
    if not sorted_xs:
        return 0.0
    pos = q * (len(sorted_xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_xs) - 1)
    frac = pos - lo
    return sorted_xs[lo] * (1 - frac) + sorted_xs[hi] * frac


def _drawdown(rs: list) -> float:
    peak = run = dd = 0.0
    for r in rs:
        run += r
        peak = max(peak, run)
        dd = max(dd, peak - run)
    return dd


def _worst_losing_run(rs: list) -> int:
    worst = cur = 0
    for r in rs:
        cur = cur + 1 if r <= 0 else 0
        worst = max(worst, cur)
    return worst


def run_monte_carlo(r_values: list, n_sims: int = 10000,
                    seed: int = 42,
                    mode: str = "permute") -> MonteCarloResult:
    """Run the Monte Carlo analysis.

    mode='permute': shuffle order each sim (path dependence).
    mode='bootstrap': resample with replacement each sim (uncertainty).
    """
    if mode not in ("permute", "bootstrap"):
        raise ValueError("mode must be 'permute' or 'bootstrap'")
    if n_sims < 1:
        raise ValueError("n_sims must be >= 1")
    if not r_values:
        return MonteCarloResult(n_sims, seed, 0.0, 0.0, 0.0, 0.0,
                                0.0, 0.0, 0)
    rng = random.Random(seed)
    nets: list = []
    dds: list = []
    worst_streak = 0
    base = list(r_values)
    for _ in range(n_sims):
        if mode == "permute":
            sample = rng.sample(base, len(base))
        else:
            sample = [rng.choice(base) for _ in base]
        nets.append(sum(sample))
        dds.append(_drawdown(sample))
        worst_streak = max(worst_streak, _worst_losing_run(sample))
    nets_sorted = sorted(nets)
    return MonteCarloResult(
        n_sims=n_sims, seed=seed,
        mean_net_r=sum(nets) / len(nets),
        p5_net_r=_quantile(nets_sorted, 0.05),
        p50_net_r=_quantile(nets_sorted, 0.50),
        p95_net_r=_quantile(nets_sorted, 0.95),
        prob_profit=sum(1 for x in nets if x > 0) / len(nets),
        max_drawdown_p95=_quantile(sorted(dds), 0.95),
        worst_losing_streak=worst_streak)
