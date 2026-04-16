"""Window functions: ROW_NUMBER, RANK, LAG, LEAD over ordered partitions."""
from typing import List, Dict, Any, Optional


def _partition_rows(rows: List[Dict], partition_by: List[str]) -> Dict[tuple, List[int]]:
    groups: Dict[tuple, List[int]] = {}
    for i, row in enumerate(rows):
        key = tuple(row.get(col) for col in partition_by)
        groups.setdefault(key, []).append(i)
    return groups


def apply_row_number(rows: List[Dict], col_name: str, partition_by: List[str], order_by: Optional[str] = None) -> List[Dict]:
    result = [dict(r) for r in rows]
    groups = _partition_rows(result, partition_by)
    for indices in groups.values():
        if order_by:
            indices.sort(key=lambda i: (result[i].get(order_by) is None, result[i].get(order_by)))
        for rank, i in enumerate(indices, 1):
            result[i][col_name] = rank
    return result


def apply_rank(rows: List[Dict], col_name: str, partition_by: List[str], order_by: str) -> List[Dict]:
    result = [dict(r) for r in rows]
    groups = _partition_rows(result, partition_by)
    for indices in groups.values():
        indices.sort(key=lambda i: (result[i].get(order_by) is None, result[i].get(order_by)))
        rank = 1
        for pos, i in enumerate(indices):
            if pos > 0:
                prev_val = result[indices[pos - 1]].get(order_by)
                curr_val = result[i].get(order_by)
                if curr_val != prev_val:
                    rank = pos + 1
            result[i][col_name] = rank
    return result


def apply_lag(rows: List[Dict], col_name: str, source_col: str, partition_by: List[str], order_by: Optional[str] = None, offset: int = 1) -> List[Dict]:
    result = [dict(r) for r in rows]
    groups = _partition_rows(result, partition_by)
    for indices in groups.values():
        if order_by:
            indices.sort(key=lambda i: (result[i].get(order_by) is None, result[i].get(order_by)))
        for pos, i in enumerate(indices):
            prev_pos = pos - offset
            result[i][col_name] = result[indices[prev_pos]].get(source_col) if prev_pos >= 0 else None
    return result


def apply_lead(rows: List[Dict], col_name: str, source_col: str, partition_by: List[str], order_by: Optional[str] = None, offset: int = 1) -> List[Dict]:
    result = [dict(r) for r in rows]
    groups = _partition_rows(result, partition_by)
    for indices in groups.values():
        if order_by:
            indices.sort(key=lambda i: (result[i].get(order_by) is None, result[i].get(order_by)))
        for pos, i in enumerate(indices):
            next_pos = pos + offset
            result[i][col_name] = result[indices[next_pos]].get(source_col) if next_pos < len(indices) else None
    return result
