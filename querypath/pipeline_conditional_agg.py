"""Pipeline integration for conditional aggregation."""
from typing import Any, Dict, List

from querypath.conditional_agg import (
    apply_avg_if,
    apply_count_if,
    apply_sum_if,
    parse_conditional_agg_spec,
)

_DISPATCH = {
    "count_if": apply_count_if,
    "sum_if": apply_sum_if,
    "avg_if": apply_avg_if,
}


def run_pipeline_with_conditional_agg(
    rows: List[Dict[str, Any]],
    opts: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Apply zero or more conditional aggregation specs to *rows*.

    Each spec may contain:
      - func      : one of 'count_if', 'sum_if', 'avg_if'
      - condition : dict with keys field / op / value
      - field     : source field (required for sum_if / avg_if)
      - alias     : output column name (optional, defaults to func name)
    """
    if not opts:
        return rows

    specs = parse_conditional_agg_spec(opts)
    if not specs:
        return rows

    for spec in specs:
        func_name = spec.get("func", "")
        fn = _DISPATCH.get(func_name)
        if fn is None:
            continue

        condition = spec.get("condition", {})
        alias = spec.get("alias", func_name)

        if func_name == "count_if":
            rows = fn(rows, condition, alias=alias)
        else:
            field = spec.get("field", "")
            rows = fn(rows, field, condition, alias=alias)

    return rows
