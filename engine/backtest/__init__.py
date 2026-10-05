"""R-based backtesting engine (Phase 3)."""

from .costs import CostModel
from .metrics import Metrics, compute_metrics
from .records import TRADE_COLUMNS, TradeRecord, trade_from_signal_and_result
from .report import export_equity, export_summary, export_trades
from .simulator import TradeResult, simulate_all, simulate_signal

__all__ = [
    "CostModel", "Metrics", "compute_metrics",
    "TRADE_COLUMNS", "TradeRecord", "trade_from_signal_and_result",
    "export_equity", "export_summary", "export_trades",
    "TradeResult", "simulate_all", "simulate_signal",
]

