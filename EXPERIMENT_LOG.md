# Experiment Log

Every experiment is recorded with its hypothesis, parameters, dataset,
periods, results, conclusion, and decision. Experiments that have not
yet run are listed as PLANNED. No experiment may be deleted.

## Experiment ID convention

`EXP-NNN`, sequential. Synthetic-pipeline validation experiments are
tagged `[SYNTHETIC]` and never represent market evidence.

---

## EXP-000 — Phase 0 repository and environment audit `[SYNTHETIC]`

- **Date:** 2026-10-05
- **Hypothesis:** The repository is empty and the environment can
  support the planned Python research engine and git workflow.
- **Parameters:** N/A
- **Dataset:** N/A
- **Training period:** N/A
- **Validation period:** N/A
- **OOS period:** N/A
- **Results:** Repository contained no files and no commits. Python
  3.10.12 and pytest 9.1.1 available. GitHub SSH authentication
  succeeded as `ybagheri`. No MetaTrader 5 terminal or broker data
  available.
- **Conclusion:** Environment supports the full Python pipeline and
  git workflow. Real market data is unavailable; research phases that
  need it are blocked until data is provided.
- **Decision:** Proceed with Phase 0 documentation, then build the
  engine and validate the pipeline on deterministic synthetic data.

---

## EXP-001 — Phase 2 deterministic replay `[SYNTHETIC]`

- **Date:** 2026-10-05
- **Hypothesis:** Same synthetic data + same v1.0 parameters → byte-identical signal CSV across runs.
- **Parameters:** v1.0 baseline (`StrategyConfig` defaults, seed 42, 5 synthetic days).
- **Dataset:** deterministic synthetic M1 (`engine/data/synthetic.py`) `[SYNTHETIC]` — never market evidence.
- **Results:** `export_signals` twice → byte-identical files; replay emits 4 signals over 5 days (4 SIGNAL_CONFIRMED + 1 Insufficient-data day). Test `test_export_byte_identical` green.
- **Conclusion:** replay is deterministic.
- **Decision:** Phase 2 replay accepted as deterministic control.

---

## EXP-002 — Phase 2 prefix-consistency (no-look-ahead) `[SYNTHETIC]`

- **Date:** 2026-10-05
- **Hypothesis:** Truncating data never changes decisions for fully-contained earlier days.
- **Parameters:** v1.0 baseline.
- **Dataset:** same synthetic set `[SYNTHETIC]`.
- **Results:** `test_prefix_consistency` green; earlier-day (state, reason) pairs identical after truncation. Missing OR-bar injection → NO_TRADE `Opening Range incomplete (missing bars)` (never filled).
- **Conclusion:** no-look-ahead holds on the replay path.
- **Decision:** proceed to Phase 3 backtester.

## EXP-003 — Phase 3 backtest accounting `[SYNTHETIC]`

- **Date:** 2026-10-05
- **Hypothesis:** Hand-computed fill fixtures (WIN, LOSS, same-bar SL-first, expiry at 11:30, MAE/MFE) match the simulator exactly.
- **Parameters:** v1.0 baseline, zero costs.
- **Dataset:** hand-built M1 fixtures in `tests/test_backtest.py` + synthetic replay `[SYNTHETIC]` — never market evidence.
- **Results:** all simulator edge-case tests green; 4 synthetic signals → 4 WIN, net +6.000R, expectancy +1.500R at zero cost. R outcomes measured from the actual fill (slippage moves fill adversely, SL/TP fixed).
- **Conclusion:** backtest accounting verified against fixtures.
- **Decision:** accept Phase 3 simulator; synthetic profits are pipeline validation only, not evidence.

---

## EXP-004 — Phase 3 cost sensitivity `[SYNTHETIC]`

- **Date:** 2026-10-05
- **Hypothesis:** Higher slippage monotonically degrades R.
- **Parameters:** slippage 0/1/2/5/10 points, v1.0 baseline otherwise.
- **Dataset:** same synthetic set `[SYNTHETIC]`.
- **Results:** net R = +6.000 / +4.350 / +2.699 / −2.252 / −10.503; expectancy = +1.500 / +1.087 / +0.675 / −0.563 / −2.626 — strictly monotonic. Cost-sensitivity test green.
- **Conclusion:** cost model behaves correctly; synthetic edge is cost-fragile (expected on trend-shaped data).
- **Decision:** every future report must state slippage + commission (spec A10).

---

## EXP-005 — Phase 5 baseline on real US30 M1 `[REAL DATA]`

- **Date:** 2026-10-06
- **Hypothesis:** The frozen v1.0 specification, run without
  optimization on real US30 data, produces a measurable
  baseline (the control experiment for all later phases).
- **Parameters:** v1.0 baseline, all INITIAL/FIXED values,
  zero changes. Costs: slippage 0, commission 0.
- **Dataset:** `data/US30_M1_UTC.csv` — 50,000 real broker
  M1 bars (UTC), 46 NY days, 2026-08-13 .. 2026-10-05.
