"""Simple in-memory join support for querypath."""
from typing import List, Dict, Any, Optional


def apply_join(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    left_key: str,
    right_key: str,
    join_type: str = "inner",
    right_prefix: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Join two record lists on specified keys.

    join_type: 'inner' | 'left'
    """
    join_type = join_type.lower()
    if join_type not in ("inner", "left"):
        raise ValueError(f"Unsupported join type: {join_type}")

    prefix = right_prefix + "." if right_prefix else ""

    # Build lookup from right side
    right_index: Dict[Any, List[Dict[str, Any]]] = {}
    for row in right:
        key_val = row.get(right_key)
        right_index.setdefault(key_val, []).append(row)

    result: List[Dict[str, Any]] = []
    for left_row in left:
        key_val = left_row.get(left_key)
        matches = right_index.get(key_val, [])
        if matches:
            for right_row in matches:
                merged = dict(left_row)
                for k, v in right_row.items():
                    merged[f"{prefix}{k}"] = v
                result.append(merged)
        elif join_type == "left":
            result.append(dict(left_row))

    return result
