"""Transaction-cost model (spec: costs stated in every report)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    """Costs applied to every simulated trade.

    - ``slippage_points``: extra adverse move on the entry fill, in
      symbol points (INITIAL; scenarios 0/1/2/5/10).
    - ``commission_per_trade``: flat commission per round trip, in price
      units of the symbol (INITIAL; must be stated in every report).
    - ``point``: SYMBOL_POINT of the configured symbol.
    - ``spread_at_signal`` is recorded on the signal (never a filter in
      v1.0); the fill model assumes the stop-order fills at the exact
      stop price plus slippage (assumption A15).
    """

    slippage_points: int = 0
    commission_per_trade: float = 0.0
    point: float = 1.0

    def entry_fill(self, stop_price: float, direction: str) -> float:
        slip = self.slippage_points * self.point
        if direction == "BULLISH":
            return stop_price + slip
        if direction == "BEARISH":
            return stop_price - slip
        raise ValueError(f"unknown direction: {direction!r}")

    def validate(self) -> "CostModel":
        if self.slippage_points < 0:
            raise ValueError("slippage_points must be >= 0")
        if self.commission_per_trade < 0:
            raise ValueError("commission_per_trade must be >= 0")
        if self.point <= 0:
            raise ValueError("point must be positive")
        return self
