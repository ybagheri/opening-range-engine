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
    b = sub.add_parser("backtest", help="(Phase 3) R backtest")
    b.add_argument("--signals", required=True)
    a = sub.add_parser("audit", help="(Phase 4) data quality audit")
    a.add_argument("--input", required=True)
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


def main(argv=None) -> int:
    args = _base_parser().parse_args(argv)
    if args.cmd == "replay":
        return cmd_replay(args)
    print(f"{args.cmd}: not implemented until its phase", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
