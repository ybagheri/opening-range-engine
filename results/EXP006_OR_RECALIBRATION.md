# EXP-006 — OR-Filter Recalibration Study `[REAL DATA]`

**Status:** EXECUTED 2026-10-06 on real broker data.
**Design:** pre-registered BEFORE any OOS evaluation (see
`EXPERIMENT_LOG.md` EXP-006). Single band hypothesis, chosen
from the train-block OR/ATR distribution ONLY — never from
OOS outcomes and never by optimizing P&L.
**Assessment:** INCONCLUSIVE (OOS n=3 < 30). No edge claimed.
v1.0 registry untouched.

## Candidate (research only, NOT adopted)

- `min_or_atr = 0.25` (unchanged), `max_or_atr = 7.00`
  (ceiling above train max 6.84, rounded up).
- All other v1.0 parameters unchanged (OR 15 min, TP R1.5,
  costs slippage 0 / commission 0.0, point 1.0).

## Dataset and blocks (same file as EXP-005)

- File: `data/US30_M1_UTC.csv` (not committed; git-ignored).
- Train 27 NY days (2026-08-13..2026-09-13): band
  selection from OR/ATR distribution only.
- Validation 9 days (2026-09-14..2026-09-23): untouched
  by band selection; reported for completeness.
- OOS 10 days (2026-09-24..2026-10-05): STRICT evaluation.
  Replay ran over full history (causal indicators only),
  then sliced to the OOS block — no OOS bar influenced the
  band or any indicator value.

## OOS evaluation (the evidence)

- Replay (OOS 10 days): **3 signals** (2026-09-28 BEARISH,
  2026-09-30 BEARISH, 2026-10-02 BULLISH). NO_TRADE: 2x
  Neutral M15 bias, 2x Breakout extension too large, 3x OR
  incomplete (weekend/partial days — data integrity).
- Backtest (OOS, costs 0/0): LOSS / WIN / LOSS =
  **-1.0 / +1.5 / -1.0 R → net -0.500R, expectancy
  -0.167R**, win rate 0.333, PF 0.625, max DD 2.000R.
- Sensitivity on the OOS slice: TP cells (R) —
  1.0: +1.000; 1.25: -0.750; 1.5: -0.500; 1.75: -0.250;
  2.0: +0.000 (each n=3). Sign-unstable →
  POSSIBLE OVERFITTING by the machinery rule (expected at
  n=3; records instability, not a verdict).
- OR-duration cells (10/20/30 min): all n=0 — DEGENERATE
  by machinery construction (`session.py` collects the
  fixed [09:30,09:45) window while `opening_range_minutes`
  demands exactly N bars, so any N≠15 is always invalid).
  Machinery limitation, disclosed; not evidence.
- Monte Carlo on the OOS R series (n=10,000, seed 42):
  permute mean -0.500R, p5/p50/p95 -0.500R, P(profit)
  0.000; bootstrap mean -0.518R, p5 -3.000R, p95 +2.000R,
  P(profit) 0.255, dd-p95 3.000R, worst streak 3.
- Assessment (`assess`): **INCONCLUSIVE — "n=3 < 30:
  sample too small to judge"** (any sensitivity verdict
  is gated behind n≥30 by construction).
- Walk-forward: NO 20d/5d window fits inside the 10-day
  OOS block, so OOS-contained walk-forward is unformable.
  Full-sample walk-forward would mix band-selection data
  into test windows and violate OOS discipline — not run
  as evidence. WF remains gated on a larger dataset.

## Context (descriptive ONLY, not evidence)

- Full-sample candidate replay: 46 days → 13 signals
  (10x OR incomplete, 17x breakout extension too large,
  5x neutral bias, 1x unconfirmed).
- Full-sample backtest: 13 trades, net **+7.000R**,
  expectancy +0.538R, win rate 0.615, PF 2.400, max DD
  3.000R. Split: train +8.0R (n=7, in-sample for the
  distribution fit — NOT validation), validation -0.5R
  (n=3), OOS -0.5R (n=3). The train/OOS divergence is
  exactly why OOS discipline exists; no conclusion is
  drawn from n=3 either way.

## Interpretation (finding, not a parameter change)

1. The recalibrated band admits trades (13 vs 0 under
   v1.0), confirming EXP-005's diagnosis that the OR gate
   — not downstream logic — was the blocker. The next
   binding constraint is the breakout-extension filter
   (17 rejections full-sample), a candidate for a future
   pre-registered study, NOT changed here.
2. OOS n=3 cannot support any profitability claim in
   either direction. The strategy idea remains UNTESTED
   at the n≥30 standard; ~10x more OOS data (or
   additional symbols under identical discipline) is
   required before Phase 11 can decide Continue/Modify/
   Reject.
3. v1.0 parameters remain FROZEN (registry unchanged).
   The [0.25, 7.00] band is a research candidate with an
   INCONCLUSIVE OOS record — not an adoption.
