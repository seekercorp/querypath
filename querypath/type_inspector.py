"""type_inspector.py – infer and report column types from a list of row dicts."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


_TYPE_PRIORITY = ["null", "bool", "int", "float", "str"]


def _infer_scalar(value: Any) -> str:
    """Return the type name for a single scalar value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    return "str"


def _merge_types(a: str, b: str) -> str:
    """Return the broader of two type names according to _TYPE_PRIORITY."""
    if a == b:
        return a
    ia = _TYPE_PRIORITY.index(a) if a in _TYPE_PRIORITY else len(_TYPE_PRIORITY)
    ib = _TYPE_PRIORITY.index(b) if b in _TYPE_PRIORITY else len(_TYPE_PRIORITY)
    return _TYPE_PRIORITY[max(ia, ib)]


def infer_column_types(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    """Return a mapping of column name -> inferred type across all rows.

    Rules:
    - A column that is always None is reported as "null".
    - Mixed int/float widens to "float".
    - Any non-numeric non-bool value widens to "str".
    """
    if not rows:
        return {}

    column_types: Dict[str, Optional[str]] = {}

    for row in rows:
        for key, value in row.items():
            vtype = _infer_scalar(value)
            if key not in column_types:
                column_types[key] = vtype
            else:
                column_types[key] = _merge_types(column_types[key], vtype)  # type: ignore[arg-type]

    return {k: (v or "null") for k, v in column_types.items()}


def summarise_columns(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return a list of summary dicts, one per column.

    Each dict contains: column, type, non_null_count, null_count, sample.
    """
    if not rows:
        return []

    types = infer_column_types(rows)
    columns = list(types.keys())
    summary = []

    for col in columns:
        values = [row.get(col) for row in rows]
        non_null = [v for v in values if v is not None]
        sample = non_null[0] if non_null else None
        summary.append(
            {
                "column": col,
                "type": types[col],
                "non_null_count": len(non_null),
                "null_count": len(values) - len(non_null),
                "sample": sample,
            }
        )

    return summary
