from typing import Any


def apply_aggregation(groups: dict[tuple, list[dict]], agg_fields: list[dict]) -> list[dict]:
    """
    Collapse each group into a single summary row.
    agg_fields: list of {"func": "COUNT", "field": "*", "alias": "count"}
    """
    result = []
    for key, rows in groups.items():
        row: dict[str, Any] = {}
        for agg in agg_fields:
            func = agg.get("func", "").upper()
            field = agg.get("field", "*")
            alias = agg.get("alias") or f"{func}({field})"
            row[alias] = _compute(rows, f"{func}({field})")
        result.append(row)
    return result


def _compute(rows: list[dict], expr: str) -> Any:
    """Evaluate a single aggregation expression like COUNT(*) or SUM(salary)."""
    expr = expr.strip()
    upper = expr.upper()

    if upper.startswith("COUNT("):
        field = expr[6:-1].strip()
        if field == "*":
            return len(rows)
        return sum(1 for r in rows if r.get(field) is not None)

    if upper.startswith("SUM("):
        field = expr[4:-1].strip()
        return sum(r.get(field, 0) or 0 for r in rows)

    if upper.startswith("AVG("):
        field = expr[4:-1].strip()
        vals = [r.get(field) for r in rows if r.get(field) is not None]
        return sum(vals) / len(vals) if vals else None

    if upper.startswith("MIN("):
        field = expr[4:-1].strip()
        vals = [r.get(field) for r in rows if r.get(field) is not None]
        return min(vals) if vals else None

    if upper.startswith("MAX("):
        field = expr[4:-1].strip()
        vals = [r.get(field) for r in rows if r.get(field) is not None]
        return max(vals) if vals else None

    return None
