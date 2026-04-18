"""Null handling utilities: COALESCE, NULLIF, IS NULL / IS NOT NULL filters."""
from typing import Any, List, Dict, Optional


def coalesce(*values: Any) -> Any:
    """Return the first non-None value, or None if all are None."""
    for v in values:
        if v is not None:
            return v
    return None


def nullif(value: Any, null_value: Any) -> Optional[Any]:
    """Return None if value == null_value, else return value."""
    return None if value == null_value else value


def apply_coalesce(rows: List[Dict], field: str, fallbacks: List[str], dest: str) -> List[Dict]:
    """Add dest column = first non-None among field + fallbacks for each row."""
    result = []
    for row in rows:
        candidates = [row.get(f) for f in [field] + fallbacks]
        new_row = dict(row)
        new_row[dest] = coalesce(*candidates)
        result.append(new_row)
    return result


def apply_nullif(rows: List[Dict], field: str, null_value: Any, dest: str) -> List[Dict]:
    """Add dest column = nullif(row[field], null_value) for each row."""
    result = []
    for row in rows:
        new_row = dict(row)
        new_row[dest] = nullif(row.get(field), null_value)
        result.append(new_row)
    return result


def filter_is_null(rows: List[Dict], field: str) -> List[Dict]:
    """Keep rows where field is None or missing."""
    return [r for r in rows if r.get(field) is None]


def filter_is_not_null(rows: List[Dict], field: str) -> List[Dict]:
    """Keep rows where field is not None."""
    return [r for r in rows if r.get(field) is not None]


def parse_null_spec(options: Dict) -> Optional[Dict]:
    """Extract null-handling spec from pipeline options."""
    if "coalesce" in options:
        return {"op": "coalesce", **options["coalesce"]}
    if "nullif" in options:
        return {"op": "nullif", **options["nullif"]}
    if "is_null" in options:
        return {"op": "is_null", "field": options["is_null"]}
    if "is_not_null" in options:
        return {"op": "is_not_null", "field": options["is_not_null"]}
    return None


def apply_null_spec(rows: List[Dict], spec: Dict) -> List[Dict]:
    op = spec["op"]
    if op == "coalesce":
        return apply_coalesce(rows, spec["field"], spec.get("fallbacks", []), spec.get("dest", spec["field"]))
    if op == "nullif":
        return apply_nullif(rows, spec["field"], spec.get("null_value"), spec.get("dest", spec["field"]))
    if op == "is_null":
        return filter_is_null(rows, spec["field"])
    if op == "is_not_null":
        return filter_is_not_null(rows, spec["field"])
    return rows
