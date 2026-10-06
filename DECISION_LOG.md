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

## DEC-010 — Gap severity is impact-based, never silent

- **Decision:** The data-quality audit classifies gaps by signal impact: ERROR if a gap intersects the OR (09:30-09:45 NY) or trade (09:45-11:30 NY) window; WARNING for gaps outside the signal windows (disclosed); INFO for recurring scheduled broker breaks (same clock-time pattern on >= 3 distinct NY days, >= 15 bars) and multi-day weekend breaks.
- **Reason:** Real broker data contains scheduled daily breaks (23:58->01:01 UTC) and benign overnight feed gaps that must not be silently forgiven (they are disclosed), but must not block research when they cannot affect any signal. Gaps inside signal windows remain hard errors because they silently corrupt M5 breakout/pullback signals.
- **Date:** 2026-10-06

## DEC-011 — EXP-005 baseline recorded as-is; v1.0 parameters NOT changed

- **Decision:** The Phase 5 baseline on real US30 data (0 trades in 46 days) is recorded verbatim. Despite the zero-trade outcome, no parameter (notably MaxOR_ATR) was altered.
- **Reason:** The baseline is the control experiment; changing parameters to "fix" the result would destroy its evidentiary value. The observed OR/ATR_M5 distribution (median ~2.5 vs the frozen band [0.25, 1.00]) is a finding, and any recalibration must go through a pre-registered, OOS-validated   experiment (EXP-006, PLANNED).
- **Date:** 2026-10-06

## DEC-012 — EXP-006 candidate NOT adopted; v1.0 stays frozen

- **Decision:** The pre-registered candidate band [0.25, 7.00]
  x ATR_M5(14) remains a research candidate with an INCONCLUSIVE
  OOS record (n=3, net -0.500R). It is not written into the
  parameter registry, `StrategyConfig` defaults, or the MQL5
  indicator. v1.0 values are unchanged.
- **Reason:** Adoption requires OOS n>=30 plus walk-forward and
  Monte Carlo confirmation under the `assess` rules; n=3 meets
  none of that. The band was selected from the train OR/ATR
  distribution (not from P&L), and the train/OOS split
  (+8.0R in-sample vs -0.5R OOS, both tiny samples) confirms
  that only held-out evidence may move parameters.
- **Date:** 2026-10-06

## DEC-013 — EXP-007 pooled result recorded as evidence, zero tuning

- **Decision:** The multi-symbol outcome (pooled n=54, net
  -6.000R, expectancy -0.111R, PF 0.818 — WEAK, borderline
  FAILED) is recorded as evidence for Phase 11. No parameter
  was tuned on these 54 trades, none adopted; the registry,
  `StrategyConfig` defaults, and MQL5 inputs are unchanged.
- **Reason:** Tuning on the evaluation sample would destroy its
  evidentiary value (DEC-011 precedent). Also noted in the
  record: the `assess` fall-through word for these numbers reads
  PROMISING, which is explicitly rejected in the report — with
  negative expectancy and PF<1 the honest reading is WEAK
  leaning FAILED.
- **Date:** 2026-10-06

## DEC-014 — Final assessment: REJECT; close Phases 10/12 as not-recommended

- **Decision:** The strategy is REJECTED for forward demo, EA
  development, and live use in both tested forms (v1.0: untestable,
  never trades; candidate: WEAK/borderline FAILED at pooled n=54,
  net -6.000R, expectancy -0.111R, PF 0.818). Phases 10 and 12 are
  closed as not-recommended. The pipeline and all evidence are
  retained for future research. Re-entry requires a new hypothesis
  pre-registered against new held-out data with OOS n>=30 plus
  walk-forward + Monte Carlo confirmation at stated costs; current
  data is spent as evaluation material.
- **Reason:** No assessable sample shows an edge; costs (run at zero)
  can only worsen the result; no modification direction has a priori
  support, so Modify would be overfitting by definition.
- **Date:** 2026-10-06
