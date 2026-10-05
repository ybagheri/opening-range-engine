"""Research machinery package (Phases 6/7/8/11).

All modules are methodology + machinery, validated on synthetic data.
No output of this package is market evidence until run on real data
(Phases 5+ stay BLOCKED). Every stochastic routine takes an explicit
seed; same inputs -> identical outputs.
"""

from .assessment import Verdict, assess
from .sensitivity import SensitivityCell, run_grid
from .splits import Split, make_splits, walk_forward_windows

__all__ = ["Verdict", "assess", "SensitivityCell", "run_grid", "Split",
           "make_splits", "walk_forward_windows"]
