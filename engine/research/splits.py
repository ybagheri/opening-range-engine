"""Dataset splits + walk-forward windows (spec section 20).

- ``make_splits``: chronological 60/20/20 train/validation/OOS split of
  an ordered day/trade list. OOS is never touched during research.
- ``walk_forward_windows``: rolling windows over an ordered day list;
  each window is (train_days, test_days) with the test block strictly
  after the train block (no overlap, no look-ahead).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Split:
    train: tuple
    validation: tuple
    oos: tuple


def make_splits(items: list,
                train_frac: float = 0.60,
                validation_frac: float = 0.20) -> Split:
    """Chronological split preserving order (no shuffling, ever)."""
    n = len(items)
    if n < 3:
        raise ValueError("need at least 3 items to split 60/20/20")
    n_train = int(n * train_frac)
    n_val = int(n * validation_frac)
    if n_train < 1 or n_val < 1 or n - n_train - n_val < 1:
        raise ValueError(f"cannot split {n} items 60/20/20")
    return Split(train=tuple(items[:n_train]),
                 validation=tuple(items[n_train:n_train + n_val]),
                 oos=tuple(items[n_train + n_val:]))


def walk_forward_windows(days: list, train_size: int,
                         test_size: int, step: int = 1):
    """Yield (train_days, test_days) rolling windows, chronological.

    Window k: train = days[k:k+train_size], test = days[k+train_size:
    k+train_size+test_size]. Test strictly follows train.
    """
    if train_size < 1 or test_size < 1 or step < 1:
        raise ValueError("train/test/step sizes must be >= 1")
    k = 0
    while k + train_size + test_size <= len(days):
        yield (list(days[k:k + train_size]),
               list(days[k + train_size:k + train_size + test_size]))
        k += step
