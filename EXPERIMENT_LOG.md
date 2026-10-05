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
- **EXP-003** `[SYNTHETIC]` — Phase 3 backtest accounting: hand-
  computed fixture with known fills, costs, and R results.
- **EXP-004** `[SYNTHETIC]` — Phase 3 cost sensitivity: slippage
  0/1/2/5/10 points and commission scenarios on synthetic data.
- **EXP-005** — Phase 5 baseline on real US30 data (BLOCKED: data).
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

- **EXP-006+** — Phases 6–9 research experiments (BLOCKED: data).
