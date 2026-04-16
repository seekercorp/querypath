"""Type casting utilities for query expressions."""

from datetime import datetime


SUPPORTED_TYPES = ("int", "float", "str", "bool", "date")


def cast_value(value, type_name: str):
    """Cast a value to the specified type name."""
    if value is None:
        return None
    t = type_name.strip().lower()
    if t == "int":
        return int(value)
    if t == "float":
        return float(value)
    if t == "str":
        return str(value)
    if t == "bool":
        if isinstance(value, str):
            return value.lower() not in ("false", "0", "", "no")
        return bool(value)
    if t == "date":
        if isinstance(value, datetime):
            return value.date()
        return datetime.fromisoformat(str(value)).date()
    raise ValueError(f"Unsupported cast type: {type_name!r}. Choose from {SUPPORTED_TYPES}")


def apply_cast(rows: list[dict], column: str, type_name: str) -> list[dict]:
    """Return rows with the given column cast to type_name."""
    out = []
    for row in rows:
        row = dict(row)
        if column in row:
            row[column] = cast_value(row[column], type_name)
        out.append(row)
    return out


def parse_cast_expression(expr: str):
    """Parse 'column::type' into (column, type). Returns None if not a cast expr."""
    if "::" not in expr:
        return None
    parts = expr.split("::", 1)
    return parts[0].strip(), parts[1].strip()
