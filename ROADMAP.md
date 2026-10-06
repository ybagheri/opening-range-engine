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

### Phase 3 — Backtesting Engine `[x]`

- **Objective:** R-based backtester with realistic costs.
- **Tasks:** stop-order entry simulation; SL/TP resolution; spread;
  commission; slippage; R accounting; equity curve; drawdown;
  performance metrics.
- **Deliverables:** reproducible backtest reports.
- **Tests:** fill logic edge cases (same-bar SL/TP, gaps), cost
  accounting, metric correctness on hand-computed examples.
- **Acceptance criteria:** metrics match hand-computed fixtures.
- **Completion date:** 2026-10-05

### Phase 4 — Data Quality Audit `[x]`

- **Objective:** verify input data integrity.
- **Tasks:** missing bars; duplicate bars; timezone; DST; broker symbol
  mapping; market holidays; bad ticks; session boundaries.
- **Deliverables:** `DATA_QUALITY_REPORT.md`.
- **Tests:** audit detects injected defects.
- **Acceptance criteria:** audit runs and reports; real-data audit is
  blocked until broker data is available (documented).
- **Completion date:** 2026-10-05

### Phase 5 — Baseline Research `[x]` (EXECUTED 2026-10-06, EXP-005)

- Run the exact v1.0 specification without optimization.
- Deliverable: `results/BASELINE_RESULTS.md` (control experiment).
- **Result:** 0 trades in 46 NY days. Audit PASS (0 errors).
  The frozen OR-size band [0.25, 1.00] x ATR_M5(14) rejects
  100% of valid days on real US30 (observed OR/ATR_M5 median
  ~2.5, range 0.97-6.84). Assessment: INCONCLUSIVE (n=0).
  No parameter changed; EXP-006 recalibration study PLANNED.

### Phase 6 — Parameter Sensitivity `[~]` EXP-006 executed (OOS n=3, INCONCLUSIVE)

- Test nearby parameters (TP, OR duration, trade window).
- Deliverable: `PARAMETER_SENSITIVITY.md`.
- EXP-006 (2026-10-06): pre-registered band [0.25, 7.00]
  evaluated strictly OOS — 3 signals, net -0.500R; TP cells
  sign-unstable; OR-duration cells degenerate (disclosed
  machinery limitation: fixed [09:30,09:45) window vs N-bar
  expectation in `session.py`). Meaningful sensitivity needs
  n>=30. Record: `results/EXP006_OR_RECALIBRATION.md`.

### Phase 7 — Walk Forward `[~]` unformable inside 10-day OOS; gated on larger dataset

- Rolling walk-forward analysis.
- Deliverable: `WALK_FORWARD_REPORT.md`.
- No 20d/5d window fits the 10-day OOS block; full-sample
  WF would mix band-selection data into tests (OOS
  violation) and was not run as evidence.

### Phase 8 — Monte Carlo `[~]` run on OOS n=3 (bootstrap P(profit) 0.255); meaningful only at n>=30

- ≥ 10,000 simulations.
- Deliverable: `MONTE_CARLO_REPORT.md`.

### Phase 9 — Multi-Symbol `[x]` EXECUTED 2026-10-06 (EXP-007)

- XAUUSD, EURUSD, US30, US500, NAS100 (50k 1-min bars each;
  `M5` filenames mislabeled — verified before use) with the
  identical EXP-006 candidate; per-symbol point = tick size.
- Result: XAUUSD -1.5R (n=14), EURUSD -1.5R (n=4), US30
  +5.5R (n=12), US500 -6.0R (n=11), NAS100 -2.5R (n=13).
  Pooled n=54, net -6.000R, expectancy -0.111R, PF 0.818,
  bootstrap P(profit) 0.236 → WEAK, borderline FAILED.
- Deliverable: `results/MULTI_SYMBOL_REPORT.md`.

### Phase 10 — Forward Demo `[B]` blocked: requires demo account + MT5

- Real-time demo recording of every signal.
- Deliverable: `FORWARD_TEST_REPORT.md`.

### Phase 11 — Final Strategy Assessment `[~]` NEXT: Continue / Modify / Reject on EXP-005 (n=0) + EXP-006 (OOS n=3) + EXP-007 (pooled n=54, WEAK/borderline FAILED)

- Decide: Continue / Modify / Reject, on quantitative evidence.
- EXP-005 flags a Modify candidate (OR-filter calibration),
  gated on the EXP-006 experiment.

### Phase 12 — Optional EA `[ ]`

- Only if Phases 5–11 justify it. Must reproduce the validated
  strategy exactly; no silent new logic.

## Blockers

- **v1.0 parameter calibration (PARTIALLY UNBLOCKED
  2026-10-06):** EXP-006 confirmed the EXP-005 diagnosis
  (widened band [0.25, 7.00] admits 13 vs 0 signals) but
  OOS n=3 is INCONCLUSIVE, so the candidate is NOT adopted
  (DEC-012) and v1.0 stays frozen. First n>=30 sample
  (EXP-007 pooled n=54: net -6.0R, expectancy -0.111R, PF
  0.818) shows no edge — WEAK, borderline FAILED (DEC-013).
  Any new hypothesis must be pre-registered against NEW
  held-out data, never fit to the 54 trades.
- **MT5 terminal / demo account:** no MetaTrader 5 terminal in
  this environment (Linux). Forward demo (Phase 10) and MQL5
  compilation verification require MT5; MQL5 structural checks
  are automated, runtime verification requires MetaEditor.
- **Real market data (EXPANDED 2026-10-06):** five
  50k-bar 1-minute files arrived (audits all PASS) and Phase 9
  executed on them. GER40 still missing; forward demo still
  needs MT5 + demo account.
