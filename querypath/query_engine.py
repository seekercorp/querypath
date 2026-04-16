"""Core query engine for querypath — handles SELECT, WHERE, ORDER BY, LIMIT."""

from typing import Any, Dict, List, Optional
from querypath.sorter import apply_order_by, apply_limit


class QueryEngine:
    """Executes SQL-like queries against a list of record dicts."""

    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records

    def execute(
        self,
        select: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        ascending: bool = True,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Run a query against the loaded records.

        Args:
            select: Columns to include; None or ['*'] means all columns.
            where: Equality filters as {column: value}.
            order_by: Column name to sort by.
            ascending: Sort direction.
            limit: Max rows to return.
            offset: Rows to skip.

        Returns:
            Filtered, sorted, and sliced list of record dicts.
        """
        results = list(self.records)

        # WHERE
        if where:
            results = self._apply_where(results, where)

        # ORDER BY
        results = apply_order_by(results, order_by, ascending=ascending)

        # LIMIT / OFFSET
        results = apply_limit(results, limit=limit, offset=offset)

        # SELECT
        if select and select != ["*"]:
            results = self._apply_select(results, select)

        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_where(
        self,
        records: List[Dict[str, Any]],
        conditions: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Filter records by equality conditions."""
        filtered = []
        for row in records:
            if all(row.get(col) == val for col, val in conditions.items()):
                filtered.append(row)
        return filtered

    def _apply_select(
        self,
        records: List[Dict[str, Any]],
        columns: List[str],
    ) -> List[Dict[str, Any]]:
        """Project only the requested columns."""
        return [{col: row.get(col) for col in columns} for row in records]
