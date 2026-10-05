# Strategy Specification v1.0 — MT5 NY Opening Range Pullback Strategy

Formal specification. This document is normative: the MT5 indicator and the
Python research engine must implement exactly these rules. Any deviation is a
spec change and must be recorded in `DECISION_LOG.md` and `CHANGELOG.md`.

**Status: research system. The strategy is NOT assumed profitable.**

## 1. Identity

- **Name:** NY Opening Range Pullback (NY OR Pullback)
- **Version:** 1.0
- **Primary market:** US30 (Dow Jones CFD). The broker symbol name is
  configurable (`US30`, `US30.cash`, `DJI`, `DJ30`, ...). Nothing about the
  symbol is hardcoded.
- **First artifact:** an MT5 **INDICATOR**. No Expert Advisor in v1.0.
- **Multi-market design:** NAS100, XAUUSD, GER40, EURUSD must be testable
  later with the same unmodified logic.

## 2. Timeframe architecture

| Role | Timeframe | Purpose |
| --- | --- | --- |
| Context | M15 | Directional bias, volatility, regime |
| Setup | M5 | Opening Range breakout, breakout validity, pullback, structural confirmation |
| Entry | M1 | Final price-action trigger, exact entry, stop location |

The chart timeframe the indicator is attached to is irrelevant: all data is
requested explicitly per timeframe.

## 3. Session and timezone

- The strategy is built around the **New York cash-session open**.
- No fixed UTC offset is hardcoded. US daylight saving time, standard time,
  broker server timezone, and historical timezone conversion are handled
  internally by converting timestamps to `America/New_York`.
- Primary session open: **09:30 America/New_York**.

## 4. Opening Range (OR)

- OR duration: **15 minutes** (initial research parameter).
- OR window: 09:30:00–09:44:59 New York time, all M1 bars.
- `OR_High` = highest high of all M1 bars in the window.
- `OR_Low` = lowest low of all M1 bars in the window.
- The OR is valid **only if all 15 M1 bars are available**. Missing
  historical data is never silently filled. If the OR cannot be
  reconstructed reliably: **NO TRADE** for that day.

## 5. Opening Range size filter

- `OR_Size = OR_High - OR_Low`
- `ATR_M5 = ATR(14)` on M5, computed from completed candles only.
- Valid only if `0.25 × ATR_M5 <= OR_Size <= 1.00 × ATR_M5`.
- `OR_Size < 0.25 × ATR_M5` → **NO TRADE** (Opening Range too small).
- `OR_Size > 1.00 × ATR_M5` → **NO TRADE** (Opening Range too large).
- These thresholds are INITIAL RESEARCH PARAMETERS and are not optimized in
  Phase 1.

## 6. M15 market bias

Uses `EMA(20)` and `EMA(50)` on M15, completed candles only.

- **BULLISH** (all must hold): `EMA20 > EMA50` AND `Close(M15) > EMA20`
  AND `EMA20[current] > EMA20[previous]`.
- **BEARISH** (all must hold): `EMA20 < EMA50` AND `Close(M15) < EMA20`
  AND `EMA20[current] < EMA20[previous]`.
- Otherwise **NEUTRAL** → **NO TRADE** (Neutral M15 bias).

## 7. Breakout

- A breakout occurs only after the OR has completed.
- Bullish: a **completed M5 candle** with `Close > OR_High`.
- Bearish: a **completed M5 candle** with `Close < OR_Low`.
- Intrabar wicks through the OR do **not** constitute a breakout.
- Bullish breakouts require `M15 Bias = BULLISH`; bearish require
  `M15 Bias = BEARISH`. Counter-trend setups are not allowed in v1.0.
- **Breakout extension limit:** `BreakoutExtension = ABS(M5 Close -
  BrokenORLevel)`. Valid only if `BreakoutExtension <= 0.50 × ATR_M5`,
  else **NO TRADE** (Breakout extension too large).
## 8. Pullback

