"""Freshness helpers for v4 stale-node detection."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def is_file_stale(filepath: str | Path, stale_after_days: int = 30) -> bool:
    """Return True when file mtime is older than the configured stale threshold."""
    if stale_after_days <= 0:
        return False

    path = Path(filepath)
    if not path.exists():
        return False

    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_days = (datetime.now(timezone.utc) - mtime).total_seconds() / 86400.0
    return age_days >= float(stale_after_days)


def stale_label(name: str, stale: bool) -> str:
    """Prefix stale entities with a marker used in v4 output assertions."""
    if not stale:
        return name
    return name if name.startswith("[STALE] ") else f"[STALE] {name}"
