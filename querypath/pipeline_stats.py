"""pipeline_stats.py – integrate column-stats computation into the query pipeline."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from querypath.column_stats import apply_column_stats


def extract_stats_spec(opts: Optional[Dict[str, Any]]) -> Optional[List[str]]:
    """Return a list of field names from opts['stats'], or None if absent.

    Accepts either a list of field names or a comma-separated string.
    """
    if not opts:
        return None
    raw = opts.get("stats")
    if raw is None:
        return None
    if isinstance(raw, list):
        return [str(f).strip() for f in raw if str(f).strip()]
    if isinstance(raw, str):
        return [f.strip() for f in raw.split(",") if f.strip()]
    return None


def run_pipeline_with_stats(
    rows: List[Dict[str, Any]],
    opts: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """If a stats spec is present, replace *rows* with per-field stat rows.

    Otherwise return *rows* unchanged.
    """
    fields = extract_stats_spec(opts)
    if not fields:
        return rows
    return apply_column_stats(rows, fields)
