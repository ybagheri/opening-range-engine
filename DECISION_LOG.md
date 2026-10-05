# Decision Log

Architectural and research decisions. Each entry states the decision,
the reason, and the date.

---

## DEC-001 — MQL5 indicator first, no EA in v1.0

- **Decision:** The first implementation is an MT5 indicator that
  identifies and displays setups without executing trades.
- **Reason:** The specification requires research and validation
  before any automation. An EA is only considered if later phases
  demonstrate robustness.
- **Date:** 2026-10-05

## DEC-002 — Python engine is the canonical research layer

- **Decision:** `engine/` (Python) implements the strategy rules and
  produces all measurements; the MQL5 indicator mirrors the same
  rules for chart visualization.
- **Reason:** The Linux environment has no MT5 terminal; Python
  provides testability, determinism, and reproducibility. The
  indicator remains the user-facing artifact inside MT5.
- **Date:** 2026-10-05

## DEC-003 — UTC input timestamps, explicit US DST rules

- **Decision:** Historical bar data is assumed to carry UTC
  timestamps. New York time is derived with `zoneinfo` and explicit
  US daylight-saving transition rules.
- **Reason:** The specification forbids a hardcoded fixed UTC
  offset; DST must be handled correctly across history.
- **Date:** 2026-10-05

## DEC-004 — Same-bar SL/TP ambiguity resolves to SL first

- **Decision:** If a single bar can reach both the stop loss and the
  take profit, the backtest assumes the stop loss is hit first.
- **Reason:** Conservative; avoids overstating performance in
  intrabar ambiguity. Documented as an INITIAL parameter so it can
  be tested later with higher-resolution data.
- **Date:** 2026-10-05

## DEC-005 — Unfilled pending orders expire at 11:30 NY

- **Decision:** Entry stop orders that are not filled by the end of
  the trade window (11:30 America/New_York) are cancelled.
- **Reason:** The specification forbids new entries after 11:30;
  leaving orders active would create entries outside the window.
- **Date:** 2026-10-05

## DEC-006 — Spread is recorded, never filtered, in v1.0

- **Decision:** `spread_at_signal` is stored on every signal; no
  trade is silently discarded because of spread.
- **Reason:** Explicit specification requirement; a spread filter is
  a later, independently validated experiment.
- **Date:** 2026-10-05

## DEC-007 — Synthetic data is for pipeline validation only

- **Decision:** A deterministic synthetic M1 generator is used to
  test the pipeline end-to-end. Results derived from it are labelled
  `[SYNTHETIC]` and are never market evidence.
- **Reason:** Real broker data is unavailable in this environment;
  the pipeline must still be verifiable before data arrives.
- **Date:** 2026-10-05

---

## DEC-008 — Research machinery built before data arrives

- **Decision:** Implement splits, walk-forward windows, seeded Monte Carlo, sensitivity grid, and outcome classifier now; validate on synthetic; run on real data later.
- **Reason:** Phases 5+ are data-blocked, but the methodology must be frozen before data arrives (avoids fitting the method to the data). Synthetic verdict correctly returns INCONCLUSIVE at n=4.
- **Date:** 2026-10-05

---

## DEC-009 — TPMode extended to spec grid values

- **Decision:** TPMode gains R1_25 (1.25) and R1_75 (1.75) so the spec-mandated sensitivity grid TP 1.0/1.25/1.5/1.75/2.0 R is fully testable.
- **Reason:** Registry lists TP scenarios R1/R1.5/R2 as INITIAL and spec section 20 requires the 5-point sweep; missing enum members made the grid unrepresentable. Baseline default unchanged (R1.5).
- **Date:** 2026-10-05
