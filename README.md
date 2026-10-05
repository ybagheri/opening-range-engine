# Persian documentation: [README_FA.md](README_FA.md)

# Opening Range Engine — NY Opening Range Pullback Strategy (US30)

**A reproducible research system for MetaTrader 5. This is a research project,
not a trading recommendation. No profitability is claimed or implied.**

## What this is

This repository implements, tests, and validates the **NY Opening Range
Breakout + Pullback + Price Action Trigger** strategy (Strategy Specification
v1.0) for the New York cash-session open on US30 (Dow Jones CFD), with an
architecture designed to later support NAS100, XAUUSD, GER40, EURUSD, and
other MT5 symbols.

The pipeline is strictly sequential and no stage may be skipped because an
earlier result looks profitable:

```text
Strategy Hypothesis → Formal Specification → MT5 Indicator → Historical Signal
Detection → Trade Dataset → Backtesting → Statistical Analysis → Parameter
Research → Out-of-Sample Testing → Walk-Forward Validation → Monte Carlo
Analysis → Forward Demo Testing → Robustness Assessment → Optional EA
```

## Repository layout

| Path | Purpose |
| --- | --- |
| `MQL5/Indicators/NY_OR_Pullback_v1.mq5` | MT5 indicator v1.0 (chart visualization, real-time state machine, no execution) |
| `engine/` | Python research engine: NY timezone, session, bias, signals, backtester, metrics, data quality |
| `tests/` | Unit, integration, determinism, DST, boundary, missing-data, and no-look-ahead tests |
| `docs/` | Strategy specification, parameter registry, architecture |
| `data/` | Input bar data (CSV) — not committed |
| `results/` | Generated reports, CSVs, equity curves — not committed |
| `HANDOFF.md` | **Authoritative continuation point** — read this first |

## Quick start (research engine)

```bash
python3 -m pip install -r requirements.txt   # no third-party deps required today
python3 -m pytest tests/ -q                   # full test suite
python3 -m engine.cli replay --help           # historical signal replay
python3 -m engine.cli backtest --help         # R-based backtest
```

## Documentation map

- [`docs/STRATEGY_SPEC.md`](docs/STRATEGY_SPEC.md) — formal Strategy Specification v1.0
- [`docs/PARAMETER_REGISTRY.md`](docs/PARAMETER_REGISTRY.md) — every parameter, its value, and its classification (FIXED / INITIAL / OPTIMIZABLE / DERIVED)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system architecture and data flow
- [`ROADMAP.md`](ROADMAP.md) — phased plan and completion status
- [`CHANGELOG.md`](CHANGELOG.md) — every meaningful change
- [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md) — every experiment and its conclusion
- [`DECISION_LOG.md`](DECISION_LOG.md) — architectural and research decisions
- [`ASSUMPTIONS.md`](ASSUMPTIONS.md) — explicit assumptions
- [`HANDOFF.md`](HANDOFF.md) — current state, blockers, next task

## Risk warning

Historical backtest results are never guaranteed future performance. Do not
risk real capital until out-of-sample testing, walk-forward validation, Monte
Carlo analysis, transaction-cost sensitivity, and forward demo testing have all
been completed. This project may conclude that the strategy has no edge; that
is a valid and successful research outcome.

## License

See `LICENSE`.
