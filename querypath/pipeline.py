"""Pipeline: orchestrates query steps in order."""
from typing import List, Dict, Any, Optional
from querypath.sorter import apply_order_by, apply_limit
from querypath.grouper import apply_group_by, apply_having, flatten_groups
from querypath.aggregator import apply_aggregation
from querypath.transformer import apply_rename, apply_computed_column
from querypath.caster import apply_cast
from querypath.expander import expand_rows
from querypath.window import apply_row_number, apply_rank, apply_lag, apply_lead


def steps_from_select(select_spec: List[str]) -> List[Dict]:
    steps = []
    for item in select_spec:
        if item.startswith("EXPAND:"):
            steps.append({"op": "expand", "column": item[7:]})
        elif item.startswith("CAST:"):
            steps.append({"op": "cast", "expr": item[5:]})
        elif " AS " in item.upper():
            steps.append({"op": "rename", "expr": item})
        elif item.startswith("COMPUTE:"):
            steps.append({"op": "compute", "expr": item[8:]})
    return steps


def run_pipeline(rows: List[Dict], plan: Dict) -> List[Dict]:
    # Expand
    if plan.get("expand"):
        rows = expand_rows(rows, plan["expand"])

    # Computed columns
    for expr in plan.get("computed", []):
        rows = apply_computed_column(rows, expr)

    # Cast
    for expr in plan.get("cast", []):
        rows = apply_cast(rows, expr)

    # Window functions (before group/agg)
    for wspec in plan.get("window", []):
        fn = wspec["fn"]
        col = wspec["col"]
        partition = wspec.get("partition", [])
        order = wspec.get("order")
        source = wspec.get("source", col)
        offset = wspec.get("offset", 1)
        if fn == "row_number":
            rows = apply_row_number(rows, col, partition, order)
        elif fn == "rank":
            rows = apply_rank(rows, col, partition, order)
        elif fn == "lag":
            rows = apply_lag(rows, col, source, partition, order, offset)
        elif fn == "lead":
            rows = apply_lead(rows, col, source, partition, order, offset)

    # Group / aggregate
    if plan.get("group_by"):
        groups = apply_group_by(rows, plan["group_by"])
        if plan.get("having"):
            groups = apply_having(groups, plan["having"])
        rows = flatten_groups(groups)
        if plan.get("aggregations"):
            rows = apply_aggregation(rows, plan["aggregations"])
    elif plan.get("aggregations"):
        rows = apply_aggregation(rows, plan["aggregations"])

    # Rename
    for expr in plan.get("rename", []):
        rows = apply_rename(rows, expr)

    # Sort
    if plan.get("order_by"):
        rows = apply_order_by(rows, plan["order_by"], plan.get("order_dir", "ASC"))

    # Limit
    if plan.get("limit") is not None:
        rows = apply_limit(rows, plan["limit"])

    return rows
