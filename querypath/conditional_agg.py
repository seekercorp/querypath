"""Conditional aggregation: COUNT IF, SUM IF, AVG IF, etc."""
from typing import Any, Dict, List, Optional


def _eval_condition(row: Dict[str, Any], condition: Dict[str, Any]) -> bool:
    """Evaluate a simple condition dict against a row."""
    field = condition.get("field")
    op = condition.get("op", "eq")
    value = condition.get("value")
    row_val = row.get(field)

    if op in ("eq", "="):
        return row_val == value
    if op in ("neq", "!="):
        return row_val != value
    if op in ("gt", ">"):
        return row_val is not None and row_val > value
    if op in ("gte", ">="):
        return row_val is not None and row_val >= value
    if op in ("lt", "<"):
        return row_val is not None and row_val < value
    if op in ("lte", "<="):
        return row_val is not None and row_val <= value
    if op == "is_null":
        return row_val is None
    if op == "is_not_null":
        return row_val is not None
    return False


def apply_count_if(
    rows: List[Dict[str, Any]],
    condition: Dict[str, Any],
    alias: str = "count_if",
) -> List[Dict[str, Any]]:
    """Add a column with the count of rows matching condition up to each row."""
    total = sum(1 for r in rows if _eval_condition(r, condition))
    return [{**row, alias: total} for row in rows]


def apply_sum_if(
    rows: List[Dict[str, Any]],
    field: str,
    condition: Dict[str, Any],
    alias: str = "sum_if",
) -> List[Dict[str, Any]]:
    """Add a column with the conditional sum."""
    total = sum(
        (r.get(field) or 0)
        for r in rows
        if _eval_condition(r, condition) and isinstance(r.get(field), (int, float))
    )
    return [{**row, alias: total} for row in rows]


def apply_avg_if(
    rows: List[Dict[str, Any]],
    field: str,
    condition: Dict[str, Any],
    alias: str = "avg_if",
) -> List[Dict[str, Any]]:
    """Add a column with the conditional average."""
    values = [
        r.get(field)
        for r in rows
        if _eval_condition(r, condition) and isinstance(r.get(field), (int, float))
    ]
    avg: Optional[float] = sum(values) / len(values) if values else None
    return [{**row, alias: avg} for row in rows]


def parse_conditional_agg_spec(opts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract list of conditional aggregation specs from pipeline options."""
    raw = opts.get("conditional_agg")
    if not raw:
        return []
    if isinstance(raw, dict):
        return [raw]
    return list(raw)
