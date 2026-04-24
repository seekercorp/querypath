"""CASE expression support for querypath.

Supports CASE WHEN ... THEN ... [ELSE ...] END style conditional expressions
that can be applied as computed columns.
"""
from typing import Any, Dict, List, Optional, Tuple


def _resolve_field(row: Dict[str, Any], value: Any) -> Any:
    """If value is a string matching a row key, return that field; else literal."""
    if isinstance(value, str) and value in row:
        return row[value]
    return value


def evaluate_case(
    row: Dict[str, Any],
    when_thens: List[Tuple[Tuple[str, str, Any], Any]],
    else_value: Any = None,
) -> Any:
    """Evaluate a CASE expression against a single row.

    Args:
        row: A data row dict.
        when_thens: List of ((field, op, compare_value), result_value) tuples.
        else_value: Value to return if no WHEN clause matches.

    Returns:
        The matched THEN value, or else_value.
    """
    for (field, op, compare_val), result in when_thens:
        actual = row.get(field)
        compare = _resolve_field(row, compare_val)
        matched = False
        if op == "==":
            matched = actual == compare
        elif op == "!=":
            matched = actual != compare
        elif op == ">":
            try:
                matched = actual > compare
            except TypeError:
                matched = False
        elif op == ">=":
            try:
                matched = actual >= compare
            except TypeError:
                matched = False
        elif op == "<":
            try:
                matched = actual < compare
            except TypeError:
                matched = False
        elif op == "<=":
            try:
                matched = actual <= compare
            except TypeError:
                matched = False
        if matched:
            return _resolve_field(row, result)
    return _resolve_field(row, else_value)


def apply_case_column(
    rows: List[Dict[str, Any]],
    alias: str,
    when_thens: List[Tuple[Tuple[str, str, Any], Any]],
    else_value: Any = None,
) -> List[Dict[str, Any]]:
    """Add a computed column to each row using a CASE expression."""
    result = []
    for row in rows:
        new_row = dict(row)
        new_row[alias] = evaluate_case(row, when_thens, else_value)
        result.append(new_row)
    return result


def parse_case_spec(spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract a case spec from a pipeline options dict.

    Expected shape:
        {"case": {"alias": str, "when_thens": [...], "else": any}}
    """
    if "case" not in spec:
        return None
    return spec["case"]
