"""Backtest report export (trades CSV + summary + equity curve)."""

import csv


def _fmt(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return repr(float(value))
    return str(value)


def export_trades(trades, path: str) -> str:
    from .records import TRADE_COLUMNS
    rows = sorted(trades, key=lambda t: t.signal_time_utc)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(list(TRADE_COLUMNS))
        for tr in rows:
            writer.writerow([_fmt(v) for v in tr.to_row()])
    return path


def export_summary(metrics, costs, path: str) -> str:
    lines = [
        "# Backtest summary (R-based; research only, not advice)",
        f"n_trades={metrics.n_trades}",
        f"win_rate={metrics.win_rate:.4f}",
        f"avg_win_r={metrics.avg_win_r:.4f}",
        f"avg_loss_r={metrics.avg_loss_r:.4f}",
        f"expectancy_r={metrics.expectancy_r:.4f}",
        f"net_r={metrics.net_r:.4f}",
        f"profit_factor={metrics.profit_factor:.4f}",
        f"max_drawdown_r={metrics.max_drawdown_r:.4f}",
        f"max_losing_streak={metrics.max_losing_streak}",
        f"max_winning_streak={metrics.max_winning_streak}",
        f"median_r={metrics.median_r:.4f}",
        f"stdev_r={metrics.stdev_r:.4f}",
        (f"costs: slippage_points={costs.slippage_points}, "
         f"commission_per_trade={costs.commission_per_trade}, "
         f"point={costs.point}"),
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def export_equity(r_values: list, path: str) -> str:
    running = 0.0
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["trade", "trade_r", "equity_r"])
        for i, r in enumerate(r_values, start=1):
            running += r
            writer.writerow([i, _fmt(r), _fmt(running)])
    return path
