"""Final outcome classification (spec section 20).

PROMISING / INCONCLUSIVE / WEAK / FAILED / OVERFIT / ROBUST — from
quantitative evidence, never net profit alone. Thresholds below are
INITIAL and documented; they gate the *label*, never the parameters.
"""

from dataclasses import dataclass

VERDICTS: tuple = ("PROMISING", "INCONCLUSIVE", "WEAK", "FAILED",
                   "OVERFIT", "ROBUST")


@dataclass(frozen=True)
class Verdict:
    label: str
    reasons: tuple


def assess(n_trades: int, expectancy_r: float, profit_factor: float,
           max_drawdown_r: float, sensitivity_verdict: str,
           mc_prob_profit: float | None = None) -> Verdict:
    """Classify the strategy state from evidence.

    Rules (all must hold for the stronger labels):
    - ROBUST: sensitivity ROBUST REGION + expectancy > 0 + PF > 1.2
      + MC P(profit) > 0.8 (when MC available).
    - OVERFIT: sensitivity POSSIBLE OVERFITTING (regardless of profit).
    - FAILED: expectancy <= -0.2 or PF < 0.8 with n >= 30.
    - WEAK: |expectancy| small or PF near 1 with n >= 30.
    - PROMISING: expectancy > 0.1 and PF > 1.1 with n >= 30 but MC
      missing or weak.
    - INCONCLUSIVE: anything with n < 30 (never judge on tiny samples).
    """
    reasons: list = []
    if n_trades < 30:
        reasons.append(f"n={n_trades} < 30: sample too small to judge")
        return Verdict("INCONCLUSIVE", tuple(reasons))
    if sensitivity_verdict == "POSSIBLE OVERFITTING":
        reasons.append("nearby parameters unstable")
        return Verdict("OVERFIT", tuple(reasons))
    if expectancy_r <= -0.2 or profit_factor < 0.8:
        reasons.append(f"expectancy={expectancy_r:.3f}R "
                       f"PF={profit_factor:.3f}")
        return Verdict("FAILED", tuple(reasons))
    if abs(expectancy_r) < 0.1 or abs(profit_factor - 1.0) < 0.1:
        reasons.append(f"expectancy={expectancy_r:.3f}R "
                       f"PF={profit_factor:.3f}: no detectable edge")
        return Verdict("WEAK", tuple(reasons))
    if (sensitivity_verdict == "ROBUST REGION" and expectancy_r > 0
            and profit_factor > 1.2 and mc_prob_profit is not None
            and mc_prob_profit > 0.8):
        reasons.append(
            f"expectancy={expectancy_r:.3f}R PF={profit_factor:.3f} "
            f"MC P(profit)={mc_prob_profit:.2f} "
            f"maxDD={max_drawdown_r:.2f}R")
        return Verdict("ROBUST", tuple(reasons))
    reasons.append(f"expectancy={expectancy_r:.3f}R "
                   f"PF={profit_factor:.3f}: needs OOS/WF/MC confirmation")
    return Verdict("PROMISING", tuple(reasons))
