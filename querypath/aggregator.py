"""Aggregation functions for querypath query results."""
from typing import Any, Dict, List, Optional


SUPPORTED_FUNCS = ("COUNT", "SUM", "AVG", "MIN", "MAX")


def apply_aggregation(
    records: List[Dict[str, Any]],
    agg_func: str,
    agg_field: Optional[str],
    group_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Apply an aggregation function to records, optionally grouped."""
    func = agg_func.upper()
    if func not in SUPPORTED_FUNCS:
        raise ValueError(f"Unsupported aggregation function: {agg_func}")

    if group_by:
        groups: Dict[Any, List[Dict]] = {}
        for rec in records:
            key = rec.get(group_by)
            groups.setdefault(key, []).append(rec)
        return [
            {group_by: key, f"{func}({agg_field})": _compute(func, agg_field, rows)}
            for key, rows in groups.items()
        ]

    result = _compute(func, agg_field, records)
    label = f"{func}({agg_field})" if agg_field else f"{func}(*)"
    return [{label: result}]


def _compute(func: str, field: Optional[str], records: List[Dict[str, Any]]) -> Any:
    if func == "COUNT":
        return len(records)

    values = []
    for rec in records:
        val = rec.get(field)
        if val is not None:
            try:
                values.append(float(val))
            except (TypeError, ValueError):
                pass

    if not values:
        return None

    if func == "SUM":
        return sum(values)
    if func == "AVG":
        return sum(values) / len(values)
    if func == "MIN":
        return min(values)
    if func == "MAX":
        return max(values)
