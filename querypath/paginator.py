"""Pagination support: LIMIT/OFFSET for query results."""

from typing import List, Dict, Any, Optional


def apply_offset(rows: List[Dict[str, Any]], offset: int) -> List[Dict[str, Any]]:
    """Skip the first `offset` rows."""
    if offset <= 0:
        return rows
    return rows[offset:]


def apply_limit(rows: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """Return at most `limit` rows."""
    if limit < 0:
        return rows
    return rows[:limit]


def apply_pagination(
    rows: List[Dict[str, Any]],
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Apply offset then limit to a list of rows."""
    if offset is not None:
        rows = apply_offset(rows, offset)
    if limit is not None:
        rows = apply_limit(rows, limit)
    return rows


def parse_pagination_spec(spec: Dict[str, Any]) -> Dict[str, Optional[int]]:
    """Extract limit and offset from a query spec dict.

    Expected keys: 'limit' and/or 'offset'.
    Returns a dict with 'limit' and 'offset' as ints or None.
    """
    limit = spec.get("limit")
    offset = spec.get("offset")

    if limit is not None:
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid limit value: {limit!r}")

    if offset is not None:
        try:
            offset = int(offset)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid offset value: {offset!r}")

    return {"limit": limit, "offset": offset}
