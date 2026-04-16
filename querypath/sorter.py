"""Sorting and limiting results for querypath."""

from typing import List, Dict, Any, Optional


def apply_order_by(
    records: List[Dict[str, Any]],
    order_by: Optional[str] = None,
    ascending: bool = True,
) -> List[Dict[str, Any]]:
    """Sort records by a given column.

    Args:
        records: List of row dicts.
        order_by: Column name to sort by, or None to skip.
        ascending: Sort direction; True = ASC, False = DESC.

    Returns:
        Sorted list of records.
    """
    if not order_by or not records:
        return records

    if order_by not in records[0]:
        raise ValueError(f"ORDER BY column '{order_by}' not found in results.")

    def sort_key(row: Dict[str, Any]):
        val = row.get(order_by)
        # Push None values to the end regardless of direction
        if val is None:
            return (1, None)
        return (0, val)

    return sorted(records, key=sort_key, reverse=not ascending)


def apply_limit(
    records: List[Dict[str, Any]],
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """Apply LIMIT and OFFSET to records.

    Args:
        records: List of row dicts.
        limit: Maximum number of rows to return, or None for all.
        offset: Number of rows to skip from the start.

    Returns:
        Sliced list of records.
    """
    if offset:
        records = records[offset:]
    if limit is not None:
        records = records[:limit]
    return records
