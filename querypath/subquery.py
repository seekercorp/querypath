"""Subquery / nested query support for querypath."""
from typing import Any


def resolve_value(value: Any, context: dict) -> Any:
    """Resolve a value that may be a subquery dict or a plain value."""
    if isinstance(value, dict) and "__subquery__" in value:
        return execute_subquery(value["__subquery__"], context)
    return value


def execute_subquery(subquery: dict, context: dict) -> Any:
    """Execute a subquery and return its scalar or list result.

    A subquery dict has:
      - data: list of records
      - select: field name to extract (single field)
      - where: optional filter clauses (same format as QueryEngine)
      - scalar: if True, return a single value instead of a list
    """
    from querypath.query_engine import QueryEngine

    data = subquery.get("data", [])
    engine = QueryEngine(data)

    result = engine.execute(
        select=subquery.get("select", ["*"]),
        where=subquery.get("where"),
        order_by=subquery.get("order_by"),
        limit=subquery.get("limit"),
    )

    field = subquery.get("scalar_field")
    if subquery.get("scalar", False) and field:
        return result[0][field] if result else None

    if field:
        return [row[field] for row in result if field in row]

    return result


def apply_subquery_where(records: list, where: dict, context: dict) -> list:
    """Filter records where a field's value is IN a subquery result list."""
    field = where.get("field")
    subquery = where.get("in_subquery")
    if not field or not subquery:
        return records

    allowed = set(execute_subquery(subquery, context))
    return [r for r in records if r.get(field) in allowed]
