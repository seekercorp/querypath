from collections import defaultdict
from typing import Any


def apply_group_by(rows: list[dict], group_by: list[str]) -> dict[tuple, list[dict]]:
    """Group rows by the specified columns, returning a dict keyed by group tuple."""
    if not group_by:
        return {(): rows}

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        key = tuple(row.get(col) for col in group_by)
        groups[key].append(row)
    return dict(groups)


def apply_having(groups: dict[tuple, list[dict]], having: dict | None) -> dict[tuple, list[dict]]:
    """Filter groups using a HAVING clause (same structure as WHERE)."""
    if not having:
        return groups

    field = having.get("field")
    op = having.get("op", "=")
    value = having.get("value")

    from querypath.aggregator import _compute

    filtered = {}
    for key, group_rows in groups.items():
        agg_value = _compute(group_rows, field)
        if _match(agg_value, op, value):
            filtered[key] = group_rows
    return filtered


def _match(actual: Any, op: str, expected: Any) -> bool:
    try:
        if op in ("=", "=="):
            return actual == expected
        elif op == "!=":
            return actual != expected
        elif op == ">":
            return actual > expected
        elif op == ">=":
            return actual >= expected
        elif op == "<":
            return actual < expected
        elif op == "<=":
            return actual <= expected
    except TypeError:
        return False
    return False


def flatten_groups(groups: dict[tuple, list[dict]], group_by: list[str]) -> list[dict]:
    """Flatten grouped rows back into a list, injecting group keys as fields."""
    result = []
    for key, group_rows in groups.items():
        for row in group_rows:
            merged = dict(zip(group_by, key))
            merged.update(row)
            result.append(merged)
    return result
