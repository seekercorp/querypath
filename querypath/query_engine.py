import re
from typing import Any, List, Dict, Optional


class QueryEngine:
    """
    Executes simple SQL-like queries against a list of records (dicts).
    Supported syntax: SELECT col1, col2 FROM data [WHERE col op value] [LIMIT n]
    """

    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records

    def execute(self, query: str) -> List[Dict[str, Any]]:
        query = query.strip().rstrip(";")
        select_match = re.match(
            r"SELECT\s+(.+?)\s+FROM\s+\w+(\s+WHERE\s+(.+?))?(\s+LIMIT\s+(\d+))?$",
            query,
            re.IGNORECASE,
        )
        if not select_match:
            raise ValueError(f"Unsupported or malformed query: {query}")

        columns_str = select_match.group(1).strip()
        where_clause = select_match.group(3)
        limit_str = select_match.group(5)

        results = self.records

        if where_clause:
            results = self._apply_where(results, where_clause.strip())

        if columns_str != "*":
            cols = [c.strip() for c in columns_str.split(",")]
            results = [{col: row.get(col) for col in cols} for row in results]

        if limit_str:
            results = results[: int(limit_str)]

        return results

    def _apply_where(self, records: List[Dict], clause: str) -> List[Dict]:
        pattern = re.match(r"(\w+)\s*(=|!=|>=|<=|>|<)\s*(.+)", clause)
        if not pattern:
            raise ValueError(f"Invalid WHERE clause: {clause}")

        col, op, raw_val = pattern.group(1), pattern.group(2), pattern.group(3).strip()

        # Strip quotes for string values
        if (raw_val.startswith("'") and raw_val.endswith("'")) or (
            raw_val.startswith('"') and raw_val.endswith('"')
        ):
            value: Any = raw_val[1:-1]
        else:
            try:
                value = int(raw_val)
            except ValueError:
                try:
                    value = float(raw_val)
                except ValueError:
                    value = raw_val

        ops = {
            "=": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a is not None and a > b,
            ">=": lambda a, b: a is not None and a >= b,
            "<": lambda a, b: a is not None and a < b,
            "<=": lambda a, b: a is not None and a <= b,
        }
        fn = ops[op]
        return [row for row in records if fn(row.get(col), value)]
