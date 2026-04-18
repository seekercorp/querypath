"""Pipeline integration for set operations."""
from typing import List, Dict, Any, Optional
from querypath.set_ops import apply_union, apply_intersect, apply_except, parse_set_op_spec


def extract_set_op_spec(options: dict) -> Optional[dict]:
    """Pull set-op config from pipeline options if present."""
    raw = options.get("set_op")
    if not raw:
        return None
    return parse_set_op_spec(raw)


def run_pipeline_with_set_op(
    rows: List[Dict[str, Any]],
    options: dict,
) -> List[Dict[str, Any]]:
    """Apply a set operation to *rows* using spec from *options*.

    The spec lives under options["set_op"] and must include:
      - op:    'union' | 'intersect' | 'except'
      - right: list of row dicts (the second operand)
      - all:   bool (optional, default False — distinct)
    """
    spec = extract_set_op_spec(options)
    if spec is None:
        return rows

    op = spec["op"]
    right = spec["right"]
    distinct = not spec["all"]

    if op == "union":
        return apply_union(rows, right, distinct=distinct)
    if op == "intersect":
        return apply_intersect(rows, right)
    if op == "except":
        return apply_except(rows, right)

    raise ValueError(f"Unhandled set operation: '{op}'")
