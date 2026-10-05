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

## PLANNED experiments (not yet run)

- **EXP-001** `[SYNTHETIC]` — Phase 2 deterministic replay: same
  data + same parameters → byte-identical signal CSV across runs.
- **EXP-002** `[SYNTHETIC]` — Phase 2 prefix-consistency: truncating
  data at any bar never changes earlier decisions (no-look-ahead).
- **EXP-003** `[SYNTHETIC]` — Phase 3 backtest accounting: hand-
  computed fixture with known fills, costs, and R results.
- **EXP-004** `[SYNTHETIC]` — Phase 3 cost sensitivity: slippage
  0/1/2/5/10 points and commission scenarios on synthetic data.
- **EXP-005** — Phase 5 baseline on real US30 data (BLOCKED: data).
- **EXP-006+** — Phases 6–9 research experiments (BLOCKED: data).
