"""Set operations: UNION, INTERSECT, EXCEPT for query results."""
from typing import List, Dict, Any


def _row_tuple(row: Dict[str, Any]):
    return tuple(sorted(row.items()))


def apply_union(left: List[Dict], right: List[Dict], distinct: bool = True) -> List[Dict]:
    """UNION (default distinct) or UNION ALL."""
    combined = left + right
    if not distinct:
        return combined
    seen = set()
    result = []
    for row in combined:
        key = _row_tuple(row)
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def apply_intersect(left: List[Dict], right: List[Dict]) -> List[Dict]:
    """Return rows present in both left and right (distinct)."""
    right_keys = {_row_tuple(r) for r in right}
    seen = set()
    result = []
    for row in left:
        key = _row_tuple(row)
        if key in right_keys and key not in seen:
            seen.add(key)
            result.append(row)
    return result


def apply_except(left: List[Dict], right: List[Dict]) -> List[Dict]:
    """Return rows in left not present in right (distinct)."""
    right_keys = {_row_tuple(r) for r in right}
    seen = set()
    result = []
    for row in left:
        key = _row_tuple(row)
        if key not in right_keys and key not in seen:
            seen.add(key)
            result.append(row)
    return result


def parse_set_op_spec(spec: dict) -> dict:
    """Validate and normalise a set-op spec dict.

    Expected keys: op ('union'|'intersect'|'except'), right (list of dicts),
    all (bool, default False).
    """
    op = spec.get("op", "").lower()
    if op not in ("union", "intersect", "except"):
        raise ValueError(f"Unknown set operation: '{op}'")
    return {
        "op": op,
        "right": spec.get("right", []),
        "all": bool(spec.get("all", False)),
    }
