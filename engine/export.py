"""Deterministic CSV export (byte-identical for identical inputs)."""

import csv

from .data.schema import SIGNAL_COLUMNS


def _fmt(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return repr(float(value))
    return str(value)


def export_signals(signals, path: str) -> str:
    """Write signal records to CSV. Returns the path."""
    rows = sorted(signals, key=lambda s: (s.signal_time_utc, s.direction))
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(list(SIGNAL_COLUMNS))
        for sig in rows:
            writer.writerow([_fmt(v) for v in sig.to_row()])
    return path


def export_day_reports(reports, path: str) -> str:
    """Write per-day outcomes (one row per NY day)."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["date", "state", "reason", "n_signals"])
        for rep in sorted(reports, key=lambda r: str(r.ny_day)):
            writer.writerow([str(rep.ny_day), rep.state,
                             rep.reason or "", len(rep.signals)])
    return path
