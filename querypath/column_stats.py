"""column_stats.py – per-column descriptive statistics for numeric and string fields."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


def _numeric_values(rows: List[Dict], field: str) -> List[float]:
    out = []
    for row in rows:
        v = row.get(field)
        if v is None:
            continue
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            pass
    return out


def stat_min(values: List[float]) -> Optional[float]:
    return min(values) if values else None


def stat_max(values: List[float]) -> Optional[float]:
    return max(values) if values else None


def stat_mean(values: List[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def stat_median(values: List[float]) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def stat_stddev(values: List[float]) -> Optional[float]:
    if len(values) < 2:
        return None
    mean = stat_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def stat_count_non_null(rows: List[Dict], field: str) -> int:
    return sum(1 for row in rows if row.get(field) is not None)


def compute_column_stats(rows: List[Dict], field: str) -> Dict[str, Any]:
    """Return a dict of descriptive stats for *field* across *rows*."""
    values = _numeric_values(rows, field)
    return {
        "field": field,
        "count": stat_count_non_null(rows, field),
        "numeric_count": len(values),
        "min": stat_min(values),
        "max": stat_max(values),
        "mean": stat_mean(values),
        "median": stat_median(values),
        "stddev": stat_stddev(values),
    }


def apply_column_stats(rows: List[Dict], fields: List[str]) -> List[Dict[str, Any]]:
    """Return one stats-row per requested field."""
    return [compute_column_stats(rows, f) for f in fields]