- **Training period:** 27 days (2026-08-13 .. 2026-09-13).
- **Validation period:** 9 days (2026-09-14 .. 2026-09-23).
- **OOS period:** 10 days (2026-09-24 .. 2026-10-05).
- **Results:**
  - Data-quality audit: PASS (0 errors). Disclosed: 8 weekend
    breaks, 27 scheduled daily breaks (23:58->01:01 UTC),
    68 small gaps all outside the 09:30-11:30 NY signal
    windows, 10 OR-incomplete days (Sundays/partial days).
  - Replay: 46 days, **0 signals**. NO_TRADE: 10x OR
    incomplete, 35x "Opening Range too large", 1x "Breakout
    extension too large".
  - OR_Size/ATR_M5(14) on valid days: min 0.97, median
    ~2.5, max 6.84; only 1 of 36 days inside the v1.0 band
    [0.25, 1.00].
  - Backtest: 0 trades, net 0.000R.
  - Sensitivity grid: all 9 cells (TP 1.0-2.0 R; OR
    10/15/20/30 min) n=0 -> POSSIBLE OVERFITTING (degenerate).
  - Walk-forward: 22 windows (20d train / 5d test) defined.
  - Monte Carlo: n=10,000 both modes; R series empty -> all
    statistics 0 by construction.
  - Assessment: INCONCLUSIVE (n=0 < 30).
- **Conclusion:** The pipeline executes end-to-end on real
  data with zero errors, but the frozen v1.0 OR-size band
  [0.25, 1.00] x ATR_M5(14) rejects 100% of valid days on
  real US30 (a 15-minute opening range is 1.1x-6.8x the
  M5-ATR(14)). The strategy as frozen never trades; its
  profitability is untestable until the OR gate is
  recalibrated through a documented experiment.
- **Decision:** Baseline recorded as-is; **no parameter
  changed** (control experiment integrity). EXP-006
  (OR-filter recalibration study with pre-registered band
  and strict OOS evaluation) is PLANNED and requires
  explicit approval before any parameter changes.

---

## EXP-006 — OR-filter recalibration study `[REAL DATA]` (APPROVED 2026-10-06, pre-registered)

- **Date pre-registered:** 2026-10-06 (band hypothesis fixed
  BEFORE any OOS evaluation; v1.0 registry untouched).
- **Hypothesis:** The v1.0 OR-size band [0.25, 1.00] x
  ATR_M5(14) was calibrated for a different volatility
  regime. On real US30, the 15-minute OR is ~1-7x the
  M5-ATR(14); widening ONLY the upper bound to 7.00 (lower
  bound unchanged) admits a usable sample without
  re-fitting to OOS outcomes.
- **In-sample measurement (train block ONLY,
  2026-08-13..2026-09-13, 27 NY days):** 21 valid OR days;
  OR/ATR_M5 min 0.97, median 2.32, max 6.84, p90 ~4.3,
  p95 ~6.6; 1 of 21 inside v1.0 band. Lower bound needs
  no change (train min 0.97 >> 0.25).
- **Pre-registered candidate (single hypothesis, no grid
  search):** `min_or_atr = 0.25` (unchanged),
  `max_or_atr = 7.00` (ceiling above train max 6.84,
  rounded up). All other v1.0 parameters unchanged
  (OR 15 min, TP R1.5, costs 0/0). Rationale documented
  before seeing any OOS result.
- **Parameters:** candidate config above vs v1.0 control.
- **Dataset:** `data/US30_M1_UTC.csv` (same 50,000 real
  M1 bars as EXP-005).
- **Training period:** 2026-08-13..2026-09-13 (band
  selection ONLY).
- **Validation period:** 2026-09-14..2026-09-23
  (untouched by band selection; reported for completeness).
- **OOS period:** 2026-09-24..2026-10-05 (10 NY days;
  STRICT evaluation — replay -> backtest -> assessment ->
  walk-forward windows -> Monte Carlo n=10,000 seeded).
- **Results:**
  - OOS replay (2026-09-24..2026-10-05, 10 days): 3
    signals (09-28 BEARISH, 09-30 BEARISH, 10-02 BULLISH).
  - OOS backtest (costs 0/0): -1.0 / +1.5 / -1.0 R =
    net -0.500R, expectancy -0.167R.
  - OOS sensitivity: TP 1.0/1.25/1.5/1.75/2.0 R -> net
    +1.000 / -0.750 / -0.500 / -0.250 / +0.000 (n=3 each,
    sign-unstable); OR-duration cells degenerate n=0
    (machinery limitation: fixed [09:30,09:45) window vs
    N-bar expectation, disclosed in results file).
  - Monte Carlo (n=10,000, seed 42): permute P(profit)
    0.000; bootstrap P(profit) 0.255.
  - Assessment: INCONCLUSIVE (n=3 < 30). Walk-forward:
    unformable inside the 10-day OOS block.
  - Full-sample context (NOT evidence): 13 trades, net
    +7.000R (train +8.0R in-sample / validation -0.5R /
    OOS -0.5R).
- **Conclusion:** The widened band admits trades (13 vs 0
  under v1.0), confirming the EXP-005 diagnosis, but OOS
  n=3 supports no profitability claim in either direction.
  Next binding constraint is the breakout-extension filter
  (17 full-sample rejections) — a future study, unchanged.
- **Decision:** v1.0 registry stays FROZEN. The [0.25,
  7.00] band remains a research candidate with an
  INCONCLUSIVE record — not adopted. Full record:
  `results/EXP006_OR_RECALIBRATION.md`.
