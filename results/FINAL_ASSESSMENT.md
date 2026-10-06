# Final Strategy Assessment — Phase 11 `[REAL DATA]`

**Date:** 2026-10-06. Evidence: EXP-005 + EXP-006 + EXP-007.
**Verdict: REJECT** — the strategy, in v1.0 and EXP-006-candidate
form, shows no edge and is not approved for forward demo, EA
development, or live use. The research pipeline itself is
validated and retained.

## Evidence summary (all `[REAL DATA]`, costs 0/0 throughout)

| Experiment | Sample | Net R | Expectancy R | PF | Verdict |
| --- | --- | --- | --- | --- | --- |
| EXP-005 v1.0 control (US30) | 46 days, 0 trades | 0.000 | — | — | INCONCLUSIVE; OR band [0.25,1.00] rejects 100% of valid days |
| EXP-006 candidate OOS (US30) | n=3 | -0.500 | -0.167 | 0.625 | INCONCLUSIVE (n<30) |
| EXP-007 pooled (5 symbols) | n=54 | -6.000 | -0.111 | 0.818 | WEAK, borderline FAILED |
| — XAUUSD | n=14 | -1.500 | -0.107 | 0.833 | negative lean |
| — EURUSD | n=4 | -1.500 | -0.375 | 0.500 | too small to read |
| — US30 | n=12 | +5.500 | +0.458 | 2.100 | positive but n<30 |
| — US500 | n=11 | -6.000 | -0.545 | 0.333 | negative |
| — NAS100 | n=13 | -2.500 | -0.192 | 0.643 | negative |

Pooled detail: win rate 0.333 vs 0.400 breakeven at TP1.5/SL1.0;
max DD 14.000R; worst losing streak 5 / best winning 3.
Monte Carlo (10k, seed 42): bootstrap P(profit) 0.236.
By month: Aug (n=13) -5.5R / Sep (n=36) +3.5R / Oct (n=5)
-4.0R — no stability. By direction: BEARISH (n=34) +0.5R /
BULLISH (n=20) -6.5R — post-hoc observation, NOT a
modification basis (both cuts <30; fitting to them would be
overfitting by construction).

## Validation-discipline checklist (spec §20)

- Splits 60/20/20: DONE (EXP-005/006 dates documented).
- Walk-forward 20d/5d: windows defined; OOS-contained WF
  unformable (10-day OOS); full-sample WF not run (would mix
  band-selection data into tests). PARTIAL — honestly limited.
- Monte Carlo ≥10,000: DONE (permute + bootstrap + streaks,
  EXP-006 and EXP-007).
- Nearby-parameter robustness: TP grid run (OOS slice,
  sign-unstable at n=3); OR-duration grid degenerate
  (disclosed `session.py` limitation); trade-window grid
  structural placeholder. PARTIAL.
- Multi-symbol, same unmodified parameters first: DONE
  (EXP-007) — and it fails: 4 of 5 symbols negative.
- Costs: all runs at slippage 0 / commission 0. Live costs
  can only subtract (monotonicity demonstrated EXP-004),
  so zero-cost -6.0R is an UPPER BOUND on real performance.

## Why not Continue

Continue requires a validated edge. The only assessable sample
(pooled n=54) is negative on expectancy (-0.111R), PF (0.818),
win rate vs breakeven (0.333 vs 0.400), and Monte Carlo
(P(profit) 0.236). US30's +5.5R is n=12 — below every
threshold — and elevating the best of 5 symbols ex post is the
multiple-comparison fallacy.

## Why not Modify (now)

No modification direction has a priori support in the evidence:
losses are broad-based across symbols, months, and both
directions. Any change fit to these 54 trades (bullish-side
filters, breakout-extension widening, symbol restriction to
US30) would be overfitting by definition. Modify is parked
until a hypothesis can be pre-registered against NEW held-out
data — which does not currently exist.

## Decision: REJECT (DEC-014)

1. Neither v1.0 (untestable — never trades) nor the
   [0.25, 7.00] candidate (WEAK/borderline FAILED at n=54)
   is approved for forward demo, EA work, or live trading.
2. Phase 10 (forward demo) and Phase 12 (EA) are CLOSED as
   not-recommended — demoing/EA-building a rejected
   candidate consumes resources for no evidentiary gain.
   (MT5 absence is moot: there is nothing validated to
   forward-test.)
3. Retained: the full research pipeline (engine, audit,
   replay, backtester, research machinery, 103 tests) and
   all evidence files — reusable for future strategy
   research under the same discipline.
4. Re-entry condition (all must hold): a NEW hypothesis,
   pre-registered BEFORE touching new held-out data, then
   OOS n>=30 with walk-forward + Monte Carlo confirmation
   and stated costs. The current data is spent — it may
   never again serve as evaluation for a hypothesis formed
   from it.
