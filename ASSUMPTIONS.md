# Assumptions

Every assumption is explicit. If an assumption is violated, the
affected results must be re-evaluated.

## Data

- A1. Historical bar data timestamps are **UTC**. If broker-local
  timestamps are used, the loader must be told the offset and the
  assumption re-validated.
- A2. M1 bars are the base resolution; M5 and M15 bars are derived
  by exact aggregation of M1 bars (no gaps, no overlaps).
- A3. The broker symbol name is configurable and never hardcoded
  (`US30`, `US30.cash`, `DJI`, `DJ30`, ...).
- A4. Symbol point size and digits are read from configuration /
  `SYMBOL_POINT`; no decimal precision is assumed.

## Market

- A5. The New York cash session opens at 09:30 America/New_York on
  regular trading days.
- A6. US daylight saving time follows the current US rules (2nd
  Sunday March, 1st Sunday November).
- A7. Market holidays (e.g. NY close days) may produce missing
  sessions; missing data is never silently filled.

## Strategy

- A8. Signals are generated only from completed candles.
- A9. No look-ahead is permitted in any form.
- A10. Transaction costs (spread, commission, slippage) must be
  included in final validation; defaults are stated in every report.
- A11. The strategy is NOT assumed profitable at any stage.

## Environment

- A12. The research engine runs on Python 3.10+ with only the
  standard library (no third-party runtime dependencies).
- A13. The MQL5 indicator is compiled in MetaEditor; this Linux
  environment cannot compile MQL5, so structural checks are
  automated and compilation is verified in MT5.
- A14. Real broker data availability is outside the control of this
  repository; phases requiring it are explicitly blocked until data
  is provided.

## Simulation

- A15. Stop-order entries fill at the exact stop price plus
  configured slippage (no partial fills, no requotes).
- A16. If one bar reaches both SL and TP, SL is assumed hit first
  (conservative).
- A17. Unfilled pending orders are cancelled at 11:30 NY.
- A18. Position sizing uses `RiskAmount / MonetaryLossAtStop`; fixed
  lot sizing is not used for portfolio-level risk.
