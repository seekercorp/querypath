"""Deduplication support: DISTINCT and DISTINCT ON."""
from typing import List, Dict, Any, Optional


def _row_key(row: Dict[str, Any], columns: List[str]) -> tuple:
    return tuple(row.get(c) for c in columns)


def apply_distinct(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove fully duplicate rows (all fields equal)."""
    seen = set()
    result = []
    for row in rows:
        key = tuple(sorted(row.items()))
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def apply_distinct_on(
    rows: List[Dict[str, Any]],
    columns: List[str],
    keep: str = "first",
) -> List[Dict[str, Any]]:
    """Keep only the first (or last) row per unique combination of *columns*.

    Args:
        rows: input rows.
        columns: columns that define uniqueness.
        keep: ``'first'`` or ``'last'``.
    """
    if not columns:
        return rows

    if keep == "last":
        rows = list(reversed(rows))

    seen = set()
    result = []
    for row in rows:
        key = _row_key(row, columns)
        if key not in seen:
            seen.add(key)
            result.append(row)

    if keep == "last":
        result = list(reversed(result))

    return result


def parse_distinct_spec(spec: Optional[Any]) -> Optional[List[str]]:
    """Normalise a DISTINCT ON spec to a list of column names or None."""
    if spec is None:
        return None
    if isinstance(spec, str):
        return [c.strip() for c in spec.split(",") if c.strip()]
    if isinstance(spec, list):
        return [str(c) for c in spec]
    return None
