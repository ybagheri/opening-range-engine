# Parameter Registry — Strategy v1.0

Every parameter has a classification:

- **FIXED** — structural rule of the strategy; changing it changes the strategy
  itself and requires a new specification version.
- **INITIAL** — initial research parameter. Never optimized to improve
  historical performance; may only be changed through a documented experiment
  with a logical, statistically defensible hypothesis.
- **OPTIMIZABLE** — may be researched in later phases, only inside
  walk-forward / OOS discipline.
- **DERIVED** — computed from other parameters or market data; never set by hand.

## Registry

| # | Parameter | Value | Type | Notes |
| --- | --- | --- | --- | --- |
| 1 | Opening Range duration | 15 min | INITIAL | 09:30:00–09:44:59 America/New_York |
| 2 | Context timeframe | M15 | FIXED | Bias, volatility, regime |
| 3 | Setup timeframe | M5 | FIXED | Breakout + pullback detection |
| 4 | Entry timeframe | M1 | FIXED | Final trigger |
| 5 | EMA fast | 20 | INITIAL | M15 |
| 6 | EMA slow | 50 | INITIAL | M15 |
| 7 | ATR period | 14 | INITIAL | M5, completed candles only |
| 8 | Min OR / ATR | 0.25 | INITIAL | OR below → NO TRADE |
| 9 | Max OR / ATR | 1.00 | INITIAL | OR above → NO TRADE |
| 10 | Max breakout extension | 0.50 ATR | INITIAL | First breakout candle close beyond OR |
| 11 | Pullback lower band | 0.25 ATR | INITIAL | Close below OR level − 0.25 ATR invalidates |
| 12 | Pullback upper band | 0.10 ATR | INITIAL | Price must trade at/below OR level + 0.10 ATR |
| 13 | Min stop distance | 0.10 ATR | INITIAL | RiskDistance below → NO TRADE |
| 14 | Max stop distance | 1.00 ATR | INITIAL | RiskDistance above → NO TRADE |
| 15 | Trade window start | 09:45 NY | INITIAL | No new entries before |
| 16 | Trade window end | 11:30 NY | INITIAL | No new entries after |
| 17 | Max trades per day | 2 | INITIAL | Pending orders cancelled at limit |
| 18 | Max active setups per direction | 1 | FIXED | Setup consumed on trigger |
| 19 | Daily loss control | -2R | INITIAL | Research simulation rule |
| 20 | Risk percent per trade | 0.50% | INITIAL | Scenarios 0.25/0.50/0.75/1.00% |
| 21 | TP mode | R1.5 | INITIAL | R1 / R1.5 / R2 all testable |
| 22 | Break-even | disabled | FIXED (v1.0) | Future research only |
| 23 | Trailing stop | disabled | FIXED (v1.0) | Future research only |
| 24 | Partial exits | disabled | FIXED (v1.0) | Future research only |
| 25 | News filter | disabled | FIXED (v1.0) | Timestamps recorded for later testing |
| 26 | Spread filter | disabled (record only) | FIXED (v1.0) | `spread_at_signal` recorded |
| 27 | Slippage | 0 points | INITIAL | Scenarios 1/2/5/10 points |
| 28 | Commission | configurable | INITIAL | Must be stated in every report |
| 29 | Entry buffer | 1 point | FIXED | Symbol SYMBOL_POINT |
| 30 | Stop buffer | 1 point | FIXED | Symbol SYMBOL_POINT |
| 31 | Same-bar SL/TP resolution | SL first | INITIAL | Conservative; documented assumption |
| 32 | Pending order expiry | 11:30 NY | INITIAL | Unfilled entries cancelled at window close |

## Change control

- Any change to an INITIAL parameter requires: hypothesis, experiment ID in
  `EXPERIMENT_LOG.md`, and a `DECISION_LOG.md` entry.
- The registry is the single source of truth; `engine/config.py` and the MQL5
  indicator inputs must mirror it.
- v1.0 baseline values above are the control experiment. They are not to be
  tuned to improve historical performance.
