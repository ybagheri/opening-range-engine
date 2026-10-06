# Multi-Symbol Report — EXP-007 `[REAL DATA]`

**Status:** EXECUTED 2026-10-06. Pre-registered config, zero
per-symbol tuning. Costs: slippage 0, commission 0.0.
**Bottom line: pooled n=54, net -6.000R, expectancy
-0.111R, PF 0.818 — no edge detected. Verdict: WEAK
(borderline FAILED).** v1.0 registry untouched.

## Config (identical strategy parameters, all symbols)

OR 15 min, `min_or_atr` 0.25, `max_or_atr` 7.00 (EXP-006
candidate), TP R1.5. Per-symbol market input ONLY (FIXED
convention, not a strategy parameter): point = observed
tick size — XAUUSD 0.01, EURUSD 0.00001, US30/US500/NAS100
0.1. Note: US30 here uses point 0.1 (vs 1.0 in EXP-005/006)
and the extended file, so its trade list differs slightly
from EXP-006 context — disclosed, not hidden.

## Data (all 1-minute bars; `M5` filenames are mislabeled —
verified 99.9% 1-min spacing before use; 50,000 bars each)

- `data/XAUUSD_M5_UTC.csv` — 2026-08-14..10-06, 46 NY days
- `data/EURUSD_M5_UTC.csv` — 2026-08-18..10-06, 43 NY days
- `data/US30_M5_UTC.csv` — 2026-08-14..10-06, 46 NY days
- `data/US500_M5_UTC.csv` — 2026-08-17..10-06, 45 NY days
- `data/NAS100_M5_UTC.csv` — 2026-08-17..10-06, 45 NY days

## Audits: all 5 PASS (0 errors)

Weekend session breaks + scheduled daily broker breaks
(63-bar US indices, 71-bar XAUUSD, 21-bar EURUSD) as INFO;
small overnight gaps as WARNING, all outside the
09:30-11:30 NY signal windows. Per-symbol reports were
rendered to temp files during execution (audits re-runnable
via `python3 -m engine.cli audit`).

## Per-symbol replay + backtest (candidate config)

| Symbol | Days | Signals | Trades (W/L/E) | Net R | Exp R | Win rate | PF | MaxDD R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| XAUUSD | 46 | 14 | 5/9/0 | -1.500 | -0.107 | 0.357 | 0.833 | 3.000 |
| EURUSD | 43 | 4 | 1/3/0 | -1.500 | -0.375 | 0.250 | 0.500 | 2.000 |
| US30 | 46 | 12 | 7/5/0 | +5.500 | +0.458 | 0.583 | 2.100 | 3.000 |
| US500 | 45 | 11 | 2/9/0 | -6.000 | -0.545 | 0.182 | 0.333 | 6.000 |
| NAS100 | 45 | 13 | 3/7/3 | -2.500 | -0.192 | 0.231 | 0.643 | 5.500 |

(E = EXPIRED 0R: stop entry never filled by 11:30 NY —
3x NAS100. Full per-trade lists in experiment artifacts.)

## Pooled evidence (n=54 — first assessable sample)

- Pooled: **n=54, net -6.000R, expectancy -0.111R, win
  rate 0.333, PF 0.818, max DD 14.000R.**
- Monte Carlo (n=10,000, seed 42): permute P(profit)
  0.000; bootstrap mean -5.959R, p5 -20.000R, p95 +8.000R,
  **P(profit) 0.236**.
- Verdict note: the `assess` fall-through label for these
  numbers reads PROMISING ("needs confirmation") — that
  label is explicitly NOT claimed here. With negative
  expectancy and PF below 1.0, the honest classification
  is **WEAK, borderline FAILED** (FAILED cutoffs are
  exp<=-0.2 / PF<0.8; observed -0.111 / 0.818 sit just
  above both): no edge detected, with the lean negative.
  The machinery's label set did not anticipate this
  borderline; the numbers above are the verdict, not the
  word.
- Heterogeneity warning: only US30 is positive (+5.5R,
  n=12); US500 (-6.0R) and NAS100 (-2.5R) are negative and
  EURUSD (n=4) is too small to read. Pooling correlated
  US-index trades overstates effective sample
  independence — the pooled n=54 is an upper bound on
  evidence, not a clean n=54.

## Interpretation

1. The candidate does not generalize: 4 of 5 symbols
   negative, pooled expectancy negative at the first
   n>=30 sample. US30's positivity (+5.5R, n=12) is
   isolated and itself below n=30.
2. The failure mode also moved: the OR gate now admits
   trades everywhere (54 pooled), so downstream logic
   (breakout/trigger/stop placement) is now testable —
   and what it shows so far is losses.
3. No further tuning on this data: any new hypothesis
   (e.g. breakout-extension recalibration) must be
   pre-registered against NEW held-out data, never fit to
   these 54 trades.
