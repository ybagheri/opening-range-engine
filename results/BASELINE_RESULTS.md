# Baseline Results - EXP-005 [REAL DATA]

**Status:** EXECUTED 2026-10-06 on real broker data.
**Result:** 0 trades in 46 NY days. The frozen v1.0 OR-size
filter rejects 100% of valid days on this dataset.
**Assessment:** INCONCLUSIVE (n=0 < 30) - no profitability
claim is possible; the control experiment instead exposes a
parameter-calibration defect in v1.0 (see Interpretation).

## Dataset

- File: `data/US30_M1_UTC.csv` (not committed; git-ignored)
- 50,000 M1 bars, UTC, 2026-08-14T01:02Z .. 2026-10-05T13:15Z
- 46 NY days (2026-08-13 .. 2026-10-05)
- Costs stated per spec A10: slippage 0 points,
  commission 0.0, point = 1.0 (INITIAL defaults)

## Procedure (executed verbatim)

    python3 -m engine.cli audit --input data/US30_M1_UTC.csv \
      --report results/DATA_QUALITY_REPORT_REAL.md   # PASS: 0 errors
    python3 -m engine.cli replay --input data/US30_M1_UTC.csv \
      --signals results/signals_real.csv --days results/days_real.csv
    python3 -m engine.cli backtest --signals results/signals_real.csv \
      --bars data/US30_M1_UTC.csv --trades results/trades_real.csv \
      --summary results/summary_real.txt --equity results/equity_real.csv

Then: 60/20/20 split (`engine.research.splits.make_splits`),
sensitivity (`run_grid`), walk-forward
(`walk_forward_windows`), Monte Carlo (`run_monte_carlo`,
n=10,000, seed 42, both modes), verdict (`assess`).

## Data quality (audit PASS, 0 errors)

All defects disclosed in `results/DATA_QUALITY_REPORT_REAL.md`:

- 8 multi-day weekend session breaks (INFO, expected).
- 27 scheduled daily broker breaks, 23:58->01:01 UTC
  (63 bars, recurring clock-time pattern) (INFO).
- 68 small feed-interruption gaps (2-4 bars) - all outside
  the 09:30-11:30 NY signal windows (WARNING).
- 10 NY days with an incomplete OR window (Sundays + the
  partial first/last days) -> correctly NO TRADE (WARNING).
- Final day partial (data ends 09:15 NY) (WARNING).
- No gap intersects the OR (09:30-09:45) or trade
  (09:45-11:30) window; DST rules agree with zoneinfo.

## Replay (no-look-ahead)

- days=46, **signals=0**.
- NO_TRADE reasons:
  - 10 x "Opening Range incomplete (missing bars)" (Sundays,
    partial first/last days - data integrity, not strategy).
  - 35 x "Opening Range too large" - OR_Size > 1.00 x ATR_M5.
  - 1 x "Breakout extension too large" (2026-08-31, the only
    day passing the OR gate, ratio 0.97).

### OR-size gate evidence (the control result)

OR_Size / ATR_M5(14) on the 36 days with a valid OR:

| statistic | value |
| --- | --- |
| min | 0.97 |
| median | ~2.5 |
| max | 6.84 |
| days inside v1.0 band [0.25, 1.00] | 1 of 36 (2.8%) |

A 15-minute US30 opening range is 1.1x-6.8x the M5-ATR(14)
on real data; v1.0's band (INITIAL MaxOR_ATR = 1.00) admits
only sub-1.0 ratios, so the strategy as frozen almost never
arms. (The single in-band day was then rejected by the
breakout-extension filter.)

## Backtest

- trades=0, net_r=+0.000, expectancy_r=+0.000
  (`results/summary_real.txt`, `results/trades_real.csv`,
  `results/equity_real.csv`).

## Research machinery (run for the record)

- **Splits** (60/20/20 over days): train 27 (2026-08-13..
  2026-09-13), validation 9 (2026-09-14..2026-09-23),
  OOS 10 (2026-09-24..2026-10-05).
- **Walk-forward** (train 20d / test 5d, step 1d): 22 windows,
  W1 test 2026-09-06..09-10 ... W22 test 2026-09-30..10-05.
- **Sensitivity grid** (`run_grid`): every cell n=0, net_r=0 -
  TP 1.0/1.25/1.5/1.75/2.0 R AND OR minutes 10/15/20/30 all
  produce zero trades (even a 10-minute OR exceeds 1.0 x
  ATR_M5(14) on every valid day). Grid verdict: POSSIBLE
  OVERFITTING (all cells degenerate to zero).
- **Monte Carlo** (n=10,000, seed 42, permute + bootstrap):
  R series is empty; all statistics are 0 by construction.
- **Assessment** (`assess`): INCONCLUSIVE - "n=0 < 30: sample
  too small to judge".

## Interpretation (finding, not a parameter change)

1. The pipeline (audit -> replay -> backtest -> research
   machinery) executes end-to-end on real broker data with
   zero errors; the engine is unblocked and working. The frozen v1.0 parameter set never trades on real US30
   data: the OR-size band [0.25, 1.00] x ATR_M5(14) is
   mis-calibrated for US30's observed opening volatility
   (median ratio ~2.5). This is a control-experiment result:
   v1.0 is recorded as-is. **No parameter was changed**
   (project rule: parameters change only via a documented
   experiment). Profitability of the *strategy idea* remains
   untested - it cannot be evaluated until the OR gate admits
   a usable sample.

## Next (proposed, requires a documented experiment)

- EXP-006 (PLANNED): OR-filter recalibration study - measure
  the OR/ATR_M5 distribution on an in-sample period, choose a
  band hypothesis (e.g. wider MaxOR_ATR), pre-register it, and
  evaluate strictly on the held-out OOS block (2026-09-24..
  2026-10-05) with walk-forward + Monte Carlo. Until such an
  experiment is approved and recorded, v1.0 parameters remain
  frozen and no EA work may begin.

## Synthetic reference [SYNTHETIC] (machinery check, not evidence)

- 5 days -> 4 signals -> 4 WIN, net +6.000R, expectancy +1.500R.
- Verdict on synthetic: INCONCLUSIVE (n=4 < 30) - correctly refused.
