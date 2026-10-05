"""Strategy configuration — the typed mirror of docs/PARAMETER_REGISTRY.md.

Every parameter carries its registry classification. No parameter may be
silently changed: INITIAL values are the v1.0 baseline (control
experiment) and may only change through a documented experiment.
"""

from dataclasses import dataclass
from enum import Enum


class TPMode(Enum):
    """Take-profit mode. Values are the R multiple of RiskDistance."""

    R1 = 1.0
    R1_25 = 1.25
    R1_5 = 1.5
    R1_75 = 1.75
    R2 = 2.0

    @classmethod
    def from_string(cls, name: str) -> "TPMode":
        key = name.strip().upper().replace("-", "_").replace(".", "_")
        aliases = {"R1_5": "R1_5", "R15": "R1_5",
                   "R1_25": "R1_25", "R125": "R1_25",
                   "R1_75": "R1_75", "R175": "R1_75"}
        if key in aliases:
            return cls[aliases[key]]
        if key in cls.__members__:
            return cls[key]
        raise ValueError(f"unknown TP mode: {name!r}")


class Bias(Enum):
    """M15 directional bias."""

    NEUTRAL = "NEUTRAL"
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


class SignalState(Enum):
    """Explicit strategy states (spec section 13)."""

    WAITING = "WAITING"
    BULLISH_BIAS = "BULLISH_BIAS"
    BEARISH_BIAS = "BEARISH_BIAS"
    OR_FORMING = "OR_FORMING"
    OR_VALID = "OR_VALID"
    BREAKOUT_DETECTED = "BREAKOUT_DETECTED"
    WAITING_PULLBACK = "WAITING_PULLBACK"
    PULLBACK_CONFIRMED = "PULLBACK_CONFIRMED"
    SIGNAL_CONFIRMED = "SIGNAL_CONFIRMED"
    TRADE_ACTIVE = "TRADE_ACTIVE"
    SETUP_INVALIDATED = "SETUP_INVALIDATED"
    NO_TRADE = "NO_TRADE"


@dataclass(frozen=True)
class StrategyConfig:
    """All v1.0 parameters. Immutable once created; validate() enforces
    sanity ranges so a bad input fails loudly instead of silently.
    """

    # Market / symbol (never hardcoded; point size is an explicit input)
    symbol: str = "US30"
    point: float = 1.0          # SYMBOL_POINT for the configured symbol
    digits: int = 2             # SYMBOL_DIGITS for the configured symbol

    # Timeframe architecture (FIXED)
    context_timeframe_minutes: int = 15   # M15
    setup_timeframe_minutes: int = 5      # M5
    entry_timeframe_minutes: int = 1      # M1

    # Session (INITIAL)
    opening_range_minutes: int = 15
    or_start_ny: str = "09:30"     # America/New_York
    trade_start_ny: str = "09:45"  # America/New_York
    trade_end_ny: str = "11:30"    # America/New_York

    # Indicators (INITIAL)
    ema_fast: int = 20
    ema_slow: int = 50
    atr_period: int = 14

    # Filters (INITIAL)
    min_or_atr: float = 0.25
    max_or_atr: float = 1.00
    max_breakout_extension_atr: float = 0.50
    pullback_lower_atr: float = 0.25
    pullback_upper_atr: float = 0.10
    min_stop_atr: float = 0.10
    max_stop_atr: float = 1.00

    # Risk / limits (INITIAL)
    max_trades_per_day: int = 2
    risk_percent: float = 0.50     # research risk per trade, % of equity
    daily_loss_limit_r: float = 2.0  # simulated daily loss control (-2R)
    tp_mode: TPMode = TPMode.R1_5

    # Costs (INITIAL; stated in every report)
    slippage_points: int = 0
    commission_per_lot: float = 0.0

    # Buffers (FIXED)
    entry_buffer_points: int = 1
    stop_buffer_points: int = 1

    # Determinism
    seed: int = 42

    def validate(self) -> "StrategyConfig":
        """Raise ValueError on any invalid configuration."""
        if not self.symbol:
            raise ValueError("symbol must not be empty")
        if self.point <= 0:
            raise ValueError("point must be positive")
        if self.digits < 0:
            raise ValueError("digits must be >= 0")
        for name, value in (
            ("context_timeframe_minutes", self.context_timeframe_minutes),
            ("setup_timeframe_minutes", self.setup_timeframe_minutes),
            ("entry_timeframe_minutes", self.entry_timeframe_minutes),
        ):
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.opening_range_minutes <= 0:
            raise ValueError("opening_range_minutes must be positive")
        if self.ema_fast <= 0 or self.ema_slow <= 0:
            raise ValueError("EMA periods must be positive")
        if self.ema_fast >= self.ema_slow:
            raise ValueError("ema_fast must be < ema_slow")
        if self.atr_period <= 0:
            raise ValueError("atr_period must be positive")
        for name, value in (
            ("min_or_atr", self.min_or_atr),
            ("max_or_atr", self.max_or_atr),
            ("max_breakout_extension_atr", self.max_breakout_extension_atr),
            ("pullback_lower_atr", self.pullback_lower_atr),
            ("pullback_upper_atr", self.pullback_upper_atr),
            ("min_stop_atr", self.min_stop_atr),
            ("max_stop_atr", self.max_stop_atr),
        ):
            if value < 0:
                raise ValueError(f"{name} must be >= 0")
        if self.min_or_atr >= self.max_or_atr:
            raise ValueError("min_or_atr must be < max_or_atr")
        if self.min_stop_atr >= self.max_stop_atr:
            raise ValueError("min_stop_atr must be < max_stop_atr")
        if self.max_trades_per_day < 1:
            raise ValueError("max_trades_per_day must be >= 1")
        if not (0 < self.risk_percent <= 100):
            raise ValueError("risk_percent must be in (0, 100]")
        if self.daily_loss_limit_r <= 0:
            raise ValueError("daily_loss_limit_r must be positive")
        if self.slippage_points < 0:
            raise ValueError("slippage_points must be >= 0")
        if self.commission_per_lot < 0:
            raise ValueError("commission_per_lot must be >= 0")
        if self.entry_buffer_points < 0 or self.stop_buffer_points < 0:
            raise ValueError("entry/stop buffers must be >= 0")
        return self

    @property
    def tp_multiplier(self) -> float:
        return self.tp_mode.value
