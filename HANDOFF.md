# PROJECT HANDOFF

## Current Status

- **Phase:** 1 — MT5 Indicator v1.0 + Python Core
- **Status:** COMPLETE (53 tests green; to be committed)
- **Overall Progress:** 2 of 13 phases (0–12). Phase 2 next.

## Last Completed Work

- Phase 1 (resumed after killed session): `engine/session.py`, `engine/bias.py`, `engine/signals.py`, `MQL5/Indicators/NY_OR_Pullback_v1.mq5`, and 4 test files (53 tests green). Orphaned pre-kill modules (`config`, `ny_time`, `bars`, `indicators`) audited and kept.
- Phase 0: repository inspection, environment verification, project
  skeleton, and full documentation structure created.
- Environment verified: Python 3.10.12, pytest available, git
  configured (`Winuser <ybagheir83@gmail.com>`), GitHub SSH push
  access confirmed (`git@github.com:ybagheri/opening-range-engine.git`).

## Current Implementation

- Python core (config, ny_time, bars, indicators, session, bias, signals) + MQL5 indicator v1.0 structural draft.
- Files: `README.md`, `README_FA.md` (Persian),
  `docs/STRATEGY_SPEC.md`, `docs/PARAMETER_REGISTRY.md`,
  `docs/ARCHITECTURE.md`, plus the tracking documents in the repo root.

## Current Strategy Version

v1.0 (specification frozen; see `docs/STRATEGY_SPEC.md`)

## Current Parameters

See `docs/PARAMETER_REGISTRY.md`. All v1.0 values are INITIAL or
FIXED; none have been optimized.

## Tests Completed

- 53 tests: `test_core.py`, `test_strategy.py`, `test_signals.py`, `test_mql5_structure.py` — all green.

## Test Results

- N/A

## Known Issues

- None.

## Known Limitations

- No MT5 terminal / MetaTrader 5 Python package is available in this
  environment (Linux). Real broker data is therefore not yet loaded;
  Phases that require live MT5 data (real-data baseline, forward demo)
  are blocked until data is provided. A deterministic synthetic data
  generator is planned so the pipeline can be validated end-to-end.

## Research Findings

- None yet.

## Decisions Made

- MQL5 indicator is the Phase 1 deliverable; no EA in v1.0.
- Python `engine/` is the canonical research layer; MQL5 mirrors it.
- Input data timestamps are assumed UTC; NY conversion via `zoneinfo`
  with explicit US DST rules.
- Same-bar SL/TP ambiguity resolves conservatively (SL first).

## Files Changed

- `.gitignore`, `README.md`, `README_FA.md`, `docs/STRATEGY_SPEC.md`,
  `docs/PARAMETER_REGISTRY.md`, `docs/ARCHITECTURE.md`,
  `HANDOFF.md`, `ROADMAP.md`, `CHANGELOG.md`, `EXPERIMENT_LOG.md`,
  `DECISION_LOG.md`, `ASSUMPTIONS.md`, `data/.gitkeep`,
  `results/.gitkeep`

## Last Git Commit

See `git log --oneline -1` (phase-00: project initialization and documentation skeleton)

## Last Git Push

Successful (verify with `git status` after pull)

## Next Exact Task

- Phase 2: implement `engine/data/` (schema, loader, synthetic), `engine/replay.py`, `engine/export.py` with determinism + prefix-consistency tests (EXP-001, EXP-002).

## Remaining Phase Tasks

- [ ] Phase 1 — MT5 Indicator v1.0
- [ ] Phase 2 — Historical Signal Engine
- [ ] Phase 3 — Backtesting Engine
- [ ] Phase 4 — Data Quality Audit
- [ ] Phase 5 — Baseline Research (blocked: needs real MT5 data)
- [ ] Phase 6 — Parameter Sensitivity (blocked: needs Phase 5)
- [ ] Phase 7 — Walk Forward (blocked: needs Phase 5)
- [ ] Phase 8 — Monte Carlo (blocked: needs Phase 5)
- [ ] Phase 9 — Multi-Symbol (blocked: needs Phase 5)
- [ ] Phase 10 — Forward Demo (blocked: needs demo account)
- [ ] Phase 11 — Final Strategy Assessment
- [ ] Phase 12 — Optional EA (only if justified)

## Do NOT Repeat

- Do not optimize v1.0 parameters to improve historical results.
- Do not add an EA before validation completes.
- Do not silently fill missing bars.

## Important Warnings

- The strategy is NOT assumed profitable. Never claim an edge without
  OOS, walk-forward, Monte Carlo, cost sensitivity, and forward demo
  evidence.
- Missing historical data must produce NO TRADE, never a synthetic fill.

## Instructions For Next Agent

1. Read this file first.
2. Read ROADMAP.md.
3. Read CHANGELOG.md.
4. Inspect git status and recent commits.
5. Continue from the current phase.
6. Do not redo completed work.
7. Do not change strategy parameters without documenting the experiment.
