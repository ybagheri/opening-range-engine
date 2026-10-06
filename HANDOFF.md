# PROJECT HANDOFF

## Current Status

- **Phase:** 6 - Parameter Sensitivity (GATED: see EXP-005
  finding below; next action is the EXP-006 recalibration
  study, PLANNED and requiring approval)
- **Status:** EXP-005 EXECUTED on real US30 data; all
  documents updated; 103 tests green; working tree ready
  to commit.
- **Overall Progress:** 6 of 13 phases (0-5 complete).

## Phase 5 Evidence `[REAL DATA]` (EXP-005, 2026-10-06)

- Dataset: `data/US30_M1_UTC.csv` - 50,000 real broker
  M1 bars (UTC), 46 NY days, 2026-08-13 .. 2026-10-05
  (git-ignored; not committed).
- Data-quality audit: **PASS (0 errors)**. Disclosed:
  8 weekend breaks, 27 scheduled daily breaks
  (23:58->01:01 UTC), 68 small gaps all OUTSIDE the
  09:30-11:30 NY signal windows, 10 OR-incomplete days.
- Replay: 46 days, **0 signals** (35x "Opening Range
  too large", 10x "Opening Range incomplete", 1x
  "Breakout extension too large").
- Backtest: 0 trades, net 0.000R.
- Sensitivity grid: all 9 cells (TP 1.0-2.0 R; OR
  10/15/20/30 min) n=0. Walk-forward: 22 windows
  (20d/5d) defined. Monte Carlo: n=10,000 both modes
  (empty R series). Assessment: INCONCLUSIVE (n=0 < 30).
- **Key finding:** the frozen v1.0 OR-size band
  [0.25, 1.00] x ATR_M5(14) rejects 100% of valid days
  on real US30 - a 15-minute opening range is 1.1x-6.8x
  the M5-ATR(14) (median ~2.5). The strategy as frozen
  never arms; its profitability is untestable until the
  OR gate is recalibrated through a documented experiment.

## Last Completed Work

- Phase 5 (EXP-005): real-data baseline executed
  end-to-end (audit -> replay -> backtest -> splits ->
  sensitivity -> walk-forward -> Monte Carlo -> assess).
- `engine/data/loader.py`: MT5 export-format support
  (case-insensitive headers, TickVolume/RealVolume ->
  volume, dot-dates with seconds).
- `engine/quality/audit.py`: impact-based gap severity
  model (DEC-010) + trade-window completeness check +
  source-aware report rendering ("EXECUTED" for real).
- `results/BASELINE_RESULTS.md`: full EXP-005 record.
- `results/DATA_QUALITY_REPORT_REAL.md`: real audit.
- New tests: `tests/test_loader.py` (6), expanded
  `tests/test_audit.py` (+6). 103 tests green.

## Current Implementation

- Python core (config, ny_time, bars, indicators,
  session, bias, signals, replay, export) + backtest
  (costs, metrics, records, report, simulator) + data
  (loader, schema, synthetic) + quality (audit) +
  research (splits, walk_forward, montecarlo,
  sensitivity, assessment) + CLI.
- MQL5 indicator v1.0 structural draft (compilation
  requires MetaEditor; not available here).
- Docs: README.md, README_FA.md (Persian),
  docs/STRATEGY_SPEC.md, docs/PARAMETER_REGISTRY.md,
  docs/ARCHITECTURE.md, plus root tracking docs.

## Current Strategy Version

v1.0 (specification frozen; see docs/STRATEGY_SPEC.md).
**No parameter has ever been optimized or changed on
the basis of results (DEC-011).**

## Tests Completed

- 103 tests (core, strategy, signals, replay, backtest,
  backtest metrics, audit incl. injected defects, loader,
  research, MQL5 structure) - all green.

## Test Results

- `python3 -m pytest -q` -> 103 passed.

## Known Issues

- None.

## Known Limitations

- No MT5 terminal / MetaTrader 5 Python package in this
  environment (Linux): MQL5 compilation and forward demo
  (Phase 10) are blocked until MT5 is available.
- Real broker data is git-ignored by design; results are
  reproducible only where the data file is present.

## Research Findings

- EXP-005: OR_Size/ATR_M5(14) on real US30 (36 valid
  days): min 0.97, median ~2.5, max 6.84; 1 of 36 days
  inside the v1.0 band. v1.0's OR filter is
  mis-calibrated for US30 opening volatility.

## Decisions Made

- (Phase 0-4) MQL5 indicator is the Phase 1 deliverable;
  no EA in v1.0. Python engine is the canonical research
  layer. UTC input timestamps; NY via zoneinfo + explicit
  DST rules. Same-bar SL/TP resolves SL first. Pending
  orders expire at 11:30 NY. Spread recorded, never
  filtered. Synthetic data is pipeline validation only.
- DEC-010: gap severity is impact-based, never silent.
- DEC-011: EXP-005 baseline recorded as-is; v1.0
  parameters NOT changed despite the zero-trade outcome.

## Next Exact Task

- NEXT: EXP-006 (PLANNED, requires explicit approval
  before any parameter change): OR-filter recalibration
  study. Measure OR/ATR_M5 on the train block
  (2026-08-13..2026-09-13), pre-register a band
  hypothesis (e.g. wider MaxOR_ATR), then evaluate
  strictly on the held-out OOS block (2026-09-24..
  2026-10-05) with walk-forward + Monte Carlo. Record
  the experiment in EXPERIMENT_LOG.md before running it.

## Remaining Phase Tasks

- [x] Phase 0 - Project Initialization
- [x] Phase 1 - MT5 Indicator v1.0
- [x] Phase 2 - Historical Signal Engine
- [x] Phase 3 - Backtesting Engine
- [x] Phase 4 - Data Quality Audit
- [x] Phase 5 - Baseline Research (EXP-005: 0 trades;
      v1.0 OR filter mis-calibrated for real US30)
- [ ] Phase 6 - Parameter Sensitivity (gated on EXP-006)
- [ ] Phase 7 - Walk Forward (gated on EXP-006)
- [ ] Phase 8 - Monte Carlo (gated on EXP-006)
- [ ] Phase 9 - Multi-Symbol (gated on EXP-006 + data)
- [ ] Phase 10 - Forward Demo (blocked: demo account + MT5)
- [ ] Phase 11 - Final Strategy Assessment
- [ ] Phase 12 - Optional EA (only if justified)

## Do NOT Repeat

- Do not optimize v1.0 parameters to improve historical
  results (DEC-011).
- Do not add an EA before validation completes.
- Do not silently fill missing bars.
- Do not reclassify data defects to make the audit pass;
  the severity model (DEC-010) is impact-based and every
  defect must stay disclosed.

## Important Warnings

- The strategy is NOT assumed profitable. EXP-005 produced
  zero trades; no edge is claimed. Never claim an edge
  without OOS, walk-forward, Monte Carlo, cost sensitivity,
  and forward demo evidence.
- Missing historical data must produce NO TRADE, never a
  synthetic fill.

## Instructions For Next Agent

1. Read this file first.
2. Read ROADMAP.md.
3. Read CHANGELOG.md.
4. Read results/BASELINE_RESULTS.md (EXP-005 evidence).
5. Inspect git status and recent commits.
6. Continue from the current phase (EXP-006 design, or
   as directed).
7. Do not redo completed work.
8. Do not change strategy parameters without documenting
   the experiment first.
