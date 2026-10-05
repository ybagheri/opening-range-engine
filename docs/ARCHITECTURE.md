# Architecture — Opening Range Engine

## Design goals

1. **Research-first.** The Python engine (`engine/`) is the canonical
   measurement layer. The MQL5 indicator is the chart-facing
   implementation of the *same* rules; it executes nothing.
2. **No look-ahead, by construction.** Every module consumes only
   completed bars up to and including the decision bar. The replay
   engine processes bars strictly in time order and never indexes
   beyond the current position.
3. **Determinism.** Pure functions of `(data, parameters)`. No wall
   clock, no randomness outside Monte Carlo (seeded), no hidden state.
4. **Symbol-agnostic.** Point size, digits, and symbol name are inputs,
   never assumptions.
5. **Testability.** Timezone/DST math, session boundaries, bias,
   breakout, pullback, trigger, stop arithmetic, and backtest
   accounting each have dedicated unit tests; integration tests replay
   full synthetic sessions; replay tests prove byte-identical output
   across runs.

## Components

```text
engine/
├── config.py        StrategyConfig: typed, validated parameters (mirrors the registry)
├── ny_time.py       America/New_York conversion, US DST rules, session windows
├── bars.py          Bar dataclass, timeframe resampling (M1 → M5/M15), completeness checks
├── indicators.py    EMA and Wilder ATR on completed bars only
├── session.py       Opening Range reconstruction + validity (all-bars-present rule)
├── bias.py          M15 EMA(20)/EMA(50) directional bias
├── signals.py       State machine: OR → bias → breakout → pullback → M1 trigger
├── data/
│   ├── schema.py    Trade/event record schemas (CSV column contracts)
│   ├── loader.py    CSV bar loader with validation
│   └── synthetic.py Deterministic synthetic M1 generator for pipeline testing
├── replay.py        Historical signal reconstruction (no-look-ahead replay)
├── export.py        CSV export of signals and trades
├── backtest/
│   ├── costs.py     Spread / commission / slippage cost model
│   ├── simulator.py Stop-order fill, SL/TP resolution, R accounting
│   ├── metrics.py   Performance, risk, distribution, and time-slice metrics
│   └── montecarlo.py Seeded Monte Carlo simulations
├── quality/
│   └── audit.py     Data quality audit (gaps, duplicates, DST, holidays, outliers)
└── cli.py           Command-line entry points (replay, backtest, audit)

MQL5/Indicators/NY_OR_Pullback_v1.mq5   MT5 indicator v1.0 (visualization only)
tests/                                    pytest suite
```

## Data flow

```text
M1 CSV (UTC timestamps)
   → loader (validate, sort, dedupe)
   → replay (time-ordered, completed-bar gate)
       → session (OR reconstruction per NY day)
       → bias (M15 EMA state)
       → signals (breakout/pullback/trigger state machine)
   → trade candidate records (entry/SL/TP, spread_at_signal)
   → backtest simulator (fills, costs, R, MAE/MFE)
   → metrics + equity curve + reports (results/)
```

## Timezone model

- Input data timestamps are **UTC** (documented assumption; loader
  rejects ambiguous input).
- `ny_time.py` converts UTC ↔ America/New_York using explicit US DST
  rules (2nd Sunday March 07:00 UTC → EDT; 1st Sunday November 06:00
  UTC → EST), implemented with `zoneinfo` and cross-checked against
  known transition instants in tests.
- Session windows (09:30 OR start, 09:45 trade start, 11:30 trade
  end) are defined in New York time and evaluated on per-bar NY time.

## No-look-ahead contract

Every function that produces a decision takes an explicit `index` (or
receives only bars with `time <= decision_time`). Tests in
`tests/test_no_lookahead.py` assert that truncating the dataset at any
point never changes decisions before that point (the "prefix
consistency" property).

## MQL5 indicator contract

The indicator mirrors `signals.py` exactly: same states, same reasons,
same thresholds (all exposed as inputs). It requests M1/M5/M15 data
explicitly, evaluates only completed bars, draws OR levels, breakout,
pullback zone, signal bar, entry/SL/TP, BUY/SELL arrows, and an
optional panel. It never calls `OrderSend`.
