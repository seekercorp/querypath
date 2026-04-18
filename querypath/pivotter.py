"""Pivot and unpivot row transformations."""
from collections import defaultdict
from typing import Any


def apply_pivot(rows: list[dict], index: str, columns: str, values: str) -> list[dict]:
    """Pivot rows: group by index, spread unique column values as new columns."""
    if not rows:
        return []

    grouped: dict[Any, dict] = {}
    for row in rows:
        key = row.get(index)
        if key not in grouped:
            grouped[key] = {index: key}
        col_val = row.get(columns)
        val = row.get(values)
        if col_val is not None:
            grouped[key][str(col_val)] = val

    return list(grouped.values())


def apply_unpivot(
    rows: list[dict],
    id_columns: list[str],
    value_columns: list[str],
    var_name: str = "variable",
    val_name: str = "value",
) -> list[dict]:
    """Unpivot (melt) rows: turn value_columns into rows."""
    result = []
    for row in rows:
        base = {k: row[k] for k in id_columns if k in row}
        for col in value_columns:
            new_row = dict(base)
            new_row[var_name] = col
            new_row[val_name] = row.get(col)
            result.append(new_row)
    return result


def parse_pivot_spec(spec: dict) -> dict:
    """Validate and return pivot spec keys."""
    required = {"index", "columns", "values"}
    missing = required - spec.keys()
    if missing:
        raise ValueError(f"Pivot spec missing keys: {missing}")
    return spec
