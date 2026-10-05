# Roadmap — Opening Range Engine

Current state, verified evidence, and open gaps are summarised in
[`HANDOFF.md`](HANDOFF.md).

## Status legend

- `[x]` complete (implementation + tests + docs + commit + push)
- `[~]` in progress
- `[ ]` not started
- `[B]` blocked (reason stated)

## Phases

### Phase 0 — Project Initialization `[x]`

- **Objective:** repository inspection, architecture, documentation
  structure, roadmap, experiment log, parameter registry, handoff,
  changelog, assumptions.
- **Tasks:** inspect repo; verify environment; create docs; formalize
  Strategy Specification v1.0; create parameter registry.
- **Deliverables:** project skeleton + documentation.
- **Tests:** repository structure verification.
- **Acceptance criteria:** all six tracking documents exist; spec and
  registry are complete; git history clean.
- **Completion date:** 2026-10-05
- **Commit:** see `git log --oneline` (`phase-00: ...`)

### Phase 1 — MT5 Indicator v1.0 `[x]` (implementation + 53 tests green; commit pending)

- **Objective:** implement the indicator with the full state machine.
- **Tasks:** session detection; NY timezone conversion; Opening Range;
  M15 bias; M5 breakout; pullback; M1 trigger; entry/SL/TP; no-trade
  states and reasons; chart visualization; diagnostic panel.
- **Deliverables:** `MQL5/Indicators/NY_OR_Pullback_v1.mq5` + Python
  core modules (`config`, `ny_time`, `bars`, `indicators`, `session`,
  `bias`, `signals`).
- **Tests:** unit tests for every module; DST tests; boundary tests;
  no-look-ahead tests.
- **Acceptance criteria:** full pytest suite green; indicator source
  passes structural checks; all 12 signal states and all 14 no-trade
  reasons implemented.
- **Completion date:** 2026-10-05

### Phase 2 — Historical Signal Engine `[x]`

- **Objective:** reconstruct historical signals without look-ahead.
- **Tasks:** historical signal reconstruction; no-look-ahead validation;
  CSV export; trade/event schema; deterministic replay.
- **Deliverables:** historical signal dataset (CSV).
- **Tests:** determinism (byte-identical reruns), prefix-consistency,
  missing-data handling.
- **Acceptance criteria:** replay over synthetic data produces
  reproducible, schema-conformant CSVs.
- **Completion date:** 2026-10-05

### Phase 3 — Backtesting Engine `[ ]`

- **Objective:** R-based backtester with realistic costs.
- **Tasks:** stop-order entry simulation; SL/TP resolution; spread;
  commission; slippage; R accounting; equity curve; drawdown;
  performance metrics.
- **Deliverables:** reproducible backtest reports.
- **Tests:** fill logic edge cases (same-bar SL/TP, gaps), cost
  accounting, metric correctness on hand-computed examples.
- **Acceptance criteria:** metrics match hand-computed fixtures.
- **Completion date:** TBD

### Phase 4 — Data Quality Audit `[ ]`

- **Objective:** verify input data integrity.
- **Tasks:** missing bars; duplicate bars; timezone; DST; broker symbol
  mapping; market holidays; bad ticks; session boundaries.
- **Deliverables:** `DATA_QUALITY_REPORT.md`.
- **Tests:** audit detects injected defects.
- **Acceptance criteria:** audit runs and reports; real-data audit is
  blocked until broker data is available (documented).
- **Completion date:** TBD

### Phase 5 — Baseline Research `[B]` blocked: requires real US30 M1/M5/M15 data

- Run the exact v1.0 specification without optimization.
- Deliverable: `BASELINE_RESULTS.md` (control experiment).

### Phase 6 — Parameter Sensitivity `[B]` blocked: requires Phase 5

- Test nearby parameters (TP, OR duration, trade window).
- Deliverable: `PARAMETER_SENSITIVITY.md`.

### Phase 7 — Walk Forward `[B]` blocked: requires Phase 5

- Rolling walk-forward analysis.
- Deliverable: `WALK_FORWARD_REPORT.md`.

### Phase 8 — Monte Carlo `[B]` blocked: requires Phase 5

- ≥ 10,000 simulations.
- Deliverable: `MONTE_CARLO_REPORT.md`.

### Phase 9 — Multi-Symbol `[B]` blocked: requires Phase 5

- US30, NAS100, XAUUSD, GER40, EURUSD with identical parameters.
- Deliverable: `MULTI_SYMBOL_REPORT.md`.

### Phase 10 — Forward Demo `[B]` blocked: requires demo account + MT5

- Real-time demo recording of every signal.
- Deliverable: `FORWARD_TEST_REPORT.md`.

### Phase 11 — Final Strategy Assessment `[ ]`

- Decide: Continue / Modify / Reject, on quantitative evidence.

### Phase 12 — Optional EA `[ ]`

- Only if Phases 5–11 justify it. Must reproduce the validated
  strategy exactly; no silent new logic.

## Blockers

- **Real market data:** no MetaTrader 5 terminal or broker feed in
  this environment. Phases 5–10 cannot produce real research results
  until M1/M5/M15 data for the configured symbol is provided. The
  engine is being built and validated end-to-end on deterministic
  synthetic data so that data arrival unblocks research immediately.
- **MT5 compilation:** MQL5 cannot be compiled in this Linux
  environment; compilation must be verified in MetaEditor. Structural
  checks are automated; runtime verification requires MT5.
