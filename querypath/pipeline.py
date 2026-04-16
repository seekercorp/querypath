"""Pipeline: orchestrates cast and transform steps before query execution."""

from querypath.caster import apply_cast, parse_cast_expression
from querypath.transformer import apply_rename, apply_computed_column, parse_alias


def run_pipeline(rows: list[dict], steps: list[dict]) -> list[dict]:
    """
    Apply a list of pipeline steps to rows.

    Supported step types:
      - {"type": "cast",    "column": "age",   "as": "int"}
      - {"type": "rename",  "column": "old",   "as": "new"}
      - {"type": "compute", "expr": "a * b",   "as": "alias"}
    """
    for step in steps:
        stype = step.get("type", "").lower()
        if stype == "cast":
            rows = apply_cast(rows, step["column"], step["as"])
        elif stype == "rename":
            rows = apply_rename(rows, step["column"], step["as"])
        elif stype == "compute":
            rows = apply_computed_column(rows, step["expr"], step["as"])
        else:
            raise ValueError(f"Unknown pipeline step type: {stype!r}")
    return rows


def steps_from_select(select_exprs: list[str]) -> tuple[list[dict], list[str]]:
    """
    Parse SELECT expressions for inline casts (col::type) and aliases (expr AS name).
    Returns (pipeline_steps, clean_column_names).
    """
    steps = []
    clean = []
    for expr in select_exprs:
        base, alias = parse_alias(expr)
        cast_info = parse_cast_expression(base)
        if cast_info:
            col, type_name = cast_info
            out_name = alias or col
            steps.append({"type": "cast", "column": col, "as": type_name})
            clean.append(out_name if alias else col)
        elif alias:
            steps.append({"type": "compute", "expr": base, "as": alias})
            clean.append(alias)
        else:
            clean.append(base)
    return steps, clean
