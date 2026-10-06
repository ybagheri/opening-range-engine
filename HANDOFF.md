# PROJECT HANDOFF

## Current Status

- **Phase:** 9 - Multi-Symbol (EXP-007 EXECUTED:
  pooled n=54, net -6.000R — WEAK, borderline FAILED;
  no edge detected)
- **Status:** EXP-007 EXECUTED on 5 real symbols with a
  pre-registered config; all documents updated; working
  tree ready to commit.
- **Overall Progress:** 6 of 13 phases (0-5 complete).

## Phase 9 Evidence `[REAL DATA]` (EXP-007, 2026-10-06)

- Pre-registered identical candidate (OR band [0.25,
  7.00], TP R1.5, costs 0/0; per-symbol point = tick:
  XAUUSD 0.01, EURUSD 0.00001, US-indices 0.1) on 5
  files (all verified 1-minute bars despite `M5`
  filenames; 50k bars each). All 5 audits PASS.
- Per-symbol net R: XAUUSD -1.5 (n=14), EURUSD -1.5
  (n=4), US30 +5.5 (n=12), US500 -6.0 (n=11), NAS100
  -2.5 (n=13).
- Pooled: n=54, net -6.000R, expectancy -0.111R, PF
  0.818; Monte Carlo bootstrap P(profit) 0.236. Verdict:
  WEAK, borderline FAILED — no edge detected (the
  `assess` fall-through word PROMISING is explicitly not
  claimed with negative expectancy and PF<1).
- Only US30 positive and itself n=12 <30; US-index
  correlation makes pooled n=54 an upper bound.
- Registry FROZEN; nothing adopted or tuned on these
  trades. Full record: `results/MULTI_SYMBOL_REPORT.md`.

## Phase 6 Evidence `[REAL DATA]` (EXP-006, 2026-10-06)

- Pre-registered candidate (band chosen from TRAIN
  OR/ATR distribution only, before any OOS run):
  `min_or_atr = 0.25` (unchanged), `max_or_atr = 7.00`
  (ceiling above train max 6.84). Train: 21 valid days,
  min 0.97 / median 2.32 / max 6.84.
- OOS evaluation (2026-09-24..2026-10-05, 10 NY days):
  replay 3 signals; backtest -1.0 / +1.5 / -1.0 R =
  net -0.500R, expectancy -0.167R.
- Sensitivity (OOS slice): TP cells sign-unstable
  (+1.0/-0.75/-0.5/-0.25/0.0); OR-duration cells
  degenerate n=0 (disclosed machinery limitation).
  Monte Carlo n=10,000 both modes; bootstrap P(profit)
  0.255. Assessment: INCONCLUSIVE (n=3 < 30).
  Walk-forward unformable inside 10-day OOS.
- Full-sample context (NOT evidence): 13 trades, net
  +7.000R (train +8.0R in-sample / validation -0.5R /
  OOS -0.5R). Next binding constraint: breakout-extension
  filter (17 full-sample rejections) — future study.
- v1.0 registry FROZEN; candidate NOT adopted. Full
  record: `results/EXP006_OR_RECALIBRATION.md`.

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
- DEC-012: EXP-006 candidate band [0.25, 7.00] tested
  under strict OOS discipline; v1.0 registry stays
  frozen and the candidate is NOT adopted (INCONCLUSIVE,
  OOS n=3).
- DEC-013: EXP-007 pooled result (-6.0R, WEAK/borderline
  FAILED) recorded as evidence with zero tuning —
  registry stays frozen; new hypotheses need NEW
  held-out data, never fits to the 54 trades.

## Next Exact Task

- NEXT: Phase 11 Final Strategy Assessment on current
  evidence (EXP-005 n=0, EXP-006 OOS n=3 INCONCLUSIVE,
  EXP-007 pooled n=54 WEAK/borderline FAILED): draft the
  Continue / Modify / Reject decision on quantitative
  grounds. Lean: the candidate shows no edge; any Modify
  proposal must name a pre-registered test on new held-out
  data. No EA work (Phase 12 needs ROBUST evidence, absent).

## Remaining Phase Tasks

- [x] Phase 0 - Project Initialization
- [x] Phase 1 - MT5 Indicator v1.0
- [x] Phase 2 - Historical Signal Engine
- [x] Phase 3 - Backtesting Engine
- [x] Phase 4 - Data Quality Audit
- [x] Phase 5 - Baseline Research (EXP-005: 0 trades;
      v1.0 OR filter mis-calibrated for real US30)
- [ ] Phase 6 - Parameter Sensitivity (EXP-006 executed:
      OOS n=3 INCONCLUSIVE; OR-duration cells disclose a
      machinery limitation; needs n>=30 to mean anything)
- [ ] Phase 7 - Walk Forward (unformable inside 10-day OOS;
      gated on a larger dataset)
- [ ] Phase 8 - Monte Carlo (machinery run on OOS n=3;
      meaningful only at n>=30)
- [x] Phase 9 - Multi-Symbol (EXP-007: 5 symbols, pooled
      n=54 net -6.0R, WEAK/borderline FAILED; US30 alone
      positive at n=12)
- [ ] Phase 10 - Forward Demo (blocked: demo account + MT5)
- [ ] Phase 11 - Final Strategy Assessment (NEXT: decide
      Continue / Modify / Reject on EXP-005/006/007)
- [ ] Phase 12 - Optional EA (only if justified; currently
      no ROBUST evidence — do not start)

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
  zero trades, EXP-006 OOS n=3 was INCONCLUSIVE, and
  EXP-007 pooled n=54 is WEAK/borderline FAILED (-6.0R);
  no edge is claimed. Never claim an edge
  without OOS, walk-forward, Monte Carlo, cost sensitivity,
  and forward demo evidence.
- Missing historical data must produce NO TRADE, never a
  synthetic fill.

## Instructions For Next Agent

1. Read this file first.
2. Read ROADMAP.md.
3. Read CHANGELOG.md.
4. Read results/BASELINE_RESULTS.md (EXP-005 evidence).
  4b. Read results/EXP006_OR_RECALIBRATION.md + results/MULTI_SYMBOL_REPORT.md.
5. Inspect git status and recent commits.
6. Continue from the current phase (Phase 11 assessment,
  or as directed).
7. Do not redo completed work.
8. Do not change strategy parameters without documenting
   the experiment first.
