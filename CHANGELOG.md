# Changelog

All meaningful changes to the project are recorded here. Dates use
ISO format. Commit hashes are filled after each commit.

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
