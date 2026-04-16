"""Flatten nested JSON structures into dotted-key rows."""
from typing import Any, Dict, List


def _flatten(obj: Any, prefix: str = "", sep: str = ".") -> Dict[str, Any]:
    """Recursively flatten a nested dict into a single-level dict."""
    items: Dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}{sep}{k}" if prefix else k
            items.update(_flatten(v, new_key, sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{prefix}{sep}{i}" if prefix else str(i)
            items.update(_flatten(v, new_key, sep))
    else:
        items[prefix] = obj
    return items


def expand_rows(rows: List[Dict[str, Any]], sep: str = ".") -> List[Dict[str, Any]]:
    """Flatten each row in a list of records."""
    return [_flatten(row, sep=sep) for row in rows]


def expand_column(rows: List[Dict[str, Any]], column: str, sep: str = ".") -> List[Dict[str, Any]]:
    """Expand only a specific nested column within each row, merging results."""
    result = []
    for row in rows:
        flat = dict(row)
        value = flat.pop(column, None)
        if isinstance(value, dict):
            nested = _flatten(value, prefix=column, sep=sep)
            flat.update(nested)
        else:
            flat[column] = value
        result.append(flat)
    return result
