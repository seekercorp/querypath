"""Core query engine for querypath."""
from typing import Any, Dict, List, Optional
from querypath.aggregator import apply_aggregation


class QueryEngine:
    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records

    def execute(
        self,
        select: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        agg_func: Optional[str] = None,
        agg_field: Optional[str] = None,
        group_by: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = list(self.records)

        if where:
            results = self._apply_where(results, where)

        if agg_func:
            return apply_aggregation(results, agg_func, agg_field, group_by)

        if select and select != ["*"]:
            results = [{col: row.get(col) for col in select} for row in results]

        if order_by:
            reverse = False
            field = order_by
            if order_by.upper().endswith(" DESC"):
                field = order_by[:-5].strip()
                reverse = True
            elif order_by.upper().endswith(" ASC"):
                field = order_by[:-4].strip()
            results = sorted(results, key=lambda r: (r.get(field) is None, r.get(field)), reverse=reverse)

        if limit is not None:
            results = results[:limit]

        return results

    def _apply_where(
        self, records: List[Dict[str, Any]], where: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        filtered = []
        for record in records:
            match = True
            for key, condition in where.items():
                value = record.get(key)
                if isinstance(condition, dict):
                    op = list(condition.keys())[0]
                    cond_val = condition[op]
                    if op == "gt" and not (value is not None and value > cond_val):
                        match = False
                    elif op == "lt" and not (value is not None and value < cond_val):
                        match = False
                    elif op == "gte" and not (value is not None and value >= cond_val):
                        match = False
                    elif op == "lte" and not (value is not None and value <= cond_val):
                        match = False
                    elif op == "ne" and not (value != cond_val):
                        match = False
                    elif op == "contains" and not (isinstance(value, str) and cond_val in value):
                        match = False
                else:
                    if value != condition:
                        match = False
            if match:
                filtered.append(record)
        return filtered
