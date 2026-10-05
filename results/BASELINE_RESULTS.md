# Baseline Results — NOT RUN (blocked: no real data)

**Status:** Phase 5 cannot execute. This environment has no MT5
terminal and no broker M1 feed. The pipeline below is implemented and
validated on synthetic data; paste a real US30 M1 CSV (UTC) and the
commands run unchanged.

## Procedure (when data arrives)

```bash
python3 -m engine.cli audit --input data/US30_M1.csv \
  --report results/DATA_QUALITY_REPORT_REAL.md
# 0 errors required before proceeding
python3 -m engine.cli replay --input data/US30_M1.csv \
  --signals results/signals_real.csv --days results/days_real.csv
python3 -m engine.cli backtest --signals results/signals_real.csv \
  --bars data/US30_M1.csv --trades results/trades_real.csv \
  --summary results/summary_real.txt --equity results/equity_real.csv
```

Then: 60/20/20 split via `engine.research.splits.make_splits`,
sensitivity via `run_grid`, walk-forward via
`walk_forward_windows`, Monte Carlo via `run_monte_carlo`
(n=10,000, both modes), verdict via `assess`. Record as EXP-005.

## Synthetic reference `[SYNTHETIC]` (machinery check, not evidence)

- 5 days → 4 signals → 4 WIN, net +6.000R, expectancy +1.500R.
- Verdict on synthetic: INCONCLUSIVE (n=4 < 30) — correctly refused.
