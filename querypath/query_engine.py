"""Core query execution engine for querypath."""
from typing import Any, Dict, List, Optional
from querypath.joiner import apply_join


class QueryEngine:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def execute(
        self,
        select: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_dir: str = "asc",
        limit: Optional[int] = None,
        join_data: Optional[List[Dict[str, Any]]] = None,
        join_left_key: Optional[str] = None,
        join_right_key: Optional[str] = None,
        join_type: str = "inner",
        join_prefix: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        rows = list(self.data)

        if join_data is not None and join_left_key and join_right_key:
            rows = apply_join(
                rows,
                join_data,
                join_left_key,
                join_right_key,
                join_type=join_type,
                right_prefix=join_prefix,
            )

        if where:
            rows = self._apply_where(rows, where)

        if order_by:
            from querypath.sorter import apply_order_by
            rows = apply_order_by(rows, order_by, order_dir)

        if limit is not None:
            from querypath.sorter import apply_limit
            rows = apply_limit(rows, limit)

        if select:
            rows = self._apply_select(rows, select)

        return rows

    def _apply_where(
        self, rows: List[Dict[str, Any]], conditions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        result = []
        for row in rows:
            match = True
            for key, value in conditions.items():
                if isinstance(value, dict):
                    op = value.get("op", "eq")
                    val = value.get("value")
                    row_val = row.get(key)
                    if op == "eq" and row_val != val:
                        match = False
                    elif op == "ne" and row_val == val:
                        match = False
                    elif op == "gt" and not (row_val is not None and row_val > val):
                        match = False
                    elif op == "lt" and not (row_val is not None and row_val < val):
                        match = False
                    elif op == "gte" and not (row_val is not None and row_val >= val):
                        match = False
                    elif op == "lte" and not (row_val is not None and row_val <= val):
                        match = False
                    elif op == "contains" and (
                        row_val is None or str(val).lower() not in str(row_val).lower()
                    ):
                        match = False
                elif row.get(key) != value:
                    match = False
            if match:
                result.append(row)
        return result

    def _apply_select(
        self, rows: List[Dict[str, Any]], columns: List[str]
    ) -> List[Dict[str, Any]]:
        return [{col: row.get(col) for col in columns} for row in rows]
