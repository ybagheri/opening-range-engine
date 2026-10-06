"""CLI: replay / backtest / audit entry points."""

import argparse
import sys

from .config import StrategyConfig
from .data.loader import load_m1_csv


def _base_parser():
    p = argparse.ArgumentParser(prog="engine.cli")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("replay", help="replay M1 CSV -> signal CSVs")
    r.add_argument("--input", required=True)
    r.add_argument("--signals", required=True)
    r.add_argument("--days", required=True)
    r.add_argument("--symbol", default="US30")
    b = sub.add_parser("backtest", help="R backtest: signals + M1 -> trades")
    b.add_argument("--signals", required=True)
    b.add_argument("--bars", required=True)
    b.add_argument("--trades", required=True)
    b.add_argument("--summary", required=True)
    b.add_argument("--equity", required=True)
    b.add_argument("--symbol", default="US30")
    b.add_argument("--slippage-points", type=int, default=0)
    b.add_argument("--commission", type=float, default=0.0)
    a = sub.add_parser("audit", help="audit M1 data quality")
    a.add_argument("--input", required=True)
    a.add_argument("--report", required=True)
    a.add_argument("--symbol", default="US30")
    return p


def cmd_replay(args) -> int:
    from .data.synthetic import generate_m1
    from .export import export_day_reports, export_signals
    from .replay import replay_all
    cfg = StrategyConfig(symbol=args.symbol).validate()
    if args.input == "synthetic":
        bars = generate_m1(seed=cfg.seed)
    else:
        bars = load_m1_csv(args.input)
    reports, signals = replay_all(bars, cfg)
    export_signals(signals, args.signals)
    export_day_reports(reports, args.days)
    print(f"days={len(reports)} signals={len(signals)}")
    for rep in reports:
        print(f"{rep.ny_day} {rep.state} {rep.reason or ''}")
    return 0


def cmd_backtest(args) -> int:
    import csv
    from .backtest import (
        CostModel,
        compute_metrics,
        export_equity,
        export_summary,
        export_trades,
        simulate_all,
        trade_from_signal_and_result,
    )
    from .data.synthetic import generate_m1
    from .data.schema import SignalRecord
    cfg = StrategyConfig(symbol=args.symbol).validate()
    costs = CostModel(slippage_points=args.slippage_points,
                      commission_per_trade=args.commission,
                      point=cfg.point).validate()
    with open(args.signals, newline="", encoding="utf-8") as fh:
        signals = [SignalRecord.from_row(r) for r in csv.DictReader(fh)]
    if args.bars == "synthetic":
        bars = generate_m1(seed=cfg.seed)
    else:
        bars = load_m1_csv(args.bars)
    results = simulate_all(signals, bars, cfg, costs)
    trades = [trade_from_signal_and_result(s, r)
              for s, r in zip(sorted(signals,
                                     key=lambda s: s.signal_time_utc),
                              results)]
    r_values = [t.r_result for t in trades]
    metrics = compute_metrics(r_values)
    export_trades(trades, args.trades)
    export_summary(metrics, costs, args.summary)
    export_equity(r_values, args.equity)
    print(f"trades={len(trades)} net_r={metrics.net_r:.3f} "
          f"expectancy_r={metrics.expectancy_r:.3f}")
    for t in trades:
        print(f"{t.date} {t.direction} {t.result} "
              f"{t.r_result:+.3f}R mae={t.mae_r:+.2f} mfe={t.mfe_r:+.2f}")
    return 0


def cmd_audit(args) -> int:
    from .data.synthetic import generate_m1
    from .quality.audit import audit_bars, render_report
    cfg = StrategyConfig(symbol=args.symbol).validate()
    if args.input == "synthetic":
        bars = generate_m1(seed=cfg.seed)
    else:
        bars = load_m1_csv(args.input)
    report = audit_bars(bars, symbol=cfg.symbol)
    text = render_report(report,
                         source=("synthetic" if args.input == "synthetic"
                                 else "real"))
    with open(args.report, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(text)
    return 0 if report.passed() else 1


def main(argv=None) -> int:
    args = _base_parser().parse_args(argv)
    if args.cmd == "replay":
        return cmd_replay(args)
    if args.cmd == "backtest":
        return cmd_backtest(args)
    if args.cmd == "audit":
        return cmd_audit(args)
    print(f"{args.cmd}: not implemented until its phase", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