- After a valid breakout, the system waits for a pullback.
- Bullish: price must retrace toward `OR_High`. The pullback is valid
  when price trades at or below `OR_High + 0.10 × ATR_M5` **and**
  remains above `OR_High - 0.25 × ATR_M5`. A completed candle
  closing below `OR_High - 0.25 × ATR_M5` invalidates the setup
  (**NO TRADE: Pullback invalidated**).
- Bearish: mirrored around `OR_Low`.
- `PullbackLow` (bullish) / `PullbackHigh` (bearish) = the extreme
  price reached during the pullback, identified only from bars that
  occurred after the breakout and before the entry trigger. No future
  candles may be used.

## 9. M1 entry trigger

- **Bullish Signal Bar** (completed M1 candle): `Close > Open` AND
  `Close > previous M1 High` AND `Close > OR_High`.
- **Bearish Signal Bar** (completed M1 candle): `Close < Open` AND
  `Close < previous M1 Low` AND `Close < OR_Low`.

## 10. Entry, stop, targets

- Entry uses a **stop order**, never the signal candle close:
  - BUY: `Entry = SignalBarHigh + 1 point`
  - SELL: `Entry = SignalBarLow - 1 point`
  - "1 point" is converted via the symbol's `SYMBOL_POINT`; no
    decimal precision is assumed.
- **Stop loss:** BUY `SL = PullbackLow - 1 point`; SELL
  `SL = PullbackHigh + 1 point`.
- **Stop distance filter:** `RiskDistance = ABS(Entry - SL)`. Reject
  if `RiskDistance > 1.00 × ATR_M5` (Stop distance too large) or
  `RiskDistance < 0.10 × ATR_M5` (Stop distance too small).
- **Take profit modes** (all three testable, default R1.5):
  - `TP_MODE_R1`: `TP = Entry ± 1.0 × RiskDistance`
  - `TP_MODE_R1_5`: `TP = Entry ± 1.5 × RiskDistance`
  - `TP_MODE_R2`: `TP = Entry ± 2.0 × RiskDistance`
- **No break-even, no trailing stop, no partial exits** in v1.0.

## 11. Trade window and limits

- New entries only between **09:45 and 11:30 America/New_York**. No
  new entries after 11:30 (NO TRADE: Breakout occurred after trading
  window / Signal not confirmed before window close). Existing trades
  may run to TP or SL.
- **Maximum 2 entries per day** (default). After two executed trades:
  no more trades; pending orders are cancelled.
- **One active setup per direction.** Once an entry is triggered, the
  setup is consumed.
- **Daily loss control (research simulation only):** once simulated
  daily loss reaches **-2R**, no additional simulated trades that day.
- **Spread** is recorded (`spread_at_signal`) but never silently
  filters trades in v1.0.
- **Slippage** is configurable (default 0 points; scenarios 1/2/5/10
  points).
- **Commission** is configurable and must be stated in every report.
- **No news filter** in v1.0; trade timestamps are recorded so news
  overlap can be tested later.

## 12. Research integrity (hard requirements)

- **No look-ahead bias.** No future candles, highs/lows, ATR, EMA,
  session information, spread, news, or market state may be used when
  generating a historical signal. Every decision must be reproducible
  as if running live at that exact moment.
- **Bar closure rule.** All calculations use completed candles. An
  in-progress candle may be displayed as "in-progress" but never
  classified as a confirmed signal.
- **Determinism.** Same data + same parameters + same code version →
  same signals, same trades, same results.

## 13. Signal states (indicator)

`WAITING`, `BULLISH_BIAS`, `BEARISH_BIAS`, `OR_FORMING`, `OR_VALID`,
`BREAKOUT_DETECTED`, `WAITING_PULLBACK`, `PULLBACK_CONFIRMED`,
`SIGNAL_CONFIRMED`, `TRADE_ACTIVE`, `SETUP_INVALIDATED`, `NO_TRADE`.

