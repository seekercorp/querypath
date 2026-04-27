"""Row-level validation: flag or drop rows that fail field constraints."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Low-level predicates
# ---------------------------------------------------------------------------

def _check_rule(row: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    """Return True when *row* satisfies *rule*, False otherwise."""
    field = rule.get("field")
    op = rule.get("op", "not_null")
    value = rule.get("value")

    cell = row.get(field)

    if op == "not_null":
        return cell is not None
    if op == "is_null":
        return cell is None
    if op == "eq":
        return cell == value
    if op == "neq":
        return cell != value
    if op == "gt":
        try:
            return float(cell) > float(value)
        except (TypeError, ValueError):
            return False
    if op == "gte":
        try:
            return float(cell) >= float(value)
        except (TypeError, ValueError):
            return False
    if op == "lt":
        try:
            return float(cell) < float(value)
        except (TypeError, ValueError):
            return False
    if op == "lte":
        try:
            return float(cell) <= float(value)
        except (TypeError, ValueError):
            return False
    if op == "in":
        return cell in (value or [])
    if op == "not_in":
        return cell not in (value or [])
    # unknown op — treat as passing
    return True


def validate_row(row: Dict[str, Any], rules: List[Dict[str, Any]]) -> List[str]:
    """Return a list of violated rule descriptions for *row* (empty = valid)."""
    violations: List[str] = []
    for rule in rules:
        if not _check_rule(row, rule):
            label = rule.get("label") or f"{rule.get('field')} {rule.get('op', 'not_null')}"
            violations.append(label)
    return violations


# ---------------------------------------------------------------------------
# Bulk helpers
# ---------------------------------------------------------------------------

def apply_validation(
    rows: List[Dict[str, Any]],
    rules: List[Dict[str, Any]],
    *,
    mode: str = "flag",
    error_column: str = "_errors",
) -> List[Dict[str, Any]]:
    """Validate every row against *rules*.

    mode='flag'  – keep all rows; add *error_column* with list of violations
                   (empty list means valid).
    mode='drop'  – silently drop rows that have any violation.
    mode='raise' – raise ValueError on the first invalid row.
    """
    out: List[Dict[str, Any]] = []
    for row in rows:
        violations = validate_row(row, rules)
        if mode == "drop":
            if not violations:
                out.append(row)
        elif mode == "raise":
            if violations:
                raise ValueError(f"Row failed validation: {violations}  row={row}")
            out.append(row)
        else:  # flag
            out.append({**row, error_column: violations})
    return out


def parse_validation_spec(opts: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extract validation config from pipeline opts dict."""
    if not opts:
        return None
    spec = opts.get("validate")
    if not spec:
        return None
    if isinstance(spec, dict) and "rules" in spec:
        return spec
    return None
