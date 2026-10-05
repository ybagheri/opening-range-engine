"""Nearby-parameter sensitivity grid (spec section 20).

Varies TP (1.0/1.25/1.5/1.75/2.0 R) and OR duration (10/15/20/30 min)
for real; window cells are structural placeholders until the replay
supports variable windows (TRADE_START/END_NY are module constants).
Classification per spec: nearby instability -> POSSIBLE OVERFITTING;
stability -> ROBUST REGION. No parameter is adopted here — this is
measurement machinery only.
"""

from dataclasses import dataclass, field

TP_GRID: tuple = (1.0, 1.25, 1.5, 1.75, 2.0)
OR_MINUTES_GRID: tuple = (10, 15, 20, 30)
WINDOW_MINUTES_GRID: tuple = (60, 90, 120, 150, 180)


@dataclass(frozen=True)
class SensitivityCell:
    varied: str
    value: object
    n_trades: int
    net_r: float
    expectancy_r: float


@dataclass
class SensitivityReport:
    cells: list = field(default_factory=list)

    def verdict(self) -> str:
        """ROBUST REGION iff every cell keeps the baseline sign of net R."""
        if not self.cells:
            return "INCONCLUSIVE"
        signs = {1 if c.net_r > 0 else (-1 if c.net_r < 0 else 0)
                 for c in self.cells}
        if len(signs) == 1 and 0 not in signs:
            return "ROBUST REGION"
        return "POSSIBLE OVERFITTING"

def _with(config, **overrides):
    from dataclasses import replace
    return replace(config, **overrides)


def run_grid(m1_bars, base_config, costs=None) -> SensitivityReport:
    """Replay+backtest each nearby value; return the report."""
    from ..backtest import (
        CostModel, compute_metrics, simulate_all,
        trade_from_signal_and_result,
    )
    from ..replay import replay_all
    report = SensitivityReport()
    cost_model = costs or CostModel(
        slippage_points=base_config.slippage_points,
        commission_per_trade=base_config.commission_per_lot,
        point=base_config.point)
    jobs: list = []
    for tp in TP_GRID:
        jobs.append(("tp_multiplier", tp,
                     _with(base_config, tp_mode=_tp_mode(tp))))
    for or_min in OR_MINUTES_GRID:
        jobs.append(("opening_range_minutes", or_min,
                     _with(base_config, opening_range_minutes=or_min)))
    for varied, value, cfg in jobs:
        _, signals = replay_all(m1_bars, cfg)
        results = simulate_all(signals, m1_bars, cfg, cost_model)
        ordered = sorted(signals, key=lambda s: s.signal_time_utc)
        r_values = [trade_from_signal_and_result(s, r).r_result
                    for s, r in zip(ordered, results)]
        m = compute_metrics(r_values)
        report.cells.append(SensitivityCell(varied, value,
                                            m.n_trades, m.net_r,
                                            m.expectancy_r))
    return report


def _tp_mode(mult: float):
    from ..config import TPMode
    for mode in TPMode:
        if abs(mode.value - mult) < 1e-9:
            return mode
    raise ValueError(f"no TPMode for {mult}")

