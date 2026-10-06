# Changelog

All meaningful changes to the project are recorded here. Dates use
ISO format. Commit hashes are filled after each commit.

## 2026-10-06 — Phase 5: baseline research on real US30 data (EXP-005)

### Added

- `engine/data/loader.py`: MT5 export-format support —
  case-insensitive headers, `TickVolume`/`RealVolume`
  mapped to volume, `%Y.%m.%d %H:%M[:%S]` timestamps.
- `tests/test_loader.py` — 6 broker-format loader tests.
- `engine/quality/audit.py`: impact-based gap severity
  model (ERROR inside signal windows; WARNING outside;
  INFO for recurring scheduled daily breaks + weekend
  breaks) and a trade-window completeness check per NY
  day; `render_report(report, source=...)` provenance
  note ("EXECUTED" for real data).
- `tests/test_audit.py`: 6 new/updated tests
  (signal-window gap ERROR, overnight gap WARNING,
  scheduled-break INFO, trade-window coverage,
  partial-day WARNING, real-source rendering).
- `results/BASELINE_RESULTS.md` — full EXP-005 record.
- `results/DATA_QUALITY_REPORT_REAL.md` — real-data
  audit (PASS, 0 errors; all defects disclosed).

### Changed

- EXP-005 executed on `data/US30_M1_UTC.csv`
  (50,000 real M1 bars, 46 NY days): audit PASS;
  replay 46 days -> 0 signals (35x OR too large,
  10x OR incomplete, 1x breakout extension too
  large); backtest 0 trades; sensitivity grid all
  cells n=0; walk-forward 22 windows; Monte Carlo
  n=10,000 (empty R series); assessment INCONCLUSIVE.
- Finding: frozen v1.0 OR band [0.25, 1.00] x
  ATR_M5(14) rejects 100% of valid days (observed
  OR/ATR_M5 median ~2.5). No parameter changed
  (DEC-011); EXP-006 recalibration study PLANNED.

### Tests

- 103 tests green (was 92).

### Decisions

- DEC-010: gap severity is impact-based, never silent.
- DEC-011: baseline recorded as-is; v1.0 parameters
  NOT changed despite the zero-trade outcome.

## 2026-10-05 — Phase 1: MT5 Indicator v1.0 + Python Core

### Added

- `engine/config.py` — StrategyConfig mirror of the parameter registry.
- `engine/ny_time.py` — NY conversion with zoneinfo + explicit DST rules.
- `engine/bars.py` — Bar model, M1→M5/M15 resampling, contiguity checks.
- `engine/indicators.py` — MT5-convention EMA + Wilder ATR.
- `engine/session.py` — OR reconstruction + all-bars-present validity.
- `engine/bias.py` — M15 EMA(20)/EMA(50) bias with slope confirmation.
- `engine/signals.py` — breakout/pullback/M1-trigger/entry-SL-TP state
  machine (all 12 states, all 14 no-trade reasons).
- `MQL5/Indicators/NY_OR_Pullback_v1.mq5` — research indicator v1.0.
- `tests/test_core.py`, `tests/test_strategy.py`,
  `tests/test_signals.py`, `tests/test_mql5_structure.py` — 53 tests.

## 2026-10-05 — Research machinery (splits/WF/MC/sensitivity/assess, 92 tests)

- `engine/research/` (splits, walk_forward, montecarlo, sensitivity, assessment) + `tests/test_research.py` (9 tests).
- `TPMode` extended R1_25/R1_75 (spec grid); window sensitivity documented as structural placeholder.
- `results/BASELINE_RESULTS.md` procedure scaffold (blocked, synthetic reference inside).

## 2026-10-05 — Phase 0: Project Initialization (details below unchanged)

### Added (Phase 0)

- `README.md` (English) with Persian documentation link at the top.
- `README_FA.md` (Persian documentation).
- `docs/STRATEGY_SPEC.md` — formal Strategy Specification v1.0.
- `docs/PARAMETER_REGISTRY.md` — all 32 parameters with values and
  FIXED/INITIAL/OPTIMIZABLE/DERIVED classifications.
- `docs/ARCHITECTURE.md` — system architecture, data flow, timezone
  model, no-look-ahead contract, MQL5 indicator contract.
- `HANDOFF.md`, `ROADMAP.md`, `CHANGELOG.md`, `EXPERIMENT_LOG.md`,
  `DECISION_LOG.md`, `ASSUMPTIONS.md`.
- `data/` and `results/` placeholder directories.
- `.gitignore`.

### Changed

- Nothing (initial commit).

### Fixed

- Nothing.

### Research

- Strategy v1.0 specification frozen. No parameter has been optimized.
- Baseline parameters recorded in the registry as the control
  experiment.

### Decisions

- MQL5 indicator is the Phase 1 deliverable; no EA in v1.0.
- Python `engine/` is the canonical research layer.
- Input data timestamps are assumed UTC.
- Same-bar SL/TP ambiguity resolves conservatively (SL first).

### Commit

- `phase-00: project initialization and documentation skeleton`
  (hash filled at commit time)

### Environment Verified

- Python 3.10.12; pytest 9.1.1; git 2.34.1; GitHub SSH push
  access confirmed.
