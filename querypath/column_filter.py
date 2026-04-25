"""column_filter.py – include/exclude columns by name or pattern.

Supports:
  - include: list of column names to keep (in order)
  - exclude: list of column names to drop
  - include_pattern / exclude_pattern: glob-style wildcards (fnmatch)

All operations are non-mutating (new dicts are returned).
"""
from __future__ import annotations

import fnmatch
from typing import Any, Dict, List, Optional, Sequence

Row = Dict[str, Any]


def _matching_keys(keys: Sequence[str], pattern: str) -> List[str]:
    """Return keys that match a glob pattern."""
    return [k for k in keys if fnmatch.fnmatch(k, pattern)]


def apply_include(rows: List[Row], columns: List[str]) -> List[Row]:
    """Keep only the specified columns, preserving their order."""
    return [{col: row[col] for col in columns if col in row} for row in rows]


def apply_exclude(rows: List[Row], columns: List[str]) -> List[Row]:
    """Drop the specified columns from every row."""
    drop = set(columns)
    return [{k: v for k, v in row.items() if k not in drop} for row in rows]


def apply_include_pattern(rows: List[Row], pattern: str) -> List[Row]:
    """Keep only columns whose names match *pattern* (glob)."""
    if not rows:
        return rows
    keep = _matching_keys(list(rows[0].keys()), pattern)
    return apply_include(rows, keep)


def apply_exclude_pattern(rows: List[Row], pattern: str) -> List[Row]:
    """Drop columns whose names match *pattern* (glob)."""
    if not rows:
        return rows
    drop = _matching_keys(list(rows[0].keys()), pattern)
    return apply_exclude(rows, drop)


def parse_column_filter_spec(opts: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extract column-filter spec from pipeline options dict."""
    if not opts:
        return None
    spec: Dict[str, Any] = {}
    for key in ("include", "exclude", "include_pattern", "exclude_pattern"):
        if key in opts:
            spec[key] = opts[key]
    return spec or None


def run_column_filter(rows: List[Row], spec: Optional[Dict[str, Any]]) -> List[Row]:
    """Apply all column-filter directives in *spec* sequentially."""
    if not spec:
        return rows
    if "include" in spec:
        rows = apply_include(rows, spec["include"])
    if "exclude" in spec:
        rows = apply_exclude(rows, spec["exclude"])
    if "include_pattern" in spec:
        rows = apply_include_pattern(rows, spec["include_pattern"])
    if "exclude_pattern" in spec:
        rows = apply_exclude_pattern(rows, spec["exclude_pattern"])
    return rows