## 14. No-trade reasons (machine- and human-readable)

`Neutral M15 bias`, `Opening Range too large`, `Opening Range too
small`, `Opening Range incomplete (missing bars)`, `Breakout occurred
after trading window`, `Breakout extension too large`, `Pullback
invalidated`, `Stop distance too large`, `Stop distance too small`,
`Daily trade limit reached`, `Signal not confirmed before window
close`, `Same-direction setup already active`, `Daily loss limit
reached`, `Insufficient data`.

## 15. Visualization and panel

The indicator displays: OR High, OR Low, Breakout, Pullback, Signal
Bar, Entry, Stop Loss, Take Profit, BUY signal, SELL signal, NO TRADE
status, and the current strategy state. It does **not** display EMAs,
trend channels, generic S/R, or decorative graphics unless diagnostic
visualization is explicitly enabled. An optional panel shows the full
state (Strategy, Symbol, Server Time, New York Time, Session, M15
Bias, OR High/Low/Size, ATR M5, Breakout, Pullback, Signal, Entry,
SL, TP, R:R, Trades Today, Status, Reason).

## 16. Configuration (all inputs)

`OpeningRangeMinutes=15`, `ContextTimeframe=M15`,
`SetupTimeframe=M5`, `EntryTimeframe=M1`, `EMAFast=20`,
`EMASlow=50`, `ATRPeriod=14`, `MinOR_ATR=0.25`, `MaxOR_ATR=1.00`,
`MaxBreakoutExtension_ATR=0.50`, `PullbackLower_ATR=0.25`,
`PullbackUpper_ATR=0.10`, `MinStop_ATR=0.10`, `MaxStop_ATR=1.00`,
`TradeStart=09:45 NY`, `TradeEnd=11:30 NY`, `MaxTradesPerDay=2`,
`RiskPercent=0.50`, `TPMode=R1.5`.

## 17. Trade record schema (minimum)

`Date, Time, Symbol, Direction, Session, OR High, OR Low, OR Size,
ATR, M15 EMA20, M15 EMA50, Entry, SL, TP, RiskDistance, R Multiple,
Spread, Commission, Slippage, Exit, Exit Time, Result, MAE, MFE`.

## 18. Trade result classification

`WIN`, `LOSS`, `BREAKEVEN`, `CANCELLED`, `EXPIRED`, each with
`R_Result` (e.g. `+1.50R`, `-1.00R`).

## 19. Performance metrics (every report)

- **Basic:** number of trades, win rate, loss rate, average win,
  average loss, expectancy, net R, profit factor.
- **Risk:** maximum drawdown, maximum drawdown in R, maximum losing
  streak, maximum winning streak, average drawdown, recovery factor.
- **Distribution:** median R, standard deviation of R, percentile
  results.
- **Time:** monthly, yearly, session, and day-of-week performance.

Expectancy = `(WinRate × AverageWinR) + (LossRate × AverageLossR)`
with losses as negative values.

## 20. Validation discipline

- Dataset split: Training 60% / Validation 20% / final Out-of-Sample
  20%. The final OOS dataset remains untouched during parameter
  optimization. Exact dates are documented.
- Rolling walk-forward with documented windows; training, validation,
  and OOS performance are reported separately.
- Monte Carlo with at least 10,000 simulations (random trade
  ordering, bootstrap resampling, losing-streak analysis, drawdown
  distribution).
- Robustness testing across nearby parameters (TP
  1.0/1.25/1.5/1.75/2.0 R; OR duration 10/15/20/30 m; trade window
  60/90/120/150/180 m). Nearby-parameter instability → `POSSIBLE
  OVERFITTING`; stability → `ROBUST REGION`.
- Multi-symbol validation uses the same unmodified parameters first.
- Final outcome classification: `PROMISING`, `INCONCLUSIVE`, `WEAK`,
  `FAILED`, `OVERFIT`, or `ROBUST` — supported by quantitative
  evidence, never by net profit alone.

