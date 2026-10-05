"""Structural checks for the MQL5 indicator (cannot compile MQL5 on Linux)."""

import re
from pathlib import Path

MQ5 = Path(__file__).resolve().parent.parent / "MQL5" / "Indicators" / "NY_OR_Pullback_v1.mq5"

REASONS = [
    "Neutral M15 bias", "Opening Range too large", "Opening Range too small",
    "Opening Range incomplete (missing bars)",
    "Breakout occurred after trading window",
    "Breakout extension too large", "Pullback invalidated",
    "Stop distance too large", "Stop distance too small",
    "Daily trade limit reached", "Signal not confirmed before window close",
    "Same-direction setup already active", "Daily loss limit reached",
    "Insufficient data",
]

STATES = ["WAITING", "BULLISH_BIAS", "BEARISH_BIAS", "OR_FORMING", "OR_VALID",
          "BREAKOUT_DETECTED", "WAITING_PULLBACK", "PULLBACK_CONFIRMED",
          "SIGNAL_CONFIRMED", "TRADE_ACTIVE", "SETUP_INVALIDATED", "NO_TRADE"]


def src():
    return MQ5.read_text(encoding="utf-8", errors="replace")


def test_indicator_file_exists():
    assert MQ5.exists(), "MQL5 indicator missing"


def test_all_no_trade_reasons_present():
    text = src()
    for reason in REASONS:
        assert reason in text, f"reason missing: {reason}"


def test_all_states_present():
    text = src()
    for state in STATES:
        assert state in text, f"state missing: {state}"


def test_all_registry_inputs_present():
    text = src()
    for name in ["InpOpeningRangeMinutes", "InpEMAFast", "InpEMASlow",
                 "InpATRPeriod", "InpMinOR_ATR", "InpMaxOR_ATR",
                 "InpMaxBreakoutExt_ATR", "InpPullbackLower_ATR",
                 "InpPullbackUpper_ATR", "InpMinStop_ATR", "InpMaxStop_ATR",
                 "InpTradeStartNY", "InpTradeEndNY", "InpMaxTradesPerDay",
                 "InpTP_R"]:
        assert name in text, f"input missing: {name}"


def test_no_ordersend():
    assert "OrderSend" not in src(), "indicator must never trade"


def test_dst_rules_present():
    text = src()
    assert "SecondSundayMarch" in text and "FirstSundayNovember" in text
    assert "07:00" in text and "06:00" in text


def test_completed_bars_only():
    text = src()
    assert "prev_calculated" in text
